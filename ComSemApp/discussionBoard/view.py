import json

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from django.urls import resolve
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from ComSemApp.teacher import constants as teacher_constants

from ComSemApp.models import *
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin, SubmissionViewMixin
from ComSemApp.administrator.forms import ReplyForm, TopicForm


#This class deals with listing out all the topics within database
#brings back the Topic model and displays it using Django Listview
#This page requires you to be logged in to use
class TopicListView(LoginRequiredMixin,ListView):
    model = Topic
    template_name = 'ComSemApp/discussionBoard/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter().order_by("-id")

class ReplyMixin(LoginRequiredMixin, ListView, object):
    context_object_name = 'replies'
    template_name = 'ComSemApp/discussionBoard/add_reply.html'
    fields = ["message", "personPosted", "topic", "hasMark"]
    success_url = reverse_lazy("discussionBoard:topic")
    
    def get_form_kwargs(self):
        kwargs = super(ReplyMixin, self).get_form_kwargs()
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        topic_id = kwargs.get('topic_id', None)
        topics = Topic.objects.filter(id = topic_id)
        if not topics.exists():
            return HttpResponseRedirect(reverse("discussion_board:topics"))
        self.topic = topics.first()
        return super(ReplyMixin, self).dispatch(request, *args, **kwargs)
    


class ReplyView(ReplyMixin, FormView):
    model = Reply
    template_name = 'ComSemApp/discussionBoard/reply_page.html'
    context_object_name = 'replies'
    fields = ["message", "personPosted", "topic", "hasMark"]

    def get_queryset(self):
        return Reply.objects.filter(topic = self.topic)

    def get_context_data(self ,**kwargs):
        self.object_list = self.get_queryset()
        context = super(ReplyView, self).get_context_data(**kwargs)
        context['topic_description'] = self.topic.topic
        context['discussion_board'] = True
        return context

    def form_invalid(self, reply_form, **kwargs):
        response = super().form_invalid(reply_form)
        return JsonResponse(reply_form.errors, status=400)
    
    def get(self, request, *args, **kwargs):
        allow_empty = True
        reply_form = ReplyForm()
        reply_form.prefix = 'reply_form'
        return self.render_to_response(self.get_context_data(form=reply_form))

    def post(self, request, *args, **kwargs):
        current_url = resolve(request.path_info).url_name
        reply_form = ReplyForm(self.request.POST, prefix = 'reply_form')
        likeButton = request.POST.get("like")
        dislikeButton = request.POST.get("dislike")
        if likeButton:
            print(likeButton)
            reply = Reply.objects.get(id = int(likeButton))
            reply.hasMark = 1
            reply.save()
            if current_url == "admin_topic":
                return HttpResponseRedirect(reverse("administrator:admin_topic", kwargs={'topic_id': self.topic.id }))
            elif current_url == "teacher_topic":
                return HttpResponseRedirect(reverse("teacher:teacher_topic", kwargs={'topic_id': self.topic.id }))
            elif current_url == "student_topic":
                return HttpResponseRedirect(reverse("student:student_topic", kwargs={'topic_id': self.topic.id }))
            else:
                return HttpResponseRedirect(reverse("discussion_board:topic", kwargs={'topic_id': self.topic.id }))
        elif dislikeButton:
            print(dislikeButton)
            reply = Reply.objects.get(id = int(dislikeButton))
            reply.hasMark = 0
            reply.save()
            if current_url == "admin_topic":
                return HttpResponseRedirect(reverse("administrator:admin_topic", kwargs={'topic_id': self.topic.id }))
            elif current_url == "teacher_topic":
                return HttpResponseRedirect(reverse("teacher:teacher_topic", kwargs={'topic_id': self.topic.id }))
            elif current_url == "student_topic":
                return HttpResponseRedirect(reverse("student:student_topic", kwargs={'topic_id': self.topic.id }))
            else:
                return HttpResponseRedirect(reverse("discussion_board:topic", kwargs={'topic_id': self.topic.id }))
        elif reply_form.is_valid():
            print("it is giving this if statement a thing")
            reply = reply_form.save(commit=False)
            reply.personPosted = request.user
            reply.topic = self.topic
            reply.hasMark = 0
            reply.save()

            if current_url == "admin_topic":
                return HttpResponseRedirect(reverse("administrator:admin_topic", kwargs={'topic_id': self.topic.id }))
            elif current_url == "teacher_topic":
                return HttpResponseRedirect(reverse("teacher:teacher_topic", kwargs={'topic_id': self.topic.id }))
            elif current_url == "student_topic":
                return HttpResponseRedirect(reverse("student:student_topic", kwargs={'topic_id': self.topic.id }))
            else:
                return HttpResponseRedirect(reverse("discussion_board:topic", kwargs={'topic_id': self.topic.id }))
        else:
            return self.form_invalid(reply_form, **kwargs)



class CreateThreadView(LoginRequiredMixin,FormView):
    model = Reply
    template_name = 'ComSemApp/discussionBoard/create_topic.html'
    context_object_name = 'replies'
    fields = ["message", "personPosted", "topic", "hasMark"]

    def form_invalid(self, topic_form, **kwargs):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)
    
    def get(self, request, *args, **kwargs):
        allow_empty = True
        topic_form = TopicForm()
        topic_form.prefix = "topic_form"
        return self.render_to_response(self.get_context_data(form=topic_form))
    
    def post(self, request, *args, **kwargs):
        topic_form = TopicForm(self.request.POST, prefix = 'topic_form')
        current_url = resolve(request.path_info).url_name
        if topic_form.is_valid():
            topic = Topic(personPosted = request.user, topic = topic_form.cleaned_data["title"])
            topic.save()
            reply = topic_form.save(commit=False)
            reply.personPosted = request.user
            reply.topic = topic
            reply.hasMark = 0
            reply.save()
            if current_url == "admin_create_topic":
                return HttpResponseRedirect(reverse("administrator:admin_topic", kwargs={'topic_id': topic.id }))
            elif current_url == "teacher_create_topic":
                return HttpResponseRedirect(reverse("teacher:teacher_topic", kwargs={'topic_id': topic.id }))
            elif current_url == "student_create_topic":
                return HttpResponseRedirect(reverse("student:student_topic", kwargs={'topic_id': topic.id }))
            else:
                return HttpResponseRedirect(reverse("discussion_board:topic", kwargs={'topic_id': topic.id }))
        else:
            return self.form_invalid(topic_form, **kwargs)