import outside_trip
import psycopg2
import json

with open('api_key_list.config') as key_file:
    api_key_list = json.load(key_file)
conn_str = api_key_list["conn_str"]



direct = ["E","S","W","N"]

conn = psycopg2.connect(conn_str)
cur = conn.cursor()
cur.execute("select state, city from county_table;")
city_list = cur.fetchall()
conn.close()



for i in city_list:
	origin_city = i[1]
	origin_state = i[0]
	print origin_city, origin_state
	for target_direction in direct:
	    outside_trip.outside_trip_poi(origin_city ,origin_state, target_direction)

	    
print "finish all city and state"




