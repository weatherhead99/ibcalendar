#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 21:51:13 2020

@author: danw
"""

import datetime
from licalendarlib.localist_calendar import LocalistCalendarAPI
import warnings

if __name__ == "__main__":
    testapi = LocalistCalendarAPI("https://calendar.usc.edu")
    
    start = datetime.datetime(year=2020, month=9, day=18)
    end = start + datetime.timedelta(days=14)
    
    department_url_names = ["american_studies_and_ethnicity", "casden_institute", "USC_Shoah_Fondatin",
                            "french_and_italian", "crcc", "cpw", "classics", "creative_writing_literature",
                            "comparative_literature_colt", "english", "gender_studies", "history",
                            "institute_on_california_and_the_west_icw","latin_american_and_iberian_cultures",
                            "german_studies_program", "max_kade_institute", "school_of_religion", "society_of_fellows",
                            "usc_shinso_ito_center_for_japanese_religions_and_culture", "early_modern_studies_institute_emsi",
                            "visions_and_voices_the_arts_and_humanities_initiative", "usc_visual_studies_research_institute_vsri",
                            "thornton_school_of_music", "roski_school_of_art_and_design", "dramatic-arts", "fisher_museum_of_art",
                            "usc_libraries", "institute_for_catholic_studies", "campus_humanities", "kaufman", "pacific_asia_museum"]
    
    depts_data = testapi.get_departments()
    
    data_urlnames = [_["urlname"] for _ in depts_data]
    
    depts_found = []
    for urlname_search in department_url_names:
        try:
            idx = data_urlnames.index(urlname_search)
        except ValueError:
            warnings.warn("URLname: %s not found in calendar departments" % urlname_search)
        depts_found.append(depts_data[idx])
        
        
    print("searching department ids")
    deptids = [_["id"] for _ in depts_found]
    #dept_events = testapi.get_events_by_department(deptids, start, end)

    print("retrieving multiple department events")
    calendar_events = testapi.get_events_from_multiple_departments(start, end, deptids)
    levan_events = testapi.get_filtered_events("LI-Humanities", start, end)
