#Get events outside the city!!!
import numpy as np
from outside_helpers import *
from helpers import *
from distance import *


'''
Outside trip table: user_id, outside_trip_id, route_ids, origin_city, state, direction, n_days, default, full_day, details 
outside route table: route_id, event_id_lst, event_type, origin_city, state, direction, details, default, 
'''
target_direction = 'N'
origin_city = 'San Francisco'
origin_state = 'California'
conn_str = "dbname='travel_with_friends' user='zoesh' host='localhost'"

def outside_trip_poi_one_day(origin_city, origin_state, target_direction = 'N', n_days = 1, full_day = True, default = True, debug = True, user_id = 'admin'):
    outside_trip_id = '-'.join([str(state.upper()), str(origin_city.upper().replace(' ','-')), target_direction,str(int(default)), str(n_days)])
    if check_outside_trip_id(outside_trip_id, debug):
        if n_days == 1:
            furthest_len = 140
        #possible city coords, target city coord_lat, target city coord_long
        coords, coord_lat, coord_long = travel_outside_coords(origin_city, origin_state)
        #coords: city, lat, long
        check_cities_info = []
        for item in coords:
            direction = direction_from_orgin(coord_long,  coord_lat, item[2], item[1])
            if (target_direction == direction) and (geopy_dist((item[1], item[2]), (coord_lat, coord_long)) < furthest_len):
                check_cities_info.append(item)
        city_infos = []
        for city, _, _ in check_cities_info:
            county = None
            #index, coord0, coord1, adjusted_normal_time_spent, poi_rank, rating
            city_info = db_start_location(county, origin_state, city)
            city_infos.extend(city_info)
        city_infos = np.array(city_infos)
        poi_coords = city_infos[:,1:3]
        n_routes = sum(1 for t in np.array(city_infos)[:,3] if t >= 120)    
        if (n_routes>1) and (city_infos.shape[0]>=10):
            kmeans = KMeans(n_clusters=n_routes).fit(poi_coords)
        elif (city_infos.shape[0]> 20) or (n_routes>1):
            kmeans = KMeans(n_clusters=2).fit(poi_coords)
        else:
            kmeans = KMeans(n_clusters=1).fit(poi_coords)
        route_labels = kmeans.labels_

        # print n_routes, len(route_labels), city_infos.shape
        # print route_labels
        outside_route_ids, outside_trip_details =[],[]
        for i in range(n_routes):
            current_events, big_ix, med_ix, small_ix = [], [],[], []
            for ix, label in enumerate(route_labels):
                if label == i:
                    time = city_infos[ix,3]
                    event_ix = city_infos[ix,0]
                    current_events.append(event_ix)
                    if time > 180 :
                        big_ix.append(ix)
                    elif time >= 120 :
                        med_ix.append(ix)
                    else:
                        small_ix.append(ix)
            big_ = sorted_events(city_infos, big_ix)
            med_ = sorted_events(city_infos, med_ix)
            small_ = sorted_events(city_infos, small_ix)
            print big_, len(big_), len(med_), len(small_)
            # need to update!!!!!!!!
            event_ids, event_type = create_event_id_list(big_, med_, small_)
            event_ids, event_type = db_event_cloest_distance(event_ids = event_ids, event_type = event_type)
            event_ids, google_ids, name_list, driving_time_list, walking_time_list =db_google_driving_walking_time(event_ids, event_type)
            event_ids, driving_time_list, walking_time_list, total_time_spent = db_remove_extra_events(event_ids, driving_time_list, walking_time_list)
            db_address(event_ids)
            outside_route_id = '-'.join(event_ids) 
            values = db_outside_route_trip(outside_route_id, event_ids, origin_city, origin_state, default, full_day,n_days,i)
            conn = psycopg2.connect(conn_str)
            cur = conn.cursor()

            cur.execute("insert into outside_route_table (outside_route_id, full_day, default, origin_city, origin_state, target_direction, details, event_type, event_ids) \
                        VALUES ( '%s', %s, %s, '%s', '%s', '%s', '%s', '%s')" \
                        %( outside_route_id, full_day, default, origin_city, origin_state, target_direction, details, event_type, event_ids))
            conn.commit()
            conn.close()
            outside_route_ids.append(outside_route_id)
            outside_trip_details.extend(details)

        user_id = "admin"
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute("insert into outside_trip_table(user_id, outside_trip_id, outside_route_ids, origin_city, origin_state, target_direction, n_days, default, full_day, details) \
                     VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', %s)" \
                     %(user_id, outside_trip_id, str(outside_route_ids), origin_city, origin_state, target_direction, n_days, default, full_day, outside_trip_details))
        conn.commit()
        conn.close()
        return "finish update %s, %s, direction %s into database" %(target_state, target_city, target_direction)
    else:
        return "ALERT: %s, %s, direction %s already in database" %(target_state, target_city, target_direction)