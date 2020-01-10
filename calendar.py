import requests
import json
import datetime
from event import Event

USC_CALENDAR_API_URL = "https://calendar.usc.edu"
LEVAN_TAG = "LI-Humanities"



class LocalistCalendarAPI:
    def __init__(self, url: str):
        self.baseurl = url
        
    def get_filtered_events(self, keyword: str, startdate: datetime.datetime,
                            enddate: datetime.datetime):
        startdatestr = startdate.strftime("%Y-%m-%d")
        enddatestr = enddate.strftime("%Y-%m-%d")
        rparams = {"end" : enddatestr, "start" : startdatestr, 
                   "keyword" : keyword, "pp" : 100}
        resp = requests.get(self.baseurl + "/api/2/events",
                                     params=rparams).json()
        
        npages = resp["page"]["total"]
        events = [Event(_["event"]) for _ in resp["events"]]
        
        for i in range(2,npages):
            rparams["page"] = i
            resp = requests.get(self.baseurl + "/api/2/events",
                                params=rparams).json()
            events.extend( Event(_["event"]) for _ in resp)
        
        return events

#get all events in next two weeks
today = datetime.datetime.today()
todaystr = today.strftime("%Y-%m-%d")


api = LocalistCalendarAPI(USC_CALENDAR_API_URL)

events = api.get_filtered_events(LEVAN_TAG, 
                                 datetime.datetime(year=2020,month=1,day=9), 
                                 datetime.datetime(year=2020,month=2,day=1))

for ev in events:
    print("** %s ** " % ev.title)
    print("-" * (len(ev.title) + 6) )
    print(ev.get_short_description())
    print("")
    