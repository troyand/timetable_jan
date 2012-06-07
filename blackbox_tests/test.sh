#!/bin/bash

if [ -f timetable/db.sqlite ]
then
    echo "Backing up existing sqlite DB to timetable/db.sqlite.orig"
    mv timetable/db.sqlite timetable/db.sqlite.orig
fi

python manage.py syncdb --noinput
python manage.py migrate university --noinput

python manage.py loaddata timetable/university/fixtures/test_timetable_dataset.xml

python manage.py runserver &

server_pid=$!

python blackbox_tests/screenshots.py

echo "Killing server (PID $server_pid)"
kill $server_pid

if [ -f timetable/db.sqlite.orig ]
then
    echo "Restoring sqlite DB from timetable/db.sqlite.orig"
    mv timetable/db.sqlite.orig timetable/db.sqlite
fi
