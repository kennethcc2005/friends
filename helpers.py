import psycopg2
import simplejson
import numpy as np
from distance import *

conn_str = "dbname='travel_with_friends' user='zoesh' host='localhost'"
my_key = 'AIzaSyDJh9EWCA_v0_B3SvjzjUA3OSVYufPJeGE'

def find_county(state, city):
    '''
    Only valid within the U.S.
    '''
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("select county from county_table where city = '%s' and state = '%s';" %(city.title(), state.title()))

    county = cur.fetchone()
    conn.close()
    if county:
        return county[0]
    else:
        return None

def db_start_location(county, state, city):
    '''
    Get numpy array of county related POIs.
    '''
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    if county:
        cur.execute("select index, coord0, coord1, adjusted_normal_time_spent, poi_rank, rating from poi_detail_table where county = '%s' and state = '%s'; "%(county.upper(), state.title()))
    else:
        cur.execute("select index, coord0, coord1, adjusted_normal_time_spent, poi_rank, rating from poi_detail_table where city = '%s' and state = '%s'; "%(city.title(), state.title()))
    a = cur.fetchall()
    conn.close()
    return np.array(a)

def get_event_ids_list(trip_locations_id):
    '''
    Input: trip_locations_id
    Output: evnet_ids, event_type = ['big', 'small', 'med', 'add',]
    '''
    conn = psycopg2.connect(conn_str)  
    cur = conn.cursor()  
    cur.execute("select event_ids,event_type from day_trip_table where trip_locations_id = '%s' " %(trip_locations_id))
    event_ids,event_type = cur.fetchone()
    event_ids = ast.literal_eval(event_ids)
    conn.close()
    return event_ids,event_type


def db_event_cloest_distance(trip_locations_id=None,event_ids=None, event_type = 'add',new_event_id = None):
    '''
    Get matrix cloest distance
    '''
    if new_event_id or not event_ids:
        event_ids, event_type = get_event_ids_list(trip_locations_id)
        if new_event_id:
            event_ids.append(new_event_id)
            
    conn = psycopg2.connect(conn_str)  
    cur = conn.cursor()
    points = np.zeros((len(event_ids), 3))
    for i,v in enumerate(event_ids):
        cur.execute("select index, coord0, coord1 from poi_detail_table where index = %i;"%(float(v)))
        points[i] = cur.fetchone()
    conn.close()
    n,D = mk_matrix(points[:,1:], geopy_dist)
    if len(points) >= 3:
        if event_type == 'add':
            tour = nearest_neighbor(n, 0, D)
            # create a greedy tour, visiting city 'i' first
            z = length(tour, D)
            z = localsearch(tour, z, D)
            return np.array(event_ids)[tour], event_type
        #need to figure out other cases
        else:
            tour = nearest_neighbor(n, 0, D)
            # create a greedy tour, visiting city 'i' first
            z = length(tour, D)
            z = localsearch(tour, z, D)
            return np.array(event_ids)[tour], event_type
    else:
        return np.array(event_ids), event_type

def check_full_trip_id(full_trip_id, debug):
    '''
    Check full trip id exist or not.  
    '''
    conn = psycopg2.connect(conn_str)  
    cur = conn.cursor()  
    cur.execute("select details from full_trip_table where full_trip_id = '%s'" %(full_trip_id)) 
    a = cur.fetchone()
    conn.close()
    if bool(a):
        if not debug: 
            return a[0]
        else:
            return True
    else:
        return False

def check_day_trip_id(day_trip_id, debug):
    '''
    Check day trip id exist or not.  
    '''
    conn = psycopg2.connect(conn_str)  
    cur = conn.cursor()  
    cur.execute("select details from day_trip_table where trip_locations_id = '%s'" %(day_trip_id)) 
    a = cur.fetchone()
    conn.close()
    if bool(a):
        if not debug: 
            return a[0]
        else:
            return True
    else:
        return False

def check_travel_time_id(new_id):
    '''
    Check google driving time exisit or not for the 2 point poi id.
    '''
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("select google_driving_time from google_travel_time_table where id_ = '%s'" %(new_id))
    a = cur.fetchone()
    conn.close()
    if bool(a):
        return True
    else:
        return False

