import pandas as pd
import psycopg2
import os
import json
from sqlalchemy import create_engine
path = os.getcwd()
with open('api_key_list.config') as key_file:
    api_key_list = json.load(key_file)
conn_str = api_key_list["conn_str"]
engine = create_engine(api_key_list["engine"])

poi_detail_path = path+'/poi_detail_table_final_v2.csv'
poi_detail = pd.read_csv(poi_detail_path,index_col=0)
poi_detail.to_sql('poi_detail_table',engine, index=True, if_exists = "replace")
conn = psycopg2.connect(conn_str)
cur = conn.cursor()
cur.execute("ALTER TABLE poi_detail_table ADD COLUMN geom geometry(POINT,4326);")
cur.execute("UPDATE poi_detail_table SET geom = ST_SetSRID(ST_MakePoint(coord_long,coord_lat),4326);")

# cur.execute("CREATE INDEX idx_poi_geom ON poi_detail_table USING GIST(geom);")
conn.commit()
conn.close()
print 'finish init poi table'