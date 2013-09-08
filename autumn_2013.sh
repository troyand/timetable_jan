#!/bin/bash

academic_term_id=`python autumn_2013.py`


# FLS
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_1.csv -y 1 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_2.csv -y 2 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_3.csv -y 3 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_4.csv -y 4 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_5.csv -y 1 -c 7.03040201 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_fls_6.csv -y 1 -c 8.03040201 -i -t $academic_term_id

# FI
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_cs_1.csv -y 1 -c 6.050103 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_math_1.csv -y 1 -c 6.040301 -i -t $academic_term_id
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Англійська мова" -a $academic_term_id
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Застосування принципів Болонського процесу в НаУКМА" -a $academic_term_id
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Українська мова" -a $academic_term_id

python import_timetable.py -f timetable/unified_docs/2013_2014_osin_cs_2.csv -y 2 -c 6.050103 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_math_2.csv -y 2 -c 6.040301 -i -t $academic_term_id
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Англійська мова" -a $academic_term_id
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Українська мова (за професійним спрямуванням)" -a $academic_term_id
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Процедурне програмування (на базі Сі/Сі++)" -a $academic_term_id

python import_timetable.py -f timetable/unified_docs/2013_2014_osin_cs_3.csv -y 3 -c 6.050103 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_math_3.csv -y 3 -c 6.040301 -i -t $academic_term_id
python add_courses.py -f 6.050103 -y 3 -t 6.040301 -z 3 -n "Безпека життєдіяльності" -a $academic_term_id
python add_courses.py -f 6.050103 -y 3 -t 6.040301 -z 3 -n "Філософія" -a $academic_term_id

python import_timetable.py -f timetable/unified_docs/2013_2014_osin_cs_4.csv -y 4 -c 6.050103 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2013_2014_osin_math_4.csv -y 4 -c 6.040301 -i -t $academic_term_id

python import_timetable.py -f timetable/unified_docs/2013_2014_osin_cs_5.csv -y 1 -c 7.05010101 -i -t $academic_term_id
