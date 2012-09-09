# -*- coding: utf-8 -*-

import sys
import codecs
import re
from HTMLParser import HTMLParser

def lookup_day(s):
    mapping = {
            u'Понеділок': u'ПН',
            u'Вівторок': u'ВТ',
            u'Середа': u'СР',
            u'Четвер': u'ЧТ',
            u'П’ятниця': u'ПТ',
            u'Субота': u'СБ',
            }
    for k, v in mapping.items():
        if k in s:
            return v
    return None

def lookup_time(s):
    mapping = {
            u'8.30': u'08:30-09:50', 
            u'10.00': u'10:00-11:20', 
            u'11.40': u'11:40-13:00', 
            u'13.30': u'13:30-14:50', 
            u'15.00': u'15:00-16:20', 
            u'16.30': u'16:30-17:50', 
            u'18.00': u'18:00-19:20'
            }
    for k, v in mapping.items():
        if k in s:
            return v
    return None

def lookup_weeks(s):
    try:
        weeks = re.findall(u'([0-9, \t-]+)т', s)[0]
        weeks = filter(lambda x: x not in ' \t', weeks)
    except IndexError:
        weeks = None
    return weeks

def lookup_room(s):
    try:
        room = re.findall(u'(\d+-\w+)', s, re.UNICODE)[-1]
    except:
        room = None
    return room

def lookup_group(s):
    try:
        room = re.findall(u'гр\.(\d)', s, re.UNICODE)[-1]
    except:
        room = None
    return room


def lookup_lecturer(s):
    try:
        lecturer = re.findall(u'(cт\. в\.|ст\.\s?в\.|ст\.\s?викл\.|доц\.|проф\.|ас\.)([^.]*\.[^.]*\.)', s)[0][1]
        lecturer = re.sub('[\t\n]+', ' ', lecturer)
        lecturer = lecturer.replace('.', '. ')
        lecturer = re.sub('[ ]+', ' ', lecturer)
        lecturer = lecturer.lstrip('~ ')
    except IndexError:
        lecturer = None
    return lecturer


class FESParser(HTMLParser):
    def init_timetable_vars(self):
        self.day = None
        self.time = None
        self._reset_lesson_related()

    def _reset_lesson_related(self):
        self.lecturer = None
        self.group = None
        self.room = None
        self.weeks = None
        self.course = None

    def handle_starttag(self, tag, attrs):
        pass
        #print "Encountered a start tag:", tag
    def handle_endtag(self, tag):
        pass
        #print "Encountered an end tag :", tag
    def handle_data(self, data):
        clean_data = data.strip('\n\t\r ')
        clean_data = re.sub('[ \t\n]+', ' ', clean_data)
        if clean_data:
            #print clean_data
            self.day = lookup_day(clean_data) or self.day
            self.time = lookup_time(clean_data) or self.time
            self.lecturer = lookup_lecturer(clean_data) or self.lecturer
            if not (lookup_day(clean_data) or lookup_time(clean_data)):
                self.course = self.course or clean_data.split(' ')[0]
            self.weeks = lookup_weeks(clean_data) or self.weeks
            self.room = lookup_room(clean_data) or self.room
            self.group = lookup_group(clean_data) or self.group
            if self.weeks and self.room:
                row = [
                        self.day,
                        self.time,
                        self.room,
                        self.course,
                        self.group or '0',
                        self.lecturer,
                        self.weeks,
                        ]
                print ','.join(
                        ['"%s"' % unicode(p).replace('"', '""') for p in row]
                        )
                self._reset_lesson_related()
            #print lookup_day(clean_data), lookup_time(clean_data), lookup_lecturer(clean_data), lookup_weeks(clean_data), lookup_room(clean_data), lookup_group(clean_data)


parser = FESParser()
parser.init_timetable_vars()
parser.feed(codecs.open(sys.argv[1], 'r', 'utf-8').read())
