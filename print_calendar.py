#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 01:04:29 2020

@author: danw
"""

import datetime
from localist_calendar import LocalistCalendarAPI


USC_CALENDAR_API_URL = "https://calendar.usc.edu"
LEVAN_TAG = "LI-Humanities"


#get all events in next two weeks
today = datetime.datetime.today()

api = LocalistCalendarAPI(USC_CALENDAR_API_URL)

events = api.get_filtered_events(LEVAN_TAG, 
                                 datetime.datetime(year=2020,month=1,day=9), 
                                 datetime.datetime(year=2020,month=2,day=1))

for ev in events:
    print("** %s ** " % ev.title)
    print("-" * (len(ev.title) + 6) )
    print(ev.get_short_description())
    print("")
