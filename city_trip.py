from helpers import *
import ast
def get_fulltrip_data(state, city, n_days, full_day = True, regular = True, debug = True):
    '''
    Get the default full trip data for each city(county)
    '''
    county = find_county(state, city)
    n_days = int(n_days)
    if county:
        full_trip_id = '-'.join([str(state.upper()), str(county.upper().replace(' ','-')),str(int(regular)), str(n_days)])
    else:
        full_trip_id = '-'.join([str(state.upper()), str(city.upper().replace(' ','-')),str(int(regular)), str(n_days)])
    if not check_full_trip_id(full_trip_id, debug):
        trip_location_ids, full_trip_details =[],[]
        county_list_info = db_start_location(county, state, city)
        time_spent = county_list_info[:,3]
        poi_coords = county_list_info[:,1:3]
        kmeans = KMeans(n_clusters=n_days).fit(poi_coords)
        day_labels = kmeans.labels_
        day_order = kmeans_leabels_day_order(day_labels)
        not_visited_poi_lst = []
        for i,v in enumerate(day_order):
            day_trip_id = '-'.join([str(state), str(county.upper().replace(' ','-')),str(int(regular)), str(n_days),str(i)])
            current_events, big_ix, small_ix, med_ix = [],[],[],[]
            for ix, label in enumerate(day_labels):
                if label == v:
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
            event_ids, event_type = db_event_cloest_distance(event_ids = event_ids, event_type = event_type, city_name = city)
            # event_ids, google_ids, name_list, driving_time_list, walking_time_list = \
            event_ids, driving_time_list, walking_time_list = \
                    db_google_driving_walking_time(event_ids, event_type)
            # print 'event_ids, google_ids, name_list', event_ids, google_ids, name_list
            # print 'driving and walking time list: ', driving_time_list, walking_time_list
            # event_ids, driving_time_list, walking_time_list, total_time_spent = db_remove_extra_events(event_ids, driving_time_list, walking_time_list)
            event_ids, driving_time_list, walking_time_list, total_time_spent, not_visited_poi_lst = \
                db_adjust_events(event_ids, driving_time_list, walking_time_list, not_visited_poi_lst, event_type, city)
            # db_address(event_ids)
            details = db_day_trip_details(event_ids, i)
            #insert to day_trip ....
            conn = psycopg2.connect(conn_str)
            cur = conn.cursor()
            cur.execute('select max(index) from day_trip_table;')
            max_index = cur.fetchone()[0]
            index = max_index+1
            cur.execute("insert into day_trip_table (index, trip_locations_id, full_day, regular, county, state, details, event_type, event_ids) VALUES ( %s, '%s', %s, %s, '%s', '%s', '%s', '%s', '%s');" %( index, day_trip_id, full_day, regular, county, state, str(details).replace("'", "''"), event_type, event_ids))
            conn.commit()
            conn.close()
            trip_location_ids.append(day_trip_id)
            full_trip_details.extend(details)

        # full_trip_id = '-'.join([str(state.upper()), str(county.upper().replace(' ','-')),str(int(regular)), str(n_days)])
        username = "zoesh"
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute("select max(index) from full_trip_table;")
        full_trip_index = cur.fetchone()[0] + 1
        cur.execute("insert into full_trip_table(index, username, full_trip_id,trip_location_ids, regular, county, state, details, n_days) VALUES (%s, '%s', '%s', '%s', %s, '%s', '%s', '%s', %s);" %(full_trip_index, username, full_trip_id, str(trip_location_ids).replace("'","''"), regular, county, state, str(full_trip_details).replace("'","''"), n_days))
        conn.commit()
        conn.close()
        print "finish update %s, %s into database" %(state, county)
        return full_trip_id, full_trip_details
    else:
        print "%s, %s already in database" %(state, county) 
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute("select details from full_trip_table where full_trip_id = '%s';" %(full_trip_id)) 
        details = cur.fetchone()[0]        
        conn.close()
        full_trip_details = ast.literal_eval(details)
        return full_trip_id, full_trip_details