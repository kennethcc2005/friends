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




	problem found:
		(fixed) id_ = str(v) + '0000'+str(event_ids[i+1]) in db_google_driving_walking_time, str(v)&event_ids[i+1] is float, id looks weird. ex. 234.000009242.0
		location dont have poi in our database, check missing_county_info.txt
		national park's  county may have None, most of it. 
		state, city = ('California', 'Newbury Park') problem with driving time, need to by ship// index = 1205 @ full_trip_table
		state, city = ('Alaska', 'Chignik Lake') problem with driving time, need to by ship// index = 1489 @ full_trip_table

	"""
