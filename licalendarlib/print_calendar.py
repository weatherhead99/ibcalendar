#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 01:04:29 2020

@author: danw
"""

import tqdm
import pytz
import datetime
import os
from licalendarlib.localist_calendar import LocalistCalendarAPI
from html_template import html_format_event
from IPython.core.display import HTML, display
import tempfile

test_startdate = datetime.datetime(year=2020,month=1,day=9)
test_enddate = datetime.datetime(year=2020,month=2,day=1)
local_timezone = pytz.timezone("US/Pacific")

def download_levan_events(startdate=None, enddate=None):
    USC_CALENDAR_API_URL = "https://calendar.usc.edu"
    LEVAN_TAG = "LI-Humanities" 
    #get all events in next two weeks
    api = LocalistCalendarAPI(USC_CALENDAR_API_URL)
    events = api.get_filtered_events(LEVAN_TAG, startdate, enddate)
    return events

def create_image_thumbnails(events, thumbnail_size=(210,280), output_dir=None):
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="levan_calendar_")    
    op_paths = []
    print("downloading and resizing images...")
    for ev in tqdm.tqdm(events):
        im = ev.download_image(thumbnail_size)
        op_fd, op_fname = tempfile.mkstemp(prefix="event_", suffix=".png", dir=output_dir)
        with os.fdopen(op_fd,"wb") as f:
            im.save(f, "png")
        op_paths.append(op_fname)
    return op_paths
        

def print_html_events(events):
    for ev in events:
        display(HTML(html_format_event(ev)))

def print_txt_events(events):
    for ev in events:
        print("** %s ** " % ev.title)
        print("-" * (len(ev.title) + 6) )
    
        local_dt = ev.instances[0].datetime.astimezone(local_timezone)
        dstr = local_dt.strftime("%A, %B %d")
        tstr = local_dt.strftime("%I:%M %p")
    
        print("| %s | %s | %s |" % (dstr, tstr, ev.location_and_room))
        
        print(ev.get_short_description())
        print("")
