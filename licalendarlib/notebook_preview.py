#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:04:37 2020

@author: danw
"""

import ipywidgets 
from IPython.core.display import display
from html_template import html_format_event
from collections import namedtuple

event_settings = namedtuple("event_settings", ("nsentences", "enabled"))

class EventBrowser:
    DEFAULT_SENTENCES = 2
    def __init__(self, events):
        self.events = events if events is not None else []
        self._init_settings()
        self.event_selector = ipywidgets.BoundedIntText(
                value=1, min=1, max=len(events), step=1,
                description="select event to display")
        
        self.nsentences = ipywidgets.IntSlider(value=2, min=1, max=2, step=1,
                                               description="number of sentences to display")
        
        self.enable_event = ipywidgets.Checkbox(value=True, 
                                                description="enable this event in the output")

        self.htmlpreview = ipywidgets.HTML()
        self._html_caches = {}
        
        if self.events is not None:
            self._setup_event_widgets()
   
        display(self.event_selector, self.nsentences, self.enable_event, self.htmlpreview)
    
    def _init_settings(self):
        self._settings = {}
        for evnum in range(len(self.events)):
            self._settings[evnum] = event_settings(nsentences=self.DEFAULT_SENTENCES,
                          enabled=True)
    
    def _setup_event_widgets(self):
        #setup widgets

        self.event_selector.observe(self._event_select_handle, "value") 
        self.nsentences.observe(self._event_change_nsentences, "value")
        self.enable_event.observe(self._event_change_enabled, "value")
        self.display_event(0,self.DEFAULT_SENTENCES)

    def _event_select_handle(self, change):
        self.display_event(change.new - 1, None)
        self.save_settings()

    def _event_change_nsentences(self, change):
        self.display_event(self.event_selector.value -1, change.new)
        self.save_settings()
            
    def _event_change_enabled(self, change):
        self.save_settings()

    def save_settings(self):
        evnum = self.event_selector.value -1
        self._settings[evnum] = event_settings(nsentences=self.nsentences.value,
                              enabled=self.enable_event.value)

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
    
        