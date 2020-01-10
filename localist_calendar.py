import requests
import datetime
from event import Event

class LocalistCalendarAPI:
    DATE_FMT = "%Y-%m-%d"
    def __init__(self, url: str):
        self.baseurl = url
        
    def get_filtered_events(self, keyword: str, startdate: datetime.datetime,
                            enddate: datetime.datetime):
        startdatestr = startdate.strftime(self.DATE_FMT)
        enddatestr = enddate.strftime(self.DATE_FMT)
        rparams = {"end" : enddatestr, "start" : startdatestr, 
                   "keyword" : keyword, "pp" : 100}
        resp = requests.get(self.baseurl + "/api/2/events",
                                     params=rparams)
        
        if resp.status_code != 200:
            raise RuntimeError("invalid response received from Localist API")
        
        respjson = resp.json()
        npages = respjson["page"]["total"]
        events = [Event(_["event"]) for _ in respjson["events"]]
        
        for i in range(2,npages):
            rparams["page"] = i
            resp = requests.get(self.baseurl + "/api/2/events",
                                params=rparams)
            
            if resp.status_code != 200:
                raise RuntimeError("invalid response received from Localist API")
            
            events.extend( Event(_["event"]) for _ in resp.json())
        return events


