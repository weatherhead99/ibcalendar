import requests
import datetime
from licalendarlib.usc_event import Event
from typing import Sequence, Dict, Any, Tuple


class LocalistCalendarAPI:
    DATE_FMT = "%Y-%m-%d"
    def __init__(self, url: str):
        self.baseurl = url
    
    def _get_date_params(self, startdate: datetime.datetime,
                         enddate: datetime.datetime) -> Dict[str,Any]:
        startdatestr = startdate.strftime(self.DATE_FMT)
        enddatestr = enddate.strftime(self.DATE_FMT)
        rparams = {"start" : startdatestr, "end" : enddatestr,
                   "pp" : 100}
        return rparams
    
    def get_departments(self):
        resp = requests.get(self.baseurl + "/api/2/departments")
        
        departments = [_ for _ in resp.json()["departments"]]
        
        for pagejson in self._localist_api_generate_pages(self.baseurl + "/api/2/departments", resp.json(), {}):
            departments.extend(pagejson["departments"])
        return [_["department"] for _ in departments]

    def get_groups(self):
        resp = requests.get(self.baseurl + "/api/2/groups")
        
        departments = [_ for _ in resp.json()["groups"]]
        
        for pagejson in self._localist_api_generate_pages(self.baseurl + "/api/2/groups", resp.json(), {}):
            departments.extend(pagejson["groups"])
        return [_["group"] for _ in departments]

    def _localist_api_events_request(self, startdate: datetime.datetime,
                              enddate: datetime.datetime,
                              **extra_params) -> Tuple[dict, dict]:
        rparams = self._get_date_params(startdate, enddate)
        rparams.update(**extra_params)
        resp = requests.get(self.baseurl + "/api/2/events", params=rparams)
        if resp.status_code != 200:
            raise RuntimeError("invalid response received from Localist API")
        
        return resp.json(), rparams

    def get_events_from_multiple_departments(self, startdate: datetime.datetime,
                                             enddate: datetime.datetime,
                                             department_ids: Sequence[int], 
                                             **extra_params):
        rparams = self._get_date_params(startdate, enddate)
        paramslst = [(k, v) for k,v in rparams.items()]
        for gid in department_ids:
            paramslst.append( ("group_id[]", gid))
        resp = requests.get(self.baseurl + "/api/2/events", params=paramslst).json()
        
        
        events = [Event(_["event"]) for _ in resp["events"]]
        for pagejson in  self._localist_api_generate_pages(self.baseurl + "/api/2/events", resp, paramslst):
            events.extend( Event(_["event"]) for _ in pagejson["events"])
        return events


    def _localist_api_generate_pages(self, url: str, resp, rparams):
        npages = resp["page"]["total"]
        for i in range(2,npages):
            rparams["page"] = i
            #resp = requests.get(self.baseurl + "/api/2/events", params=rparams)
            resp = requests.get(url, params=rparams)
            if resp.status_code != 200:
                raise RuntimeError("invalid response received from Localist API")
            yield resp.json()

    def get_filtered_events(self, keyword: str, startdate: datetime.datetime,
                            enddate: datetime.datetime):
        
        respjson, rparams= self._localist_api_events_request(startdate, enddate, keyword=keyword)
        events = [Event(_["event"]) for _ in respjson["events"]]
        
        for pagejson in self._localist_api_generate_pages(self.baseurl + "/api/2/events", respjson, rparams):
            events.extend( Event(_["event"]) for _ in pagejson["events"])
        return events


    def get_events_from_department(self, department: int,
                                   startdate: datetime.datetime, enddate: datetime.datetime):
        respjson, rparams = self._localist_api_events_request(startdate, enddate, group_id=department)
        events = [Event(_["event"]) for _ in respjson["events"]]
        
        for pagejson in self._localist_api_generate_pages(self.baseurl + "/api/2/events", respjson, rparams):
            events.extend( Event(_["event"] for _ in pagejson["events"]))
        return events



    def get_events_by_department(self, departments: Sequence[int], 
                                 startdate: datetime.datetime, enddate: datetime.datetime):
        
        respjson, rparams = self._localist_api_events_request(startdate, enddate)
        
        events = []
        for evjson in respjson["events"]:
            tempev = Event(evjson["event"])
            if any( a in  departments for a  in tempev.department_ids):
                events.append(tempev)

        for pagejson in self._localist_api_generate_pages(self.baseurl + "/api/2/events", respjson, rparams):
            for evjson in pagejson["events"]:
                tempev = Event(evjson["event"])
                if any( a in  departments for a  in tempev.department_ids):
                    events.append(tempev)

        return events


