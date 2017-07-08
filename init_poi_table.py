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

print 'finish init poi table'