#May need to improve by adding #reviews in this. :)
def sorted_events(info,ix):
    '''
    find the event_id, ranking and rating columns
    sorted base on ranking then rating
    
    return sorted list 
    '''
    event_ = info[ix][:,[0,4,5]]
    return np.array(sorted(event_, key=lambda x: (x[1], -x[2])))

#Need to make this more efficient
def create_event_id_list(big_,medium_,small_):
    event_type = ''
    if big_.shape[0] >= 1:
        if (medium_.shape[0] < 2) or (big_[0,1] <= medium_[0,1]):
            if small_.shape[0] >= 6:
                event_ids = list(np.concatenate((big_[0,0], small_[0:6,0]),axis=0))  
            else:
                event_ids = list(np.concatenate((big_[0,0], small_[:,0]),axis=0)) 
            event_type = 'big'
        else:
            if small_.shape[0] >= 8:
                event_ids = list(np.concatenate((medium_[0:2,0], small_[0:8,0]),axis=0))
            else:
                event_ids = list(np.concatenate((medium_[0:2,0], small_[:,0]),axis=0))
            event_type = 'med'
    elif medium_.shape[0] >= 2:
        if small_.shape[0] >= 8:
            event_ids = list(np.concatenate((medium_[0:2,0], small_[0:8,0]),axis=0))
        else:
            event_ids = list(np.concatenate((medium_[0:2,0], small_[:,0]),axis=0))
        event_type = 'med'
    else:
        if small_.shape[0] >= 10:
            if not medium_.shape[0]:
                event_ids = list(np.array(sorted(small_[0:10,:], key=lambda x: (x[1],-x[2])))[:,0])
            else:
                event_ids = list(np.array(sorted(np.vstack((medium_, small_[0:10,:])), key=lambda x: (x[1],-x[2])))[:,0])
        else:
            if not medium_.shape[0]:
                event_ids = list(np.array(sorted(small_[0:10,:], key=lambda x: (x[1],-x[2])))[:,0])
            else:
                event_ids = list(np.array(sorted(np.vstack((medium_,small_)), key=lambda x: (x[1],-x[2])))[:,0])
        event_type = 'small'
    return event_ids, event_type

