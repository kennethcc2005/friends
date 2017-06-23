import re
import ast

event_ids = u'[353.0000, 355.00000000000, 16043.00000000000000000000, 360, 354]'
print type(event_ids)
try:
	if type(ast.literal_eval(event_ids)) == list:
	    event_ids = map(float, ast.literal_eval(event_ids))
	    new_event_ids = map(int, (event_ids))
	else: 
	    event_ids = re.sub("\s+", ",", event_ids.strip())
	    event_ids = event_ids.replace('.', '')
	    event_ids = map(float, event_ids.strip('[').strip(']').strip(',').split(','))
	    new_event_ids = map(int, (event_ids))
except:

    event_ids = re.sub("\s+", ",", event_ids.strip())
    event_ids = event_ids.replace('.', '')
    event_ids = map(float, event_ids.strip('[').strip(']').strip(',').split(','))
    new_event_ids = map(int, (event_ids))
print new_event_ids, type(new_event_ids), type(new_event_ids[0])