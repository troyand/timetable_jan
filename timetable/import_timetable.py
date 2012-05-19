import csv
import codecs
import getopt
import logging
import sys


from django.core.management import setup_environ
from timetable import settings

setup_environ(settings)
from timetable.university.models import *

def main():
    logging.log(University.objects.all())

if __name__ == '__main__':
    main()
