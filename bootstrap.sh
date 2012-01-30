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

# foreign courses
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Англійська мова"
python add_courses.py -f 6.050103 -y 1 -t 6.040301 -z 1 -n "Екологія"
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Англійська мова"
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Об’єктно-орієнтоване програмування"
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Історія України"
python add_courses.py -f 6.050103 -y 2 -t 6.040301 -z 2 -n "Українська мова (за професійним спрямуванням)"
python add_courses.py -f 7.05010101 -y 1 -t 8.05010101 -z 2 -n "Цивільний захист"
python add_courses.py -f 7.05010101 -y 1 -t 8.04030302 -z 2 -n "Цивільний захист"
python add_courses.py -f 7.05010101 -y 1 -t 8.05010203 -z 2 -n "Цивільний захист"
python add_courses.py -f 8.05010101 -y 1 -t 7.05010101 -z 1 -n "Інформаційні системи та структури даних"
python add_courses.py -f 8.05010101 -y 1 -t 7.05010101 -z 1 -n "Побудова масштабованих мереж"
python add_courses.py -f 8.05010101 -y 1 -t 7.05010101 -z 1 -n "Розподілені операційні системи"
python add_courses.py -f 8.05010101 -y 1 -t 8.04030302 -z 1 -n "Англійська мова"
python add_courses.py -f 8.05010101 -y 1 -t 8.04030302 -z 1 -n "Інформаційні системи та структури даних"
python add_courses.py -f 8.05010101 -y 1 -t 8.05010203 -z 1 -n "Англійська мова"
python add_courses.py -f 8.05010101 -y 2 -t 8.04030302 -z 2 -n "Декларативне програмування та розробка баз знань"

# FLS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_1.csv -y 1 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_2.csv -y 2 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_3.csv -y 3 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_4.csv -y 4 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_5.csv -y 1 -c 7.03040201 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_6.csv -y 1 -c 8.03040201 -i

# FSSST
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_sociology_1.csv -y 1 -c 6.030101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_politology_1.csv -y 1 -c 6.030104 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_sociology_2.csv -y 2 -c 6.030101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_socrob_2.csv -y 2 -c 6.130102 -i
#python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_politology_2.csv -y 2 -c 6.030104 -i

# foreign courses
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Логіка"
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Історія української культури"
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Безпека життєдіяльності"
python add_courses.py -f 6.030101 -y 2 -t 6.130102 -z 2 -n "Українська мова (за професійним спрямуванням)"
python add_courses.py -f 6.030101 -y 1 -t 6.130102 -z 2 -n "Політологія-1"
