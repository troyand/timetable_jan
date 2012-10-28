#!/bin/bash

long_academic_term_id=`python autumn_2012.py long`
short_academic_term_id=`python autumn_2012.py short`

echo $long_academic_term_id
echo $short_academic_term_id

# FLS
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_1.csv -y 1 -c 6.030401 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_2.csv -y 2 -c 6.030401 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_3.csv -y 3 -c 6.030401 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_4.csv -y 4 -c 6.030401 -i -t $short_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_5.csv -y 1 -c 7.03040201 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fls_6.csv -y 1 -c 8.03040201 -i -t $long_academic_term_id

# FI
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_1.csv -y 1 -c 6.050103 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_2.csv -y 2 -c 6.050103 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_3.csv -y 3 -c 6.050103 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_4.csv -y 4 -c 6.050103 -i -t $short_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_cs_5.csv -y 1 -c 7.05010101 -i -t $long_academic_term_id

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_1.csv -y 1 -c 6.040301 -i -t $long_academic_term_id
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Англійська мова" -a 5
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Застосування принципів Болонського процесу в НаУКМА" -a 5
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Українська мова" -a 5
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_2.csv -y 2 -c 6.040301 -i -t $long_academic_term_id
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Українська мова (за професійним спрямуванням)" -a 5
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Англійська мова" -a 5
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Процедурне програмування (на базі Сі/Сі++)" -a 5
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Основи економічної теорії" -a 5
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_3.csv -y 3 -c 6.040301 -i -t $long_academic_term_id
python add_courses.py -f 6.050103 -y 3 -t 6.040301 -z 3 -n "Філософія" -a 5
python add_courses.py -f 6.050103 -y 3 -t 6.040301 -z 3 -n "Основи охорони праці" -a 5
python add_courses.py -f 6.050103 -y 3 -t 6.040301 -z 3 -n "Безпека життєдіяльності" -a 5
python add_courses.py -f 6.050103 -y 3 -t 6.040301 -z 3 -n "Політологія" -a 5
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_math_4.csv -y 4 -c 6.040301 -i -t $short_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_mathm_1.csv -y 1 -c 8.04030101 -i -t $long_academic_term_id

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_iust_1.csv -y 1 -c 8.05010101 -i -t $long_academic_term_id
python add_courses.py -f 7.05010101 -y 1 -t 8.05010101 -z 1 -n "Прикладне програмування" -a 5
python add_courses.py -f 7.05010101 -y 1 -t 8.05010101 -z 1 -n "Основи системного аналізу об’єктів і процесів комп’ютеризації" -a 5
python add_courses.py -f 7.05010101 -y 1 -t 8.05010101 -z 1 -n "Архітектура інформаційних управляючих систем" -a 5
python add_courses.py -f 7.05010101 -y 1 -t 8.05010101 -z 1 -n "Теорія прийняття рішень та керування-2" -a 5
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_iust_2.csv -y 2 -c 8.05010101 -i -t $long_academic_term_id

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_smpr_1.csv -y 1 -c 8.04030302 -i -t $long_academic_term_id
python add_courses.py -f 8.05010101 -y 1 -t 8.04030302 -z 1 -n "Англійська мова" -a 5
python add_courses.py -f 7.05010101 -y 1 -t 8.04030302 -z 1 -n "Основи системного аналізу об’єктів і процесів комп’ютеризації" -a 5
python add_courses.py -f 7.05010101 -y 1 -t 8.04030302 -z 1 -n "Теорія прийняття рішень та керування-2" -a 5
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_smpr_2.csv -y 2 -c 8.04030302 -i -t $long_academic_term_id
python add_courses.py -f 8.05010101 -y 2 -t 8.04030302 -z 2 -n "Філософія (поглиблений курс)" -a 5

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_pzas_1.csv -y 1 -c 8.05010203 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_pzas_2.csv -y 2 -c 8.05010203 -i -t $long_academic_term_id
python add_courses.py -f 8.05010101 -y 2 -t 8.05010203 -z 2 -n "Філософія (поглиблений курс)" -a 5
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_pzas_3.csv -y 3 -c 8.05010203 -i -t $short_academic_term_id

# FES
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_fes_4.csv -y 4 -c 6.030501 -i -t $long_academic_term_id

# FSSST
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_sociology_1.csv -y 1 -c 6.030101 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_politology_1.csv -y 1 -c 6.030104 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_socrob_1.csv -y 1 -c 6.130102 -i -t $long_academic_term_id

python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Філософія" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 1 -t 6.130102 -z 1 -n "Філософія" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Історія України" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 1 -t 6.130102 -z 1 -n "Історія України" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Українська мова" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 1 -t 6.130102 -z 1 -n "Українська мова" -a $long_academic_term_id
python add_courses.py -f 6.030104 -y 1 -t 6.130102 -z 1 -n "Інформатика-1" -a $long_academic_term_id

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_sociology_2.csv -y 2 -c 6.030101 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_politology_2.csv -y 2 -c 6.030104 -i -t $long_academic_term_id
python add_courses.py -f 6.030101 -y 2 -t 6.030104 -z 2 -n "Українська мова (за професійним спрямуванням)" -a $long_academic_term_id

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_sociology_3.csv -y 3 -c 6.030101 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_politology_3.csv -y 3 -c 6.030104 -i -t $long_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_socrob_3.csv -y 3 -c 6.130102 -i -t $long_academic_term_id
python add_courses.py -f 6.030101 -y 3 -t 6.130102 -z 3 -n "Психологія управління" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 3 -t 6.030104 -z 3 -n "Загальна психологія" -a $long_academic_term_id
python add_courses.py -f 6.030101 -y 3 -t 6.130102 -z 3 -n "Загальна психологія" -a $long_academic_term_id

python import_timetable.py -f timetable/unified_docs/2012_2013_osin_sociology_4.csv -y 4 -c 6.030101 -i -t $short_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_politology_4.csv -y 4 -c 6.030104 -i -t $short_academic_term_id
python import_timetable.py -f timetable/unified_docs/2012_2013_osin_socrob_4.csv -y 4 -c 6.130102 -i -t $short_academic_term_id
