#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 00:40:55 2020

@author: danw
"""

from html.parser import HTMLParser

class TagStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
        
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_data(self):
        return "".join(self.fed)
    
def strip_html_tags(text: str):
    st = TagStripper()
    st.feed(text)
    return st.get_data()
        