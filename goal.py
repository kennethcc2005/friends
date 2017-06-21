def thing to do():
	print """
	api:
	1. user securities
	2. Known issues: can create unlimited users if endpoints is known. should use CAPTCHA
	3. Seperated auth for different cases get/post
	4. Token needs to expire...now last forever!
	"""


	
	print """
	outside :
	1.	one way trip/ round trip
	2.	allow user change
	3.	better route
	4.	more than 1 day
	5.	mapping poi show map
	6.	base on state>find_next state> county in those state >find poi in all county

	model, base on poi_type, but not some type. 
	create new route type column
	親子一日遊(水)，美食遊food，shopping(change visit length)，清空心靈（parks），人民關懷（landmark, measuer），泡溫泉(spa), 一日玩不完(national park theme park) X nightnight
	base on the time of items in the route choose the type for this route.
	sroce system, score, type(tag)ex(park, measue)
	y=mx+b
	top 4 ruote
	"""



	print """
	city:
	1.	allow user change
	2.	better model
	3.	web app -- show route map
	4.	check data not in our data base
	5.	check full trip for all 5 days
	6.	take out poi from poi_table where tag = ex. tour, ....
	7.	add state == 'Puerto Rico', Virgin Islands' into our database poi_table

	city V2
	1.	find poi base on radius from city
	2.	base on # of poi points change incease the radius.
	"""

	print """
	create your own trip
	1.	user insert location that they want to go
	2.	base on how much time events need, if time less, find events around location/ if time alot, draw circle using the location and find events inside.
	3.	publish your trip, and open for people to join
	4.	new page show simple ruote of the trip


	"""


	print """
	problem found: 
		drop duplicate in poi_detail_table_v2 (done)
		change type event_ids 
		(fixed) id_ = str(v) + '0000'+str(event_ids[i+1]) in db_google_driving_walking_time, str(v)&event_ids[i+1] is float, id looks weird. ex. 234.000009242.0
		location dont have poi in our database, check missing_county_info.txt
		national park's  county may have None, most of it. 
		state, city = ('California', 'Newbury Park') problem with driving time, need to by ship// index = 1205 @ full_trip_table
		state, city = ('Alaska', 'Chignik Lake') problem with driving time, need to by ship// index = 1489 @ full_trip_table

	"""

	print """
	FOR FULL TRIP, OUTSIDE TRIP TABLE: VISIBLE
	will allow the user to delete their trips as seeting the visible to false
	setting
	-0- BOOL COL for VISIBLE"""




	