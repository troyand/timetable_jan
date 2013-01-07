# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import re
import codecs

def lookup_lecturer(s):
    try:
        lecturer = re.findall(u'(cт\. в\.|ст\.\s?в\.|ст\.\s?викл\.|доц\.|проф\.|ас\.)([^.]*\.[^.]*\.)', s)[0][1]
        lecturer = re.sub('[\t\n]+', ' ', lecturer)
        lecturer = lecturer.replace('.', '. ')
        lecturer = re.sub('[ ]+', ' ', lecturer)
        lecturer = lecturer.lstrip('~ ')
    except IndexError:
        lecturer = ''
    return lecturer

def lookup_lecturer_2(s):
    caps = u'А-ЯІЇЄҐ'
    try:
        lecturer_parts = re.findall(
                u'([%s]\.)([%s].)(\w+)' % (caps, caps), s, re.UNICODE)[0]
        lecturer = u' '.join([lecturer_parts[2], lecturer_parts[0], lecturer_parts[1]])
    except IndexError:
        lecturer = ''
    return lecturer.replace(u'~', u'')

def lookup_weeks(s):
    try:
        weeks = re.findall(u'([0-9, \t-]+)т', s)[0]
        weeks = filter(lambda x: x not in ' \t', weeks)
    except IndexError:
        weeks = ''
    return weeks

def lookup_room(s):
    try:
        room = re.findall(u'(\d+-\w+)', s, re.UNICODE)[0]
    except:
        room = ''
    return room

def lookup_course(s):
    try:
        course = re.findall(u'([^(]*)', s, re.UNICODE)[0]
    except:
        course = ''
    return course.strip()

def lookup_course_2(s):
    try:
        course = s.split(u'      ')[0]
    except:
        course = ''
    course = re.sub(u'[ ]+', ' ', course)
    return course.strip().replace(u'~', u'')

def lookup_day(s):
    mapping = {
            u'ПОНЕДІЛОК': u'ПН',
            u'ВІВТОРОК': u'ВТ',
            u'СЕРЕДА': u'СР',
            u'ЧЕТВЕР': u'ЧТ',
            u'П’ЯТНИЦЯ': u'ПТ',
            u'СУБОТА': u'СБ',
            }
    for k, v in mapping.items():
        if k in s:
            return v
    return u'ПН'

def lookup_time(s):
    mapping = {
            u'8:30': u'08:30-09:50', 
            u'10:00': u'10:00-11:20', 
            u'11:40': u'11:40-13:00', 
            u'13:30': u'13:30-14:50', 
            u'15:00': u'15:00-16:20', 
            u'16:30': u'16:30-17:50', 
            u'18:00': u'18:00-19:20'
            }
    for k, v in mapping.items():
        if k in s:
            return v


def parse(filename):
    soup = BeautifulSoup(open(filename).read())
    file_basename = filename.split('.')[0]
    for table_index, table in enumerate(soup.findAll('table')):
        csv_file = codecs.open('%s_%d.csv' % (file_basename, table_index), 'w', 'utf-8')
        spanned_content = []
        for tr in table.findAll('tr'):
            result_row = []
            td_items = tr.findAll('td')
            td_items_iter = iter(td_items)
            if spanned_content == []:
                # not initialized yet - first row
                for i in range(len(td_items)):
                    spanned_content.append([])
            day = None
            time = None
            lecturer = None
            course = None
            weeks = None
            room = None
            group = None
            try:
                for i, spanned_items_list in enumerate(spanned_content):
                    try:
                        # first try to add possible spanned item
                        td = spanned_items_list.pop(0)
                    except IndexError:
                        # else add the next item from td
                        # and if necessary update spanned_items_list
                        td = td_items_iter.next()
                        try:
                            for j in range(int(td['rowspan']) - 1):
                                spanned_items_list.append(td)
                        except KeyError:
                            pass
                    td_text_elements = td.findAll(text=True)
                    td_text_contents = reduce(
                            lambda x, y: x.replace('\n', '').replace('\t', ' ') + '~' + y, td_text_elements)
                    if i == 0:
                        day = lookup_day(td_text_contents)
                    elif i == 1:
                        time = lookup_time(td_text_contents)
                    elif i == 2:
                        print td_text_contents
                        lecturer = lookup_lecturer_2(td_text_contents)
                        weeks = lookup_weeks(td_text_contents)
                        try:
                            course_text = td.findAll('b')[0].findAll(text=True)[0]
                            course_text = course_text.replace('\n', ' ').replace('\t', ' ')
                            course_text = re.sub('[ ]+', ' ', course_text)
                            course = lookup_course(course_text)
                        except:
                            course = ''
                        course = lookup_course_2(td_text_contents)
                        if u'(л)' in td_text_contents:
                            group = '0'
                        else:
                            try:
                                group = re.findall(u'(\d)гр.', td_text_contents)[0]
                            except IndexError:
                                group = ''
                    elif i == 3:
                        room = lookup_room(td_text_contents)
                    result_row.append(td_text_contents)
                row = [day, time, room, course, group, lecturer, weeks]
                print >> csv_file,','.join(
                        ['"%s"' % p.replace('"', '""') for p in row]
                        )
            except StopIteration:
                print 'StopIteration'
        csv_file.close()

                    

        #print table


if __name__ == '__main__':
    parse('fsnst3.html')
