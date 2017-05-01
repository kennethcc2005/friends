import psycopg2
import city_trip as trip


conn_str = "dbname='travel_with_friends' user='Gon' host='localhost'"

conn = psycopg2.connect(conn_str)
cur = conn.cursor()
cur.execute("select state, city from county_table;")
c = cur.fetchall()


for x in range(len(c)):
    state, city = c[x]
    if (state == 'Puerto Rico') or (state == 'Virgin Islands'):
        continue
    print c[x]
    n_days = [1,2,3,4,5]
    for day in n_days:
        trip.get_fulltrip_data(state, city, int(day))

