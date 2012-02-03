#!/bin/bash

if [ ! -f timetable_jan/settings_local.py ]
then
    echo "Copying timetable_jan/settings_local.sample to timetable_jan/settings_local.py"
    cp timetable_jan/settings_local.sample timetable_jan/settings_local.py
fi

if [ ! -d venv_dir ]
then
    echo "Creating virtualenv"
    virtualenv --no-site-packages venv_dir
fi

source venv_dir/bin/activate

export PIP_DOWNLOAD_CACHE=/tmp/

pip install -r requirements.txt

if [ -f timetable_jan/db.sqlite ]
then
    echo "Backing up existing sqlite DB to timetable_jan/db.sqlite.backup"
    mv timetable_jan/db.sqlite timetable_jan/db.sqlite.backup
fi

python manage.py syncdb --noinput


# FLS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_1.csv -y 1 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_2.csv -y 2 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_3.csv -y 3 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_4.csv -y 4 -c 6.030401 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_5.csv -y 1 -c 7.03040201 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_fls_6.csv -y 1 -c 8.03040201 -i


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


# FSSST
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_sociology_1.csv -y 1 -c 6.030101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_politology_1.csv -y 1 -c 6.030104 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_sociology_2.csv -y 2 -c 6.030101 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_socrob_2.csv -y 2 -c 6.130102 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_politology_2.csv -y 2 -c 6.030104 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_politology_3.csv -y 3 -c 6.030104 -i

# foreign courses
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Логіка"
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Історія української культури"
python add_courses.py -f 6.030101 -y 1 -t 6.030104 -z 1 -n "Безпека життєдіяльності"
python add_courses.py -f 6.030101 -y 2 -t 6.130102 -z 2 -n "Українська мова (за професійним спрямуванням)"
python add_courses.py -f 6.030101 -y 2 -t 6.030104 -z 2 -n "Українська мова (за професійним спрямуванням)"
python add_courses.py -f 6.030101 -y 1 -t 6.130102 -z 2 -n "Політологія-1"
python add_courses.py -f 6.130102 -y 2 -t 6.030104 -z 2 -n "Основи права"

# FHS
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_history_1.csv -y 1 -c 6.020302 -i

# FPrN
# year 1
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_biology_1.csv -y 1 -c 6.040102 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_ecology_1.csv -y 1 -c 6.040106 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_physics_1.csv -y 1 -c 6.040203 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_chemistry_1.csv -y 1 -c 6.040101 -i

# foreign courses
python add_courses.py -f 6.040102 -y 1 -t 6.040106 -z 1 -n "Неорганічна хімія"
python add_courses.py -f 6.040102 -y 1 -t 6.040106 -z 1 -n "Основи загальної екології"
python add_courses.py -f 6.040102 -y 1 -t 6.040106 -z 1 -n "Вища математика-2"
python add_courses.py -f 6.040102 -y 1 -t 6.040203 -z 1 -n "Основи загальної екології"
python add_courses.py -f 6.040102 -y 1 -t 6.040101 -z 1 -n "Основи загальної екології"
python add_courses.py -f 6.040102 -y 1 -t 6.040101 -z 1 -n "Вища математика-2"
python add_courses.py -f 6.040102 -y 1 -t 6.040101 -z 1 -n "Загальна фізика"
python add_courses.py -f 6.040102 -y 1 -t 6.040101 -z 1 -n "Практикум з загальної фізики"
python add_courses.py -f 6.040203 -y 1 -t 6.040101 -z 1 -n "Вступ до загальної біології"

# year 2
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_biology_2.csv -y 2 -c 6.040102 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_ecology_2.csv -y 2 -c 6.040106 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_physics_2.csv -y 2 -c 6.040203 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_chemistry_2.csv -y 2 -c 6.040101 -i

# foreign courses
python add_courses.py -f 6.040102 -y 2 -t 6.040106 -z 2 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"
python add_courses.py -f 6.040102 -y 2 -t 6.040203 -z 2 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"
python add_courses.py -f 6.040106 -y 2 -t 6.040203 -z 2 -n "Українська мова за професійним спрямуванням"
python add_courses.py -f 6.040102 -y 2 -t 6.040101 -z 2 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"

# year 3
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_biology_3.csv -y 3 -c 6.040102 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_ecology_3.csv -y 3 -c 6.040106 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_physics_3.csv -y 3 -c 6.040203 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_chemistry_3.csv -y 3 -c 6.040101 -i

# foreign courses
python add_courses.py -f 6.040102 -y 2 -t 6.040102 -z 3 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"
python add_courses.py -f 6.040102 -y 2 -t 6.040106 -z 3 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"
python add_courses.py -f 6.040102 -y 2 -t 6.040203 -z 3 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"
python add_courses.py -f 6.040102 -y 2 -t 6.040101 -z 3 -n "Історія Часу та Всесвіту:елементи сучасної космогонії та космології"
python add_courses.py -f 6.040102 -y 3 -t 6.040106 -z 3 -n "Соціологія"
python add_courses.py -f 6.040102 -y 3 -t 6.040203 -z 3 -n "Соціологія"
python add_courses.py -f 6.040102 -y 3 -t 6.040101 -z 3 -n "Соціологія"

# year 4
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_biology_4.csv -y 4 -c 6.040102 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_ecology_4.csv -y 4 -c 6.040106 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_physics_4.csv -y 4 -c 6.040203 -i
python import_timetable.py -f timetable_jan/unified_docs/2011_2012_vesna_chemistry_4.csv -y 4 -c 6.040101 -i
