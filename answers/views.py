from django.contrib import messages
from django.contrib.auth.models import User
from django.http import *
from django.shortcuts import render, redirect

from project.settings import LOGIN_URL
from questions.models import Question
from .forms import AnswerForm
from .models import Answer


def answers_thread(request, id, slug=None):
    question = Question.objects.filter(slug=slug).first()
    answer = Answer.objects.filter(id=id).first()
    comment_form = AnswerForm(request.POST or None)

    if not answer.is_parent:
        answer = answer.parent

    if request.method == 'POST':

        user = User.objects.filter(id=request.user.id).first()

        if user is None or user.is_authenticated == False:
            messages.error(request, 'Please Login before you perform this action')
            return redirect('%s?next=%s' % (LOGIN_URL, request.path))

        if not user.has_perm('answers.add_answer'):
            messages.error(request, 'You have no permission to add replies. Please contact your admin.')
            return redirect('%s?next=%s' % (LOGIN_URL, request.path))

        if comment_form.is_valid():
            reply = comment_form.save(commit=False)
            reply.user = request.user
            reply.question = question
            try:
                parent_id = answer.id
            except:
                parent_id = None
            if parent_id:
                parent_qs = Answer.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    reply.parent = parent_qs.first()
                    reply.save()
                    messages.success(request, 'Reply added.')
                    return redirect(answer.get_absolute_url())
                else:
                    return HttpResponse(f'Multiple Answers with id: {parent_id}', status=500)
            else:
                messages.error(request, 'Failed to add reply.')
        else:
            messages.error(request, 'Failed to add reply.')

    context = {
        'title': answer.content,
        'answer': answer,
        'comment_form': comment_form,
    }

    return render(request, 'answer_detail.html', context)


def answers_delete(request, id, slug=None):

    user = User.objects.filter(id=request.user.id).first()

    if user is None or user.is_authenticated == False:
        messages.error(request, 'Please Login before you perform this action')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    if not user.has_perm('answers.delete_answer'):
        messages.error(request, 'You have no permission to delete answers. Please contact your admin.')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    answer = Answer.objects.filter(id=id).first()

    if answer.user.id != request.user.id:
        messages.error(request, 'This is not your answer')
        url = request.path
        if answer.parent is None:
            url = answer.question.get_absolute_url()
        else:
            url = answer.parent.get_absolute_url()
        return redirect(url)

    if request.method == "POST":
        if answer.user.id == request.user.id:
            if answer.question.slug == slug:
                if answer.parent is None:
                    messages.success(request, 'Answer deleted.')
                    url = answer.question.get_absolute_url()
                    answer.delete()
                    return redirect(url)
                else:
                    messages.success(request, 'Reply deleted.')
                    url = answer.parent.get_absolute_url()
                    answer.delete()
                    return redirect(url)
            else:
                messages.error(request, 'This answer is not for this question')
                return redirect('%s' % request.path)
        else:
            messages.error(request, 'This is not your answer')
            return redirect('%s' % request.path)

    context = {
        'title': answer.content + ' | Delete ',
        'object': answer,
        'url': request.META.get('HTTP_REFERER'),
    }

    return render(request, "confirm_delete.html", content_type='text/html', context=context)
