#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 00:50:49 2020

@author: danw
"""

from typing import Optional
import dateutil
import datetime
import requests
from nltk import tokenize
from .preprocess import strip_html_tags
from PIL import Image
import io
from collections import namedtuple

event_settings = namedtuple("event_settings", ("nsentences", "enabled",
                                               "thumbnail_size"))

def split_sentences(text: str):
    return tokenize.sent_tokenize(text)

class Item:
    def __init__(self, rawcontent: dict):
        self._rawcontent = rawcontent
    
    def __getitem__(self, idx):
        return self._rawcontent[idx]


class EventInstance(Item):
    @property
    def datetime(self):
        return dateutil.parser.parse(self["start"])
    
    def __lt__(self, other):
        return self.datetime < other.datetime
    def __le__(self, other):
        return self.datetime <= other.datetime
    def __gt__(self, other):
        return self.datetime > other.datetime
    def __ge__(self,other):
        return self.datetime >= other.datetime
    


def cmpcheck(func):
    def f(self, other):
        if len(self.instances) !=1 or len(other.instances) != 1:
            raise ValueError("cannot compare events with multiple instances")
        return func(self, other)
    return f


class Event(Item):

    @cmpcheck
    def __lt__(self, other):
        return self.instances[0] < other.instances[0]
    
    @cmpcheck
    def __le__(self, other):
        return self.instances[0] <= other.instances[0]
    
    @cmpcheck
    def __gt__(self, other):
        return self.instances[0] > other.instances[0]
    
    @cmpcheck
    def __ge__(self, other):
        return self.instances[0] >= other.instances[0]
    
    @property
    def title(self):
        return self["title"]

    @property
    def url(self):
        return self["localist_url"]

    @property
    def instances(self):
        return [EventInstance(_["event_instance"]) for _ in self["event_instances"] ]

    def get_short_description(self, nsentences:int = 2):
        if not hasattr(self, "_tokenized_desc"):
            self._tokenized_desc = split_sentences(self.description_text)
#        TODO: use nltk or something more clever!
        return " ".join(self._tokenized_desc[:nsentences])

    @property
    def n_desc_sentences(self) -> int:
        if not hasattr(self, "_tokenized_desc"):
            self._tokenized_desc = split_sentences(self.description_text)
        return len(self._tokenized_desc)

    def download_image(self, size: Optional[tuple] = None):
        imurl = self["photo_url"]
        
        resp = requests.get(imurl, stream=True)
        if resp.status_code != 200:
            raise RuntimeError("invalid response trying to download image!")
        
        im = Image.open(io.BytesIO(resp.raw.data))
        if size is not None:
            im.thumbnail(size, Image.ANTIALIAS)
        return im
        
    @property
    def description_text(self):
        return strip_html_tags(self["description"].strip())
    
    @property
    def location_and_room(self):
        if self["room_number"] is not None and len(self["room_number"]) > 0:
            return "%s, %s" % (self["location_name"], self["room_number"])
        elif self["room_number"] is None:
            return "Virtual"
        else:
            return self["location_name"]
    
    @property
    def department_names(self):
        try:
            deps = self["departments"]
        except KeyError:
            return []
        return [_["name"] for _ in deps]
    
    @property
    def department_ids(self):
        try:
            deps = self["departments"]
        except KeyError:
            return []
        return [_["id"] for _ in deps]
    
    def __repr__(self) -> str:
        return "Event( '%s')" % self.title
    
