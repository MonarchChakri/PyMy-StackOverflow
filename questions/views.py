import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import *
from django.shortcuts import render, redirect

from answers.forms import AnswerForm
from answers.models import Answer
from project import settings
from project.settings import LOGIN_URL
from .forms import QuestionForm
from .models import Question


def questions_create(request):
    user = User.objects.filter(id=request.user.id).first()

    if user is None or user.is_authenticated == False:
        messages.error(request, 'Please Login before you perform this action')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    if not user.has_perm('questions.add_question'):
        messages.error(request, 'You have no permission to create questions. Please contact your admin.')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    form = QuestionForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.reputation_str = ','.join(set(map(str, question.reputation_set))) + ','
            question.save()
            messages.success(request, question.title + ' created.')
            return redirect("questions:questions")
        else:
            messages.error(request, 'Failed to create.')

    context = {
        'title': 'Create Question',
        'form': form,
        'type': 'Ask Question',
    }
    return render(request, 'question_create.html', context)


def questions_detail(request, slug=None):
    question = Question.objects.filter(slug=slug).first()

    if not question:
        raise Http404

    try:
        for u_id in question.reputation_str.split(','):
            if int(u_id) > 0:
                question.reputation_count += 1
            elif int(u_id) < 0:
                question.reputation_count -= 1
            question.reputation_set.add(int(u_id))
    except:
        pass

    answers = question.answers
    answer_form = AnswerForm(request.POST or None)

    if request.method == 'POST':

        user = User.objects.filter(id=request.user.id).first()

        if user is None or user.is_authenticated == False:
            messages.error(request, 'Please Login before you perform this action')
            return redirect('%s?next=%s' % (LOGIN_URL, request.path))

        if not user.has_perm('answers.add_answer'):
            messages.error(request, 'You have no permission to add answers. Please contact your admin.')
            return redirect('%s?next=%s' % (LOGIN_URL, request.path))

        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.user = request.user
            answer.question = question

            try:
                parent_id = int(request.POST.get('parent_id', None))
            except:
                parent_id = None
            if parent_id:
                parent_qs = Answer.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    answer.parent = parent_qs.first()
                    answer.save()
                    messages.success(request, 'Reply added.')
                    return redirect(question.get_absolute_url())
                else:
                    return HttpResponse(f'Multiple Answers with id: {parent_id}', status=500)

            answer.save()
            messages.success(request, 'Answer added.')
            return redirect(question.get_absolute_url())
        else:
            messages.error(request, 'Failed to add answer.')

    context = {
        'title': question.title,
        'question': question,
        'answers': answers,
        'answer_form': answer_form,
    }

    return render(request, 'question_detail.html', context)


