from django.core.management import setup_environ
from timetable_jan import settings

setup_environ(settings)

from timetable_jan.university.models import *
from timetable_jan.audit.models import *
Building.objects.all()
b=Building.objects.all()[0]
print b
b.label='TEST'
user=User.objects.all()[0]
b.save(owner=user, changer=user)
c=Change.objects.get()
print c.unified_diff()

print c.content_object

print b.changes()

b2=Building()
b2.university=b.university
b2.number=222
b2.label='TEST'
b2.save(changer=user, owner=user)

o=Ownership.objects.get()
print o.owner
