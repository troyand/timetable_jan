#!/bin/bash

academic_term_id=`python summer_continuation.py`

echo $academic_term_id
# FLS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_1.csv -y 1 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_2.csv -y 2 -c 6.030401 -i -t $academic_term_id
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_lito_fls_3.csv -y 3 -c 6.030401 -i -t $academic_term_id

