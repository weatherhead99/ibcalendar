#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 22:07:54 2020

@author: danw
"""

import io
from typing import List
from licalendarlib.usc_event import Event, event_settings
from licalendarlib.html_template import html_format_event
import os.path
import zipfile
from slugify import slugify


SEPARATOR = "------------------------------------------------------------"

def generate_event_text(events: List[Event], settings: List[event_settings]):
    sio = io.StringIO()
    
    print("constructing HTML text file...")
    for ev, sts in zip(events, settings):
        if sts.enabled:
            html_string = html_format_event(ev, sts.nsentences)
            sio.writelines([SEPARATOR + os.linesep, html_string + os.linesep])
            
    return sio.getvalue()


def generate_event_images(events: List[Event], images):
    bio = io.BytesIO()
    bio_image = io.BytesIO()
    print("constructing image zip file...")
    with zipfile.ZipFile(bio, mode="w") as myzip:
        for ev, im in zip(events, images):
            bio_image.seek(0)
            bio_image.truncate(0)
            im.save(bio_image,"png")
            fname = slugify(ev.title) + ".png"
            myzip.writestr(fname, bio_image.getvalue())

    return bio.getvalue()