def db_google_driving_walking_time(event_ids, event_type):
    '''
    Get estimated travel time from google api.  
    Limit 1000 calls per day.
    '''
    conn = psycopg2.connect(conn_str)  
    cur = conn.cursor()  
    google_ids = []
    driving_time_list = []
    walking_time_list = []
    name_list = []
    for i,v in enumerate(event_ids[:-1]):
        id_ = str(v) + '0000'+str(event_ids[i+1])
        result_check_travel_time_id = check_travel_time_id(id_)
        if not result_check_travel_time_id:
            cur.execute("select name, coord0, coord1 from poi_detail_table where index = %s"%(v))
            orig_name, orig_coord0, orig_coord1 = cur.fetchone()
            orig_idx = v
            cur.execute("select name, coord0, coord1 from poi_detail_table where index = %s "%(event_ids[i+1]))
            dest_name, dest_coord0, dest_coord1 = cur.fetchone()
            dest_idx = event_ids[i+1]
            orig_coords = str(orig_coord1)+','+str(orig_coord0)
            dest_coords = str(dest_coord1)+','+str(dest_coord0)
            google_driving_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false&key={2}".\
                                    format(orig_coords.replace(' ',''),dest_coords.replace(' ',''),my_key)
            google_walking_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=walking&language=en-EN&sensor=false&key={2}".\
                                    format(orig_coords.replace(' ',''),dest_coords.replace(' ',''),my_key)
            driving_result= simplejson.load(urllib.urlopen(google_driving_url))
            walking_result= simplejson.load(urllib.urlopen(google_walking_url))
            if driving_result['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                google_driving_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false&key={2}".\
                                    format(orig_name.replace(' ','+').replace('-','+'),dest_name.replace(' ','+').replace('-','+'),my_key)
                driving_result= simplejson.load(urllib.urlopen(google_driving_url))
                
            if walking_result['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                google_walking_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=walking&language=en-EN&sensor=false&key={2}".\
                                        format(orig_name.replace(' ','+').replace('-','+'),dest_name.replace(' ','+').replace('-','+'),my_key)
                walking_result= simplejson.load(urllib.urlopen(google_walking_url))
            if (driving_result['rows'][0]['elements'][0]['status'] == 'NOT_FOUND') and (walking_result['rows'][0]['elements'][0]['status'] == 'NOT_FOUND'):
                new_event_ids = list(event_ids)
                new_event_ids.pop(i+1)
                new_event_ids = db_event_cloest_distance(event_ids=new_event_ids, event_type = event_type)
                return db_google_driving_walking_time(new_event_ids, event_type)
            try:
                google_driving_time = driving_result['rows'][0]['elements'][0]['duration']['value']/60
            except:            
                print v, id_, driving_result #need to debug for this
            try:
                google_walking_time = walking_result['rows'][0]['elements'][0]['duration']['value']/60
            except:
                google_walking_time = 9999
        
            cur.execute("select max(index) from  google_travel_time_table")
            index = cur.fetchone()[0]+1
            driving_result = str(driving_result).replace("'",'"')
            walking_result = str(walking_result).replace("'",'"')
            orig_name = orig_name.replace("'","''")
            dest_name = dest_name.replace("'","''")
            cur.execute("INSERT INTO google_travel_time_table VALUES (%i, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', %s, %s);"%(index, id_, orig_name, orig_idx, dest_name, dest_idx, orig_coord0, orig_coord1, dest_coord0,\
                                   dest_coord1, orig_coords, dest_coords, google_driving_url, google_walking_url,\
                                   str(driving_result), str(walking_result), google_driving_time, google_walking_time))
            conn.commit()
            name_list.append(orig_name+" to "+ dest_name)
            google_ids.append(id_)
            driving_time_list.append(google_driving_time)
            walking_time_list.append(google_walking_time)
        else:
            
            cur.execute("select orig_name, dest_name, google_driving_time, google_walking_time from google_travel_time_table \
                         where id_ = '%s'" %(id_))
            orig_name, dest_name, google_driving_time, google_walking_time = cur.fetchone()
            name_list.append(orig_name+" to "+ dest_name)
            google_ids.append(id_)
            driving_time_list.append(google_driving_time)
            walking_time_list.append(google_walking_time)
    conn.close()
    return event_ids, google_ids, name_list, driving_time_list, walking_time_list

def db_remove_extra_events(event_ids, driving_time_list,walking_time_list, max_time_spent=480):
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()   
    cur.execute("SELECT DISTINCT SUM(adjusted_normal_time_spent) FROM poi_detail_table WHERE index IN %s;" %(tuple(event_ids),))
    time_spent = cur.fetchone()[0]
    conn.close()
    time_spent += sum(np.minimum(np.array(driving_time_list),np.array(walking_time_list)))
    if time_spent > max_time_spent:
        update_event_ids = event_ids[:-1]
        update_driving_time_list = driving_time_list[:-1]
        update_walking_time_list = walking_time_list[:-1]
        return db_remove_extra_events(update_event_ids, update_driving_time_list, update_walking_time_list)
    else:
        return event_ids, driving_time_list, walking_time_list, time_spent

def db_day_trip(event_ids, trip_locations_id, county, state, default, full_day,n_days,i):
    conn=psycopg2.connect(conn_str)
    cur = conn.cursor()
    details = []
    #details dict includes: id, name,address, day
    for event_id in event_ids:
        cur.execute("select index, name, address from poi_detail_table where index = %s;" %(event_id))
        a = cur.fetchone()
        details.append(str({'id': [0],'name': a[1],'address': a[2], 'day': i}))
    conn.close()
    return [trip_locations_id, full_day, default, county, state, details]

def check_address(index):
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("select address from poi_detail_table where index = %s;"%(index))
    a = cur.fetchone()[0]
    conn.close()
    if a:
        return True
    else:
        return False
        
def db_address(event_ids):
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    for i in event_ids[:-1]:
        if not check_address(i):
            cur.execute("select driving_result from google_travel_time_table where orig_idx = %s;" %(i))
            a= cur.fetchone()[0]
            add = ast.literal_eval(a)['origin_addresses'][0]
            cur.execute("update poi_detail_table set address = '%s' where index = %s;" %(add, i))
            conn.commit()
    last = event_ids[-1]
    if not check_address(last):
        cur.execute("select driving_result from google_travel_time_table where dest_idx = %s;" %(last))
        a= cur.fetchone()[0]
        add = ast.literal_eval(a)['destination_addresses'][0]
        cur.execute("update poi_detail_table set address = '%s' where index = %s;" %(add, last))
        conn.commit()
    conn.close()

        