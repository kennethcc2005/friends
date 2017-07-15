calcluate travel time from last event of day one to first event of the next day
trip ruote not efficient 

current location feature : clear all text 

logic bug, now showing the reset and comfirm button when users click the resuggest button and also click delete button for the same event.

yosemite not find at all

Austin TX 4 day -day1 error on map

will need api views for outside poi suggest, poi add and poi delete
those functions needs different api than the full trip ones

when input event into db change to list not numpy array
and to update outside_add_search_event in trip_update.py at the same time

after checkfulladdress is false, and use the name for google api to search, find nothing, need to fix

profile_table

create table for store each direction of each city of outside trip 

need to json.loads
outside_trip_table:
	outside_route_ids
	event_id_lst
	outside_trip_details

outside_route_table:
	event_ids
	details

full_trip_table:
	trip_location_ids
	full_trip_details

day_trip_table:
	details
	event_ids