#!/bin/bash

# FLS
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_fls_1.csv -g 'Право - бакалавр - 1' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_fls_2.csv -g 'Право - бакалавр - 2' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_fls_3.csv -g 'Право - бакалавр - 3' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_fls_4.csv -g 'Право - бакалавр - 4' -i

# FSSST
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_sociology_1.csv -g 'Соціологія - бакалавр - 1' -i
#python import_timetable.py -f timetable/unified_docs/2011_2012_lito_politology_1.csv -g 'Політологія - бакалавр - 1' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_sociology_2.csv -g 'Соціологія - бакалавр - 2' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_socrob_2.csv -g 'Соціальна робота - бакалавр - 2' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_politology_2.csv -g 'Політологія - бакалавр - 2' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_sociology_3.csv -g 'Соціологія - бакалавр - 3' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_socrob_3.csv -g 'Соціальна робота - бакалавр - 3' -i
python import_timetable.py -f timetable/unified_docs/2011_2012_lito_politology_3.csv -g 'Політологія - бакалавр - 3' -i
