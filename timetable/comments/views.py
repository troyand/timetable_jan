#-*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from timetable.university.models import Lesson
from timetable.comments.models import LessonComment

import datetime
from dateutil.tz import tzlocal


def get_lesson_comments(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related(), pk=lesson_id)
    comments = [] #get comments for lesson
    comments = [
            {
                'author': 'Alice',
                'comment': lesson.group.course.discipline.description or '<script>alert("oh")</script><b>a</b>',
                'added': datetime.datetime.now,
                },
            {
                'author': 'Bob',
                'comment': ''.join(reversed(lesson.group.course.discipline.description or '')),
                'added': datetime.datetime.now,
                },
            ]
    comments = LessonComment.objects.filter(lesson=lesson)
    return render_to_response(
        'lesson_comments_modal.html',
        {
            'lesson': lesson,
            'comments': comments,
        },
        context_instance=RequestContext(request)
    )

def post_lesson_comment(request, lesson_id):
    ip = request.META['REMOTE_ADDR']
    now = datetime.datetime.now(tzlocal())

    throttle_seconds = 0
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.user.is_authenticated():
        author = request.user
        try:
            last_comment = LessonComment.objects.filter(author=request.user).order_by('-added')[0]
            delta_seconds = (now - last_comment.added).total_seconds()
            throttle_seconds = 30 - delta_seconds
        except IndexError:
            pass
    else:
        author = None
        try:
            last_comment = LessonComment.objects.filter(ip=ip).order_by('-added')[0]
            delta_seconds = (now - last_comment.added).total_seconds()
            throttle_seconds = 300 - delta_seconds
        except IndexError:
            pass
    # flood-control
    if throttle_seconds > 0:
        return HttpResponseForbidden(u'Зачекайте %d сек. перед відправленням повідомлення' % int(throttle_seconds))
    comment = request.POST['new-post-text']
    if not comment:
        return HttpResponseForbidden(u'Порожній коментар')
    if len(comment) > 160:
        return HttpResponseForbidden(u'Довжина коментаря перевищує 160 символів')
    LessonComment.objects.create(
            lesson=lesson,
            author=author,
            ip=ip,
            added=now,
            comment=comment,
            )
    return HttpResponse('Ok')
