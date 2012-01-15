#-*- coding: utf-8 -*-

from optparse import OptionParser
import logging


logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;m:%(message)s', level=logging.INFO)

from django.core.management import setup_environ
from timetable_jan import settings

setup_environ(settings)
from timetable_jan.university.models import *



def main():
    parser = OptionParser()
    parser.add_option('-f', '--fcode', dest='from_major_code',
            help='from major code')
    parser.add_option('-y', '--fyear', dest='from_year',
            help='from year of study')
    parser.add_option('-t', '--tcode', dest='to_major_code',
            help='to major code')
    parser.add_option('-z', '--tyear', dest='to_year',
            help='to year of study')
    parser.add_option('-n', '--name', dest='name',
            help='course name')
    (options, args) = parser.parse_args()
    if not options.name or not options.from_major_code or not options.from_year \
            or not options.to_major_code or not options.to_year:
        parser.print_help()
        return
    print options
    timetable_from = Timetable.objects.get(year=int(options.from_year), major=Major.objects.get(code=options.from_major_code))
    timetable_to = Timetable.objects.get(year=int(options.to_year), major=Major.objects.get(code=options.to_major_code))
    course = timetable_from.courses.get(discipline__name=options.name)
    timetable_to.courses.add(course)

if __name__ == '__main__':
    main()
