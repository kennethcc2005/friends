
from helpers import *
def get_fulltrip_data_default(state, city, n_days, full_day = True, default = True, debug = True):
    '''
    Get the default full trip data for each city(county)
    '''
    county = find_county(state, city)
    full_trip_id = '-'.join([str(state.upper()), str(county.upper().replace(' ','-')),str(int(default)), str(n_days)])
    if not check_full_trip_id(full_trip_id, debug):
        trip_location_ids, full_trip_details =[],[]
        county_list_info = db_start_location(county, state, city)
        time_spent = county_list_info[:,3]
        n_days = min(n_days, np.sum(time_spent) / 360)
        poi_coords = county_list_info[:,1:3]
        kmeans = KMeans(n_clusters=n_days).fit(poi_coords)
        day_labels = kmeans.labels_
        for i in range(n_days):
            day_trip_id = '-'.join([str(state), str(county.upper().replace(' ','-')),str(int(default)), str(n_days),str(i)])
            if not check_day_trip_id(day_trip_id, debug):
                current_events, big_ix, small_ix, med_ix = [],[],[],[]
                for ix, label in enumerate(day_labels):
                    if label == i:
                        time = county_list_info[ix,3]
                        event_ix = county_list_info[ix,0]
                        current_events.append(event_ix)
                        if time > 180 :
                            big_ix.append(ix)
                        elif time >= 120 :
                            med_ix.append(ix)
                        else:
                            small_ix.append(ix)
                #need to double check this funct!
                big_ = sorted_events(county_list_info, big_ix)
                med_ = sorted_events(county_list_info, med_ix)
                small_ = sorted_events(county_list_info, small_ix)
                
                event_ids, event_type = create_event_id_list(big_, med_, small_)
                event_ids, event_type = db_event_cloest_distance(event_ids = event_ids, event_type = event_type)
                event_ids, google_ids, name_list, driving_time_list, walking_time_list =db_google_driving_walking_time(event_ids, event_type)
                event_ids, driving_time_list, walking_time_list, total_time_spent = db_remove_extra_events(event_ids, day_trip_id, driving_time_list, walking_time_list)
                db_address(event_ids)
                details = db_day_trip_details(event_ids, i)
                #insert to day_trip ....
                conn = psycopg2.connect(conn_str)
                cur = conn.cursor()
                cur.execute("insert into day_trip_table (trip_locations_id,full_day, default, county, state, details, event_type, event_ids) VALUES ( '%s', %s, %s, '%s', '%s', '%s', '%s', '%s')" %( day_trip_id, full_day, default, county, state, details, event_type, event_ids))
                conn.commit()
                conn.close()
                trip_location_ids.append(day_trip_id)
                full_trip_details.extend(details)

            else:
                print "error: already have this day, please check the next day"
                trip_location_ids.append(day_trip_id)
                #call db find day trip detail 
                conn = psycopg2.connect(conn_str)
                cur = conn.cursor()
                cur.execute("select details from day_trip_table where trip_locations_id = '%s';"%(day_trip_id) )
                day_trip_detail = fetchall()
                conn.close()
                full_trip_details.extend(day_trip_detail)

        full_trip_id = '-'.join([str(state.upper()), str(county.upper().replace(' ','-')),str(int(default)), str(n_days)])
        details = full_trip_details
        user_id = "admin"
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute("insert into full_trip_table(user_id, full_trip_id,trip_location_ids, default, county, state, details, n_days) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', %s)" %(user_id, full_trip_id, str(trip_location_ids), default, county, state, details, n_days))
        conn.commit()
        conn.close()
        return "finish update %s, %s into database" %(state, county)
    else:
        return "%s, %s already in database" %(state, county) 

if name == '__main__':
    days = [1,2,3,4,5]
    state = 'California'
    city = 'San Francisco'
    for n_days in days:
        get_fulltrip_data_default(state, city, n_days, full_day = True, default = True, debug = True)
    
