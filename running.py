import psycopg2
import city_trip as trip


conn_str = "dbname='travel_with_friends' user='Gon' host='localhost'"

conn = psycopg2.connect(conn_str)
cur = conn.cursor()
cur.execute("select state, city from county_table;")
c = cur.fetchall()
print len(c)

cur.execute("select max(index) from full_trip_table;")
full_trip_index = cur.fetchone()[0]
print full_trip_index
cur.execute("select county, state from full_trip_table where index='%s';"%(full_trip_index-10)) 
location = cur.fetchone()       
print location
cur.execute("select state, city from county_table where county ='%s' and state='%s';"%(location[0],location[1]))
last_stop_location = cur.fetchall()[0]
print last_stop_location
last_stop =  c.index(last_stop_location)
conn.close()

Not_data_for_county=[]
for x in range(last_stop,len(c)):
    state, city = c[x]
    if (state == 'Puerto Rico') or (state == 'Virgin Islands'):
        continue
    print c[x]
    n_days = [1,2,3,4,5]
    for day in n_days:
        error = trip.get_fulltrip_data(state, city, int(day))
        Not_data_for_county.append(error)

with open("missing_county_info.txt", 'w') as f:
	for error in Not_data_for_county:
		f.write("%s\n"%error)