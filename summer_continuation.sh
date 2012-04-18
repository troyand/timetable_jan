#!/bin/bash

academic_term_id=`python summer_continuation.py`

echo $academic_term_id
# FLS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_1.csv -y 1 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_2.csv -y 2 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_3.csv -y 3 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_4.csv -y 4 -c 6.030401 -i -t $academic_term_id

# FSSST
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_sociology_1.csv -y 1 -c 6.030101 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_politology_1.csv -y 1 -c 6.030104 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_sociology_2.csv -y 2 -c 6.030101 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_socrob_2.csv -y 2 -c 6.130102 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_politology_2.csv -y 2 -c 6.030104 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_sociology_3.csv -y 3 -c 6.030101 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_socrob_3.csv -y 3 -c 6.130102 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_politology_3.csv -y 3 -c 6.030104 -i -t $academic_term_id

python add_courses.py -f 6.030104 -y 2 -t 6.030101 -z 1 -a $academic_term_id -n "Основи психології та педагогіки"
python add_courses.py -f 6.030104 -y 2 -t 6.030104 -z 1 -a $academic_term_id -n "Основи психології та педагогіки"
python add_courses.py -f 6.030401 -y 2 -t 6.030101 -z 2 -a $academic_term_id -n "Правові основи та етика паблик рілейшнз"
python add_courses.py -f 6.030104 -y 3 -t 6.030104 -z 2 -a $academic_term_id -n "Паблик рілейшнз у діяльності громадських організацій"
python add_courses.py -f 6.030104 -y 3 -t 6.030104 -z 2 -a $academic_term_id -n "Формування та розвиток персонального іміджу"
python add_courses.py -f 6.030104 -y 3 -t 6.030101 -z 3 -a $academic_term_id -n "Основи охорони праці"
python add_courses.py -f 6.030104 -y 3 -t 6.130102 -z 3 -a $academic_term_id -n "Основи охорони праці"
