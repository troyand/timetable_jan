#!/bin/bash

academic_term_id=`python summer_continuation_2013.py`

echo $academic_term_id
# FLS
python import_timetable.py -f timetable/unified_docs/2012_2013_lito_fls_1.csv -y 1 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_lito_fls_2.csv -y 2 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_lito_fls_3.csv -y 3 -c 6.030401 -i -t $academic_term_id
