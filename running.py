import psycopg2
import json
import city_trip as trip

with open('api_key_list.config') as key_file:
    api_key_list = json.load(key_file)
conn_str = api_key_list["conn_str"]

# conn_str = "dbname='travel_with_friends' user='Gon' host='localhost'"

conn = psycopg2.connect(conn_str)
cur = conn.cursor()
cur.execute("SELECT state, city FROM county_table;")
c = cur.fetchall()
print "total : ", len(c)

cur.execute("SELECT max(index) FROM full_trip_table;")
full_trip_index = cur.fetchone()[0]
print "data in full trip: ", full_trip_index
if full_trip_index == 0:
    cur = conn.cursor()
    cur.execute("SELECT state, city FROM county_table LIMIT 1;")
    location = cur.fetchall()[0]
    print "first location : ", location
else:
    cur.execute("SELECT county, state FROM full_trip_table WHERE index='%s';"%(full_trip_index)) 
    county_location = cur.fetchone()       
    print "last time stop at county and state : ", county_location
    cur.execute("SELECT state, city FROM county_table WHERE county ='%s' AND state='%s';"%(county_location[0], county_location[1]))
    location = cur.fetchall()[0]
    print "last time stop at state, city: ", location
last_stop = c.index(location)
print "num of city done from last stop: ", last_stop
conn.close()

Not_data_for_county=[]
for x in range(last_stop,len(c)):
# for x in range(len(c)):
    state, city = c[x]
    # ('California', 'Newbury Park'), ('Alaska', 'Chignik Lake') have problem 
    # if (state == 'Puerto Rico') or (state == 'Virgin Islands'):
    #     continue
    print c[x]
    n_days = [1,2,3,4,5]
    for day in n_days:
        error = trip.get_fulltrip_data(state, city, int(day))
        Not_data_for_county.append(error)
print "finish all city and state"
with open("missing_county_info.txt", 'w') as f:
	for error in Not_data_for_county:
		f.write("%s\n"%error)