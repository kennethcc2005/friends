import pandas as pd
import psycopg2
import os
import json
from sqlalchemy import create_engine

path = os.getcwd()
with open('api_key_list.config') as key_file:
    api_key_list = json.load(key_file)
conn_str = api_key_list["conn_str"]
engine = api_key_list["engine"]
# user = "Gon"
# conn_str = "dbname='travel_with_friends' user={} host='localhost'".format(user)
# engine = create_engine('postgresql://{}@localhost:5432/travel_with_friends'.format(user))
df_counties_path = path+'/us_cities_states_counties.csv'
df_city_coords_path = path+'/all_cities_coords.csv'
poi_detail_path = path+'/poi_detail_table_final_v1.csv'


def init_db_tables():
    full_trip_table = pd.DataFrame(columns =['username', 'full_trip_id', 'trip_location_ids', 'regular', 'county', 'state', 'details', 'n_days'])

    day_trip_locations_table = pd.DataFrame(columns =['trip_locations_id','full_day', 'regular', 'county', 'state','details','event_type','event_ids'])

    google_travel_time_table = pd.DataFrame(columns =['id_field','orig_name','orig_idx','dest_name','dest_idx','orig_coord_lat','orig_coord_long',\
                                           'dest_coord_lat','dest_coord_long','orig_coords','dest_coords','google_driving_url',\
                                           'google_walking_url','driving_result','walking_result','google_driving_time',\
                                           'google_walking_time'])
    day_trip_locations_table.loc[0] = ['CALIFORNIA-SAN-DIEGO-1-3-0', True, True, 'SAN DIEGO', 'California',
       ["{'address': '15500 San Pasqual Valley Rd, Escondido, CA 92027, USA', 'id': 2259, 'day': 0, 'name': u'San Diego Zoo Safari Park'}", "{'address': 'Safari Walk, Escondido, CA 92027, USA', 'id': 2260, 'day': 0, 'name': u'Meerkat'}", "{'address': '1999 Citracado Parkway, Escondido, CA 92029, USA', 'id': 3486, 'day': 0, 'name': u'Stone'}", "{'address': '1999 Citracado Parkway, Escondido, CA 92029, USA', 'id': 3487, 'day': 0, 'name': u'Stone Brewery'}", "{'address': 'Mount Woodson Trail, Poway, CA 92064, USA', 'id': 4951, 'day': 0, 'name': u'Lake Poway'}", "{'address': '17130 Mt Woodson Rd, Ramona, CA 92065, USA', 'id': 4953, 'day': 0, 'name': u'Potato Chip Rock'}", "{'address': '17130 Mt Woodson Rd, Ramona, CA 92065, USA', 'id': 4952, 'day': 0, 'name': u'Mt. Woodson'}"],
       'big','[2259, 2260,3486,3487,4951,4953,4952]']
    google_travel_time_table.loc[0] = ['439300002871', u'Moonlight Beach', 4393.0,
       u'Carlsbad Flower Fields', 2871.0, 33.047769600024424, -117.29692141333341,
       33.124079753475236, -117.3177652511278, 
       '33.0477696,-117.296921413', '33.1240797535,-117.317765251',
       'https://maps.googleapis.com/maps/api/distancematrix/json?origins=33.0477696,-117.296921413&destinations=33.1240797535,-117.317765251&mode=driving&language=en-EN&sensor=false&key=AIzaSyDJh9EWCA_v0_B3SvjzjUA3OSVYufPJeGE',
       'https://maps.googleapis.com/maps/api/distancematrix/json?origins=33.0477696,-117.296921413&destinations=33.1240797535,-117.317765251&mode=walking&language=en-EN&sensor=false&key=AIzaSyDJh9EWCA_v0_B3SvjzjUA3OSVYufPJeGE',
       "{'status': 'OK', 'rows': [{'elements': [{'duration': {'text': '14 mins', 'value': 822}, 'distance': {'text': '10.6 km', 'value': 10637}, 'status': 'OK'}]}], 'origin_addresses': ['233 C St, Encinitas, CA 92024, USA'], 'destination_addresses': ['5754-5780 Paseo Del Norte, Carlsbad, CA 92008, USA']}",
       "{'status': 'OK', 'rows': [{'elements': [{'duration': {'text': '2 hours 4 mins', 'value': 7457}, 'distance': {'text': '10.0 km', 'value': 10028}, 'status': 'OK'}]}], 'origin_addresses': ['498 B St, Encinitas, CA 92024, USA'], 'destination_addresses': ['5754-5780 Paseo Del Norte, Carlsbad, CA 92008, USA']}",
       13.0, 124.0]
    full_trip_table.loc[0] = ['zoesh', 'CALIFORNIA-SAN-DIEGO-1-3',
       "['CALIFORNIA-SAN-DIEGO-1-3-0', 'CALIFORNIA-SAN-DIEGO-1-3-1', 'CALIFORNIA-SAN-DIEGO-1-3-2']",
       True, 'SAN DIEGO', 'California',
       '["{\'address\': \'15500 San Pasqual Valley Rd, Escondido, CA 92027, USA\', \'id\': 2259, \'day\': 0, \'name\': u\'San Diego Zoo Safari Park\'}", "{\'address\': \'Safari Walk, Escondido, CA 92027, USA\', \'id\': 2260, \'day\': 0, \'name\': u\'Meerkat\'}", "{\'address\': \'1999 Citracado Parkway, Escondido, CA 92029, USA\', \'id\': 3486, \'day\': 0, \'name\': u\'Stone\'}", "{\'address\': \'1999 Citracado Parkway, Escondido, CA 92029, USA\', \'id\': 3487, \'day\': 0, \'name\': u\'Stone Brewery\'}", "{\'address\': \'Mount Woodson Trail, Poway, CA 92064, USA\', \'id\': 4951, \'day\': 0, \'name\': u\'Lake Poway\'}", "{\'address\': \'17130 Mt Woodson Rd, Ramona, CA 92065, USA\', \'id\': 4953, \'day\': 0, \'name\': u\'Potato Chip Rock\'}", "{\'address\': \'17130 Mt Woodson Rd, Ramona, CA 92065, USA\', \'id\': 4952, \'day\': 0, \'name\': u\'Mt. Woodson\'}", "{\'address\': \'1 Legoland Dr, Carlsbad, CA 92008, USA\', \'id\': 2870, \'day\': 1, \'name\': u\'Legoland\'}", "{\'address\': \'5754-5780 Paseo Del Norte, Carlsbad, CA 92008, USA\', \'id\': 2871, \'day\': 1, \'name\': u\'Carlsbad Flower Fields\'}", "{\'address\': \'211-359 The Strand N, Oceanside, CA 92054, USA\', \'id\': 2089, \'day\': 1, \'name\': u\'Oceanside Pier\'}", "{\'address\': \'211-359 The Strand N, Oceanside, CA 92054, USA\', \'id\': 2090, \'day\': 1, \'name\': u\'Pier\'}", "{\'address\': \'1016-1024 Neptune Ave, Encinitas, CA 92024, USA\', \'id\': 2872, \'day\': 1, \'name\': u\'Encinitas\'}", "{\'address\': \'625 Pan American Rd E, San Diego, CA 92101, USA\', \'id\': 147, \'day\': 2, \'name\': u\'Balboa Park\'}", "{\'address\': \'1849-1863 Zoo Pl, San Diego, CA 92101, USA\', \'id\': 152, \'day\': 2, \'name\': u\'San Diego Zoo\'}", "{\'address\': \'701-817 Coast Blvd, La Jolla, CA 92037, USA\', \'id\': 148, \'day\': 2, \'name\': u\'La Jolla\'}", "{\'address\': \'10051-10057 Pebble Beach Dr, Santee, CA 92071, USA\', \'id\': 4630, \'day\': 2, \'name\': u\'Santee Lakes\'}", "{\'address\': \'Lake Murray Bike Path, La Mesa, CA 91942, USA\', \'id\': 4545, \'day\': 2, \'name\': u\'Lake Murray\'}", "{\'address\': \'4905 Mt Helix Dr, La Mesa, CA 91941, USA\', \'id\': 4544, \'day\': 2, \'name\': u\'Mt. Helix\'}", "{\'address\': \'1720 Melrose Ave, Chula Vista, CA 91911, USA\', \'id\': 1325, \'day\': 2, \'name\': u\'Thick-billed Kingbird\'}", "{\'address\': \'711 Basswood Ave, Imperial Beach, CA 91932, USA\', \'id\': 1326, \'day\': 2, \'name\': u\'Lesser Sand-Plover\'}"]',
       3.0]
    full_trip_table.to_sql('full_trip_table',engine, if_exists = "replace")
    day_trip_locations_table.to_sql('day_trip_table',engine, if_exists = "replace")
    google_travel_time_table.to_sql('google_travel_time_table',engine, if_exists = "replace")
    poi_detail = pd.read_csv(poi_detail_path,index_col=0)
    poi_detail.to_sql('poi_detail_table_v2',engine, index=True, if_exists = "replace")
    df_counties = pd.read_csv(df_counties_path,sep='|')
    df_counties_u = df_counties.drop('City alias',axis = 1).drop_duplicates()
    df_counties_u.columns = ["city","state_abb","state","county"]
    df_counties_u.to_sql('county_table',engine, if_exists = "replace")
    cities_coords = pd.read_csv(df_city_coords_path)
    cities_coords = cities_coords[['city', 'state','nation','coord0','coord1']].drop_duplicates()
    cities_coords.columns = [['city', 'state','nation','coord_lat','coord_long']]
    cities_coords.to_sql('all_cities_coords_table',engine, index=True, if_exists = "replace")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("ALTER TABLE all_cities_coords_table ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE poi_detail_table_v2 ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE full_trip_table ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE day_trip_table ADD PRIMARY KEY (index);")
    cur.execute("ALTER TABLE google_travel_time_table ADD PRIMARY KEY (id_field);")
    cur.execute("ALTER TABLE county_table ADD PRIMARY KEY (index);")
    # cur.execute("ALTER TABLE full_trip_table ADD CONSTRAINT fk_full_trip_user_name FOREIGN KEY (username) REFERENCES auth_user (username);")
    conn.commit()
    conn.close()
    print "finish init database"
if __name__ == '__main__':
    init_db_tables()