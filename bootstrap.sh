#!/bin/bash
rm timetable_jan/db.sqlite
python manage.py syncdb --noinput

# FCSS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_cs_1.csv -y 1 -c 6.050103 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_cs_2.csv -y 2 -c 6.050103 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_cs_3.csv -y 3 -c 6.050103 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_cs_4.csv -y 4 -c 6.050103 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_math_1.csv -y 1 -c 6.040301 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_math_2.csv -y 2 -c 6.040301 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_math_3.csv -y 3 -c 6.040301 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_math_4.csv -y 4 -c 6.040301 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_cs_5.csv -y 1 -c 7.05010101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_iust_1.csv -y 1 -c 8.05010101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_ispr_1.csv -y 1 -c 8.04030302 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_pzas_1.csv -y 1 -c 8.05010203 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_iust_2.csv -y 2 -c 8.05010101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_ispr_2.csv -y 2 -c 8.04030302 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_pzas_2.csv -y 2 -c 8.05010203 -i

# FLS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_1.csv -y 1 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_2.csv -y 2 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_3.csv -y 3 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_4.csv -y 4 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_5.csv -y 1 -c 7.03040201 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_6.csv -y 1 -c 8.03040201 -i
