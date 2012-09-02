#!/bin/bash

long_academic_term_id=`python autumn_2012.py long`
short_academic_term_id=`python autumn_2012.py short`

echo $long_academic_term_id
echo $short_academic_term_id

# FLS
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_1.csv -y 1 -c 6.030401 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_2.csv -y 2 -c 6.030401 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_3.csv -y 3 -c 6.030401 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_4.csv -y 4 -c 6.030401 -i -t $short_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_5.csv -y 1 -c 7.03040201 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_6.csv -y 1 -c 8.03040201 -i -t $long_academic_term_id

# FI
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_1.csv -y 1 -c 6.050103 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_2.csv -y 2 -c 6.050103 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_3.csv -y 3 -c 6.050103 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_4.csv -y 4 -c 6.050103 -i -t $short_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_5.csv -y 1 -c 7.05010101 -i -t $long_academic_term_id
#
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_1.csv -y 1 -c 6.040301 -i -t $long_academic_term_id
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Англійська мова" -a 4
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Застосування принципів Болонського процесу в НаУКМА" -a 4
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Українська мова" -a 4
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_2.csv -y 2 -c 6.040301 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_3.csv -y 3 -c 6.040301 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_4.csv -y 4 -c 6.040301 -i -t $short_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_mathm_1.csv -y 1 -c 8.04030101 -i -t $long_academic_term_id
#
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_iust_1.csv -y 1 -c 8.05010101 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_iust_2.csv -y 2 -c 8.05010101 -i -t $long_academic_term_id
#
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_smpr_1.csv -y 1 -c 8.04030302 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_smpr_2.csv -y 2 -c 8.04030302 -i -t $long_academic_term_id
#
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_pzas_1.csv -y 1 -c 8.05010301 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_pzas_2.csv -y 1 -c 8.05010301 -i -t $long_academic_term_id
#python import_timetable.py -f timetable/unified_docs/2012_2013_osin_pzas_3.csv -y 1 -c 8.05010301 -i -t $short_academic_term_id
#
