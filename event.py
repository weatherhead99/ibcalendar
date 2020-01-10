#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 00:50:49 2020

@author: danw
"""

from nltk import tokenize
from preprocess import strip_html_tags

def split_sentences(text: str):
    return tokenize.sent_tokenize(text)

class Event:
    def __init__(self, rawevent: dict):
        self._rawevent = rawevent
    
    @property
    def title(self):
        return self._rawevent["title"]

    def get_short_description(self, nsentences:int = 2):
        text = self.description_text
#        TODO: use nltk or something more clever!
        return " ".join(split_sentences(text)[:nsentences])

    @property
    def description_text(self):
        return strip_html_tags(self._rawevent["description"].strip())
    
    def __getitem__(self, idx):
        return self._rawevent[idx]