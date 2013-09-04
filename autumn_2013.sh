#!/bin/bash

academic_term_id=`python autumn_2012.py`


# FLS
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_1.csv -y 1 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_2.csv -y 2 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_3.csv -y 3 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_4.csv -y 4 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_5.csv -y 1 -c 7.03040201 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_6.csv -y 1 -c 8.03040201 -i -t $academic_term_id
