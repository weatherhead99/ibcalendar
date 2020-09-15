#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:04:37 2020

@author: danw
"""

import tqdm
import ipywidgets
from IPython.display import display, FileLink
from .html_template import html_format_event
from datetime import datetime, timedelta
from .localist_calendar import LocalistCalendarAPI
from .usc_event import event_settings
from io import BytesIO
from .generate_textfiles import generate_event_text, generate_event_images
import warnings

def get_png_str(image) -> bytes:
    byte_io = BytesIO()
    image.save(byte_io, "png")
    return byte_io.getvalue()

class EventDownloader:
    CALENDAR_API_URL = "https://calendar.usc.edu"
    KEYWORD_TAG = "LI-Humanities"
    DEPARTMENT_URL_NAMES = ["american_studies_and_ethnicity", "casden_institute", "USC_Shoah_Fondatin",
                            "french_and_italian", "crcc", "cpw", "classics", "creative_writing_literature",
                            "comparative_literature_colt", "english", "gender_studies", "history",
                            "institute_on_california_and_the_west_icw","latin_american_and_iberian_cultures",
                            "german_studies_program", "max_kade_institute", "school_of_religion", "society_of_fellows",
                            "usc_shinso_ito_center_for_japanese_religions_and_culture", "early_modern_studies_institute_emsi",
                            "visions_and_voices_the_arts_and_humanities_initiative", "usc_visual_studies_research_institute_vsri",
                            "thornton_school_of_music", "roski_school_of_art_and_design", "dramatic-arts", "fisher_museum_of_art",
                            "usc_libraries", "institute_for_catholic_studies", "campus_humanities", "kaufman", "pacific_asia_museum"]
    

    def display(self):
        display(self.button_box)

    def __init__(self, browser_widget = None):
        self._browser = browser_widget
        self._startdate = self.get_next_friday()
        self._enddate = self._startdate + timedelta(days=21)
        self.start_date_selector = ipywidgets.DatePicker(value=self._startdate,
                                                         description="start date")
        self.end_date_selector = ipywidgets.DatePicker(value=self._enddate,
                                                       description="end date")

        self.download_button = ipywidgets.Button(description="download events")
        
        
        self.button_box = ipywidgets.HBox([self.start_date_selector, 
                                           self.end_date_selector, 
                                           self.download_button])


        self.download_button.on_click(self._event_download_button_clicked)
        

        self._events = []
        self._images = []
        
        self.api = LocalistCalendarAPI(self.CALENDAR_API_URL)
        
    def get_next_friday(self):
        today = datetime.today()
        next_friday = today + timedelta( (4 - today.weekday() % 7))
        return next_friday


    def download_events(self, startdate, enddate):
        print("retrieving events tagged with LI-Humanities...")
        levan_events = self.api.get_filtered_events(self.KEYWORD_TAG, startdate, enddate)

        print("querying department ids from known urls...")
        all_depts_data = self.api.get_departments()
        data_urlnames = [_["urlname"] for _ in all_depts_data]
        deptids = []
        for urlname_search in self.DEPARTMENT_URL_NAMES:
            try:
                idx = data_urlnames.index(urlname_search)
            except ValueError:
                warnings.warn("URLname: %s not found in calendar departments" % urlname_search)
            deptids.append(all_depts_data[idx]["id"])
            
        print("retrieving events from humanities calendar for %d departments..." % len(deptids)) 
        hum_events = self.api.get_events_from_multiple_departments(startdate, enddate, deptids)

        print("compiling list of all events...")
        self._events = sorted(levan_events + hum_events)

        print("got %d events" % len(self._events))


        self._images.clear()
        print("retrieving image files...")
        for ev in tqdm.tqdm(self._events):
            im = ev.download_image()
            self._images.append(im)

    def _event_download_button_clicked(self, event):
        self._startdate = self.start_date_selector.value
        self._enddate = self.end_date_selector.value
        self.download_events(self._startdate, self._enddate)
        self.update_browser()

    def update_browser(self):
        if self._browser is not None:
            self._browser.update_events(self._events)
            self._browser.update_images(self._images)




class EventBrowser:
    DEFAULT_SENTENCES = 2

    def display(self):
        display(self.event_selector, self.settingsbox, self.DownloadButton,
                self.download_images_button,
                self.imagepreview, self.htmlpreview, self.rawpreview)

    def __init__(self, events=None, images = None):
        self.events = events if events is not None else []
        self.images = images if images is not None else []
        self.thumbnails = []

        self._init_settings()

        minval = 1 if len(self.events) > 0 else 0

        self.event_selector = ipywidgets.BoundedIntText(
                value=minval, min=minval, max=len(self.events), step=1,
                description="event number")

        self.nsentences = ipywidgets.IntSlider(value=2, min=1, max=2, step=1,
                                               description="sentences")

        self.enable_event = ipywidgets.Checkbox(value=True,
                                                description="enable this event")

        self.settingsbox = ipywidgets.HBox([self.nsentences, self.enable_event])
        
        self.htmlpreview = ipywidgets.HTML()
        self.imagepreview = ipywidgets.Image()
        self.rawpreview = ipywidgets.Textarea()

        self.DownloadButton = ipywidgets.Button(description="download text file")
        self.download_images_button = ipywidgets.Button(description="download images")

        self._html_caches = {}

        self._setup_event_widgets()

    def _init_settings(self):
        self._settings = {}
        for evnum in range(len(self.events)):
            self._settings[evnum] = event_settings(nsentences=self.DEFAULT_SENTENCES,
                          enabled=True,
                          thumbnail_size=(210,280))

    def _setup_event_widgets(self):
        #setup widgets
        if len(self.events) == 0:
            self.event_selector.disabled = True
            self.nsentences.disabled = True

        self.event_selector.observe(self._event_select_handle, "value")
        self.nsentences.observe(self._event_change_nsentences, "value")
        self.enable_event.observe(self._event_change_enabled, "value")
        
        self.DownloadButton.on_click(self.get_text_file)
        self.download_images_button.on_click(self.get_image_file)
        
        if len(self.events) > 0:
            self.display_event(0,self.DEFAULT_SENTENCES)

    def _event_select_handle(self, change):
        self.display_event(change.new - 1, None)
        self.save_settings()

    def _event_change_nsentences(self, change):
        self.display_event(self.event_selector.value -1, change.new)
        self.save_settings()

    def _event_change_enabled(self, change):
        self.save_settings()


    def update_events(self, events):
        self.events = events
        self._init_settings()
        self.event_selector.max = len(events)
        self.event_selector.min = 1

        self.event_selector.disabled = False
        self.nsentences.disabled = False

    def update_images(self, images):
        if len(images) != len(self.events):
            raise IndexError("mismatched length of images and events")
        self.images = images
        self.thumbnails.clear()

        for ind,im in enumerate(self.images):
            thumbsize = self._settings[ind].thumbnail_size
            thumb = im.copy()
            thumb.thumbnail(thumbsize)
            self.thumbnails.append(thumb)
        self.display_event(self.event_selector.value-1, None)

    def save_settings(self):
        evnum = self.event_selector.value -1
        self._settings[evnum] = event_settings(nsentences=self.nsentences.value,
                              enabled=self.enable_event.value,
                              thumbnail_size=(210,280))

    def get_text_file(self, change):
        txt = generate_event_text(self.events, list(self._settings.values()))
        with open("generated_events.txt", "w") as f:
            f.write(txt)
        display(FileLink("generated_events.txt"))
        
    def get_image_file(self, change):
        zfile = generate_event_images(self.events, self.thumbnails)
        with open("generated_images.zip", "wb") as f:
            f.write(zfile)
        display(FileLink("generated_images.zip"))
        
        

    def display_event(self, evnum: int, nsentences: int):
        if nsentences is None:
            nsentences = self._settings[evnum].nsentences

        if evnum in self._html_caches and self._html_caches[evnum][0] == nsentences:
            html = self._html_caches[evnum][1]
        else:
            html = html_format_event(self.events[evnum], nsentences)
            self._html_caches[evnum] = (nsentences, html)

        self.nsentences.max = self.events[evnum].n_desc_sentences
        self.nsentences.value = nsentences
        self.enable_event.value = self._settings[evnum].enabled
        self.htmlpreview.value = html
        self.rawpreview.value = html

        if len(self.images) > 0:
            #TODO: is there a better method to use here?
            self.imagepreview.value = get_png_str(self.thumbnails[evnum])