def questions_list(request):
    question_list = Question.objects.all()

    query = request.GET.get("q")
    if query:
        question_list = question_list.filter(
            Q(title__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()

    try:
        for question in question_list:
            for u_id in question.reputation_str.split(','):
                if int(u_id) > 0:
                    question.reputation_count += 1
                elif int(u_id) < 0:
                    question.reputation_count -= 1
                question.reputation_set.add(int(u_id))
    except:
        pass

    question_list = sorted(question_list, key=lambda question: question.reputation_count, reverse=True)

    paginator = Paginator(question_list, 5)
    page = request.GET.get('page')
    question_page = paginator.get_page(page)

    context = {
        'title': 'List Questions',
        'question_list': question_page,
    }

    return render(request, 'question_index.html', context)


def questions_update(request, slug=None):
    user = User.objects.filter(id=request.user.id).first()

    if user is None or user.is_authenticated == False:
        messages.error(request, 'Please Login before you perform this action')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    if not user.has_perm('questions.change_question'):
        messages.error(request, 'You have no permission to change questions. Please contact your admin.')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    question = Question.objects.filter(slug=slug).first()

    try:
        for u_id in question.reputation_str.split(','):
            if int(u_id) > 0:
                question.reputation_count += 1
            elif int(u_id) < 0:
                question.reputation_count -= 1
            question.reputation_set.add(int(u_id))
    except:
        pass

    form = QuestionForm(request.POST or None, request.FILES or None, instance=question)

    if question.user.id == request.user.id:
        if request.method == 'POST':
            if form.is_valid():
                question = form.save(commit=False)
                question.reputation_str = ','.join(set(map(str, question.reputation_set))) + ','
                question.user = request.user
                question.save()
                messages.success(request, question.title + ' updated.')
                return HttpResponseRedirect(question.get_absolute_url())
            else:
                messages.error(request, 'Failed to update.')
    else:
        return HttpResponse('This is not your question', status=403)

    context = {
        'title': question.title + ' | Update',
        'question': question,
        'form': form,
        'type': 'Update Question',
    }
    return render(request, 'question_create.html', context)


def questions_delete(request, slug=None):
    user = User.objects.filter(id=request.user.id).first()

    if user is None or user.is_authenticated == False:
        messages.error(request, 'Please Login before you perform this action')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    if not user.has_perm('questions.delete_question'):
        messages.error(request, 'You have no permission to delete questions. Please contact your admin.')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    question = Question.objects.filter(slug=slug).first()

    if request.method == "POST":
        if question.user.id == request.user.id:
            import os

            try:
                os.remove(settings.MEDIA_URL + question.image.url[6:])
                os.remove(settings.MEDIA_ROOT + question.image.url[6:])
            except:
                pass

            question.delete()
            messages.success(request, question.title + ' deleted.')
            return redirect("questions:questions")
        else:
            messages.error(request, 'This is not your question')
            return redirect('%s' % request.path)

    context = {
        'title': question.content + ' | Delete ',
        'object': question,
        'url': request.META.get('HTTP_REFERER'),
    }

    return render(request, "confirm_delete.html", content_type='text/html', context=context)


def questions_upvote(request, slug=None):
    user = User.objects.filter(id=request.user.id).first()

    if user is None or user.is_authenticated == False:
        messages.error(request, 'Please Login before you perform this action')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    question = Question.objects.filter(slug=slug).first()

    try:
        for u_id in question.reputation_str.split(','):
            if int(u_id) > 0:
                question.reputation_count += 1
            elif int(u_id) < 0:
                question.reputation_count -= 1
            question.reputation_set.add(int(u_id))
    except:
        pass

    print(question.reputation_set)

    if question.user.id != request.user.id:
        if request.user.id not in question.reputation_set and -request.user.id not in question.reputation_set:
            question.reputation_set.add(request.user.id)
            question.reputation_str = ','.join(set(map(str, question.reputation_set))) + ','
            question.save()
            messages.success(request, 'Votes updated.')
            return HttpResponseRedirect(question.get_absolute_url())
        else:
            messages.success(request, 'Already voted.')
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        messages.error(request, "This is your question can't vote")
        return HttpResponseRedirect(question.get_absolute_url())


def questions_downvote(request, slug=None):
    user = User.objects.filter(id=request.user.id).first()

    if user is None or user.is_authenticated == False:
        messages.error(request, 'Please Login before you perform this action')
        return redirect('%s?next=%s' % (LOGIN_URL, request.path))

    question = Question.objects.filter(slug=slug).first()

    try:
        for u_id in question.reputation_str.split(','):
            if int(u_id) > 0:
                question.reputation_count += 1
            elif int(u_id) < 0:
                question.reputation_count -= 1
            question.reputation_set.add(int(u_id))
    except:
        pass

    print(question.reputation_set)

    if question.user.id != request.user.id:
        if request.user.id not in question.reputation_set and -request.user.id not in question.reputation_set:
            question.reputation_set.add(-request.user.id)
            question.reputation_str = ','.join(set(map(str, question.reputation_set))) + ','
            question.save()
            messages.success(request, 'Votes updated.')
            return HttpResponseRedirect(question.get_absolute_url())
        else:
            messages.success(request, 'Already voted.')
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        messages.error(request, "This is your question can't vote")
        return HttpResponseRedirect(question.get_absolute_url())


def get_questions(request):
    if request.is_ajax():
        query = request.GET.get('term', '')
        question_list = Question.objects.all()
        question_list = question_list.filter(
            Q(title__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()

        try:
            for question in question_list:
                for u_id in question.reputation_str.split(','):
                    if int(u_id) > 0:
                        question.reputation_count += 1
                    elif int(u_id) < 0:
                        question.reputation_count -= 1
                    question.reputation_set.add(int(u_id))
        except:
            pass

        results = []
        for question in question_list:
            question_json = dict()

            if question.title.lower().find(query.lower()) >= 0:
                question_json['value'] = question.title
            if question.user.first_name.lower().find(query.lower()) >= 0:
                question_json['value'] = question.user.first_name
            if question.user.last_name.lower().find(query.lower()) >= 0:
                question_json['value'] = question.user.last_name
            if question.user.username.lower().find(query.lower()) >= 0:
                question_json['value'] = question.user.username

            if results.count(question_json) == 0:
                results.append(question_json)

        data = json.dumps(results)
    else:
        data = 'fail'
    content_type = 'application/json'
    return HttpResponse(data, content_type=content_type)
