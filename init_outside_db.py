import pandas as pd
import psycopg2
from sqlalchemy import create_engine

conn_str = "dbname='travel_with_friends' user='zoesh' host='localhost'"
engine = create_engine('postgresql://zoesh@localhost:5432/travel_with_friends')
def init_outside_db_tables():
    outside_trip_id = '-'.join([str('test'.upper().replace(' ','-')), str('test'.upper().replace(' ','-')), \
                        'N'.upper(),str(int(True)), str(1)])
    outside_route_id = outside_trip_id + '-' + str(0)
    outside_route_table = pd.DataFrame(columns =['outside_route_id', 'full_day', 'regular', 'origin_city', \
                        'origin_state', 'target_direction', 'details', 'event_type', 'event_ids', 'route_num'])
    outside_trip_table = pd.DataFrame(columns = ['username', 'outside_trip_id', 'outside_route_ids', 'event_id_lst', 'origin_city', \
                        'origin_state', 'target_direction', 'n_routes', 'regular', 'full_day', 'details'])
    google_city_to_poi_table = pd.DataFrame(columns = ['city_to_poi_id', 'city_id', 'origin_city', 'origin_state', \
                        'orig_name','dest_name', 'dest_poi_id', 'start_coord_lat','start_coord_long','dest_coord_lat',\
                        'dest_coord_long','orig_coords','dest_coords', 'google_driving_url', 'google_walking_url',\
                         'driving_result', 'walking_result', 'city_to_poi_driving_time', 'city_to_poi_walking_time'])
    outside_route_table.loc[0] = [outside_route_id, True, True, 'Test', 'Test', 'N', ["{'address': '15500 San Pasqual Valley Rd, Escondido, CA 92027, USA', 'id': 2259, 'day': 0, 'name': u'San Diego Zoo Safari Park'}", "{'address': 'Safari Walk, Escondido, CA 92027, USA', 'id': 2260, 'day': 0, 'name': u'Meerkat'}", "{'address': '1999 Citracado Parkway, Escondido, CA 92029, USA', 'id': 3486, 'day': 0, 'name': u'Stone'}", "{'address': '1999 Citracado Parkway, Escondido, CA 92029, USA', 'id': 3487, 'day': 0, 'name': u'Stone Brewery'}", "{'address': 'Mount Woodson Trail, Poway, CA 92064, USA', 'id': 4951, 'day': 0, 'name': u'Lake Poway'}", "{'address': '17130 Mt Woodson Rd, Ramona, CA 92065, USA', 'id': 4953, 'day': 0, 'name': u'Potato Chip Rock'}", "{'address': '17130 Mt Woodson Rd, Ramona, CA 92065, USA', 'id': 4952, 'day': 0, 'name': u'Mt. Woodson'}"],
       'big','[2259, 2260,3486,3487,4951,4953,4952]', 0]
    outside_trip_table.loc[0] = ['zoesh', outside_trip_id, '[outside_route_id]', '[2259, 2260,3486,3487,4951,4953,4952]', \
                                'Test','Test','N',1,True, True, ["{'address': '15500 San Pasqual Valley Rd, Escondido, CA 92027, USA', 'id': 2259, 'day': 0, 'name': u'San Diego Zoo Safari Park'}", "{'address': 'Safari Walk, Escondido, CA 92027, USA', 'id': 2260, 'day': 0, 'name': u'Meerkat'}", "{'address': '1999 Citracado Parkway, Escondido, CA 92029, USA', 'id': 3486, 'day': 0, 'name': u'Stone'}", "{'address': '1999 Citracado Parkway, Escondido, CA 92029, USA', 'id': 3487, 'day': 0, 'name': u'Stone Brewery'}", "{'address': 'Mount Woodson Trail, Poway, CA 92064, USA', 'id': 4951, 'day': 0, 'name': u'Lake Poway'}", "{'address': '17130 Mt Woodson Rd, Ramona, CA 92065, USA', 'id': 4953, 'day': 0, 'name': u'Potato Chip Rock'}", "{'address': '17130 Mt Woodson Rd, Ramona, CA 92065, USA', 'id': 4952, 'day': 0, 'name': u'Mt. Woodson'}"]]
    google_city_to_poi_table.loc[0] = [999999, 999999, 'Test','Test','Test','Test', 2871.0, 33.047769600024424, -117.29692141333341, \
                                    33.124079753475236, -117.3177652511278, '33.0477696,-117.296921413', '33.1240797535,-117.317765251',\
                                    'https://maps.googleapis.com/maps/api/distancematrix/json?origins=33.0477696,-117.296921413&destinations=33.1240797535,-117.317765251&mode=driving&language=en-EN&sensor=false&key=AIzaSyDJh9EWCA_v0_B3SvjzjUA3OSVYufPJeGE',
                                    'https://maps.googleapis.com/maps/api/distancematrix/json?origins=33.0477696,-117.296921413&destinations=33.1240797535,-117.317765251&mode=walking&language=en-EN&sensor=false&key=AIzaSyDJh9EWCA_v0_B3SvjzjUA3OSVYufPJeGE',
                                    "{'status': 'OK', 'rows': [{'elements': [{'duration': {'text': '14 mins', 'value': 822}, 'distance': {'text': '10.6 km', 'value': 10637}, 'status': 'OK'}]}], 'origin_addresses': ['233 C St, Encinitas, CA 92024, USA'], 'destination_addresses': ['5754-5780 Paseo Del Norte, Carlsbad, CA 92008, USA']}",
                                    "{'status': 'OK', 'rows': [{'elements': [{'duration': {'text': '2 hours 4 mins', 'value': 7457}, 'distance': {'text': '10.0 km', 'value': 10028}, 'status': 'OK'}]}], 'origin_addresses': ['498 B St, Encinitas, CA 92024, USA'], 'destination_addresses': ['5754-5780 Paseo Del Norte, Carlsbad, CA 92008, USA']}",
                                    999.0, 999.0 ]

    outside_trip_table.to_sql('outside_trip_table',engine, if_exists = "replace")
    outside_route_table.to_sql('outside_route_table',engine, if_exists = "replace")
    google_city_to_poi_table.to_sql('google_city_to_poi_table',engine, if_exists = "replace")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("ALTER TABLE outside_trip_table ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE outside_route_table ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE google_city_to_poi_table ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE outside_trip_table ADD CONSTRAINT fk_outside_trip_user_name FOREIGN KEY (username) REFERENCES auth_user (username);")
    conn.commit()
    conn.close()
if __name__ == '__main__':
    init_outside_db_tables()