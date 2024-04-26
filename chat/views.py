from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


@login_required
def course_chat_room(request, course_id):
    """Представления чата"""
    try:
        course = request.user.courses_joined.get(id=course_id)
    except:
        # если курс не существует или пользователь не подписан на курсы
        return HttpResponseForbidden()  # 403
    return render(request, 'chat/room.html', {'course': course})
