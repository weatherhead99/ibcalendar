#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 01:59:06 2020

@author: danw
"""
from .usc_event import Event
from string import Template
import pytz

PACIFIC = pytz.timezone("US/Pacific")

#taken from the source of the myemma emails

#the text style for the date, time and location
#NOTE: This is the old (wrong) spacing
#H1_STYLE = "display: block;font-size: 30px;font-weight: bold;margin: 0;line-height: 1.3;margin: 0;padding: 0;border: 0;font-size: 100%;font: inherit;vertical-align: baseline;font-family: Arial, Helvetica, sans-serif;font-size: 12px;font-weight: normal;color: #900;margin: 0;padding: 0;border: 0;font-size: 100%;font: inherit;vertical-align: baseline;font-family: Arial, Helvetica, sans-serif;font-size: 12px;font-weight: normal;color: #900;line-height: 30px"
H1_STYLE = "display: block; margin: 0px; padding: 0px; border: 0px; font-style: inherit; font-variant-caps: inherit; font-stretch: inherit; vertical-align: baseline; font-family: Arial, Helvetica, sans-serif; font-size: 12px; font-weight: normal; color: rgb(153, 0, 0); line-height: 18px;"

H1_SPAN_STYLE = "color: rgb(0, 28, 171); font-size: 15px"
    
#the text style for the event title
H2_STYLE = "display: block;font-size: 24px;font-weight: bold;color: #444;margin: 0 0 18px 0;line-height: 1.3;margin: 0;padding: 0;border: 0;font-size: 100%;font: inherit;vertical-align: baseline;font-family: Georgia, 'Times New Roman', Times, serif;font-size: 20px;font-weight: normal;color: #000;margin: 0;padding: 0;border: 0;font-size: 100%;font: inherit;vertical-align: baseline;font-family: Georgia, 'Times New Roman', Times, serif;font-size: 20px;font-weight: normal;color: #000;line-height: 24px"
    
#the text style for the description
DIV_STYLE = "display: block;margin-bottom: 10px;font-size: 12px;line-height: 1.5;font-weight: normal;font-family: Georgia, 'Times New Roman', Times, serif;font-size: 13px;color: #000;font-family: Georgia, 'Times New Roman', Times, serif;font-size: 13px;color: #000;line-height: 20px"
DIV_SPAN_STYLE = "font-size: 15px"

#the text style for the MORE url
URL_STYLE = "font-weight: normal;font-weight: normal;color: #920000;text-decoration: none;color: #920000;text-decoration: none;color: rgb(0, 28, 171)"

single_event_text_template = """ <h1 style="$H1_STYLE"> <strong> 
<span style="$H1_SPAN_STYLE"> $DT_STRING </span> </strong> </h1>
<h2 style="$H2_STYLE"> $TITLE_STRING </h2>
<div style="$DIV_STYLE"> <span style="$DIV_SPAN_STYLE"> $DESC_STRING  
<a data-name="MORE" data-type="url" href="$URL_STRING" style="$URL_STYLE">MORE </a> </span></div>""" 


def html_format_event(ev: Event, nsentences: int=2, local_timezone=PACIFIC):
    local_dt = ev.instances[0].datetime.astimezone(local_timezone)
    dstr = local_dt.strftime("%A, %B -%d")
    tstr = local_dt.strftime("%-I:%M %p")
    dtl_string = "%s | %s | %s" % (dstr, tstr, ev.location_and_room)
    desc_string = ev.get_short_description(nsentences)
    
    dct = {"H1_STYLE" : H1_STYLE,
           "H1_SPAN_STYLE": H1_SPAN_STYLE,
           "H2_STYLE" : H2_STYLE,
           "DIV_STYLE":  DIV_STYLE,
           "DIV_SPAN_STYLE" : DIV_SPAN_STYLE,
           "URL_STYLE": URL_STYLE,
           "DT_STRING" : dtl_string,
           "DESC_STRING": desc_string,
           "TITLE_STRING": ev.title,
           "URL_STRING" : ev.url}
    
    tpl = Template(single_event_text_template)
    return tpl.substitute(dct)

