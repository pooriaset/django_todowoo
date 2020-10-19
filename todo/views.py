from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from .models import ToDo
from .forms import TodoForm
from django.utils import timezone


def home(request):
    return render(request, 'todo/home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, "todo/signup.html", {"forms": UserCreationForm()})
    elif request.method == 'POST':
        username = request.POST['username']
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username, request.POST['password1'])
                user.save()
                auth_login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                error_message = "Username '%s' has already been taken! Please choose another username!" % username
                return render(request, "todo/signup.html", {"forms": UserCreationForm(), 'error': error_message})
        else:
            error_message = "Password and confirm password are not match"
            return render(request, "todo/signup.html", {"forms": UserCreationForm(), 'error': error_message})
    else:
        return HttpResponseForbidden()


def login(request):
    if request.method == 'GET':
        return render(request, "todo/login.html", {"forms": AuthenticationForm()})
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            error_message = "Password and username did not match"
            return render(request, 'todo/login.html', {'forms': AuthenticationForm, 'error': error_message})
        else:
            auth_login(request, user)
            return redirect('current_todos')
    else:
        return HttpResponseForbidden()


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('home')
    else:
        return HttpResponseNotFound()


def current_todos(request):
    todos = ToDo.objects.filter(todoCreator=request.user, dateCompleted__isnull=True)
    return render(request, 'todo/current_todos.html', {"todos": todos})


def create_todo(request):
    if request.method == "GET":
        return render(request, 'todo/createTodo.html', {'forms': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.todoCreator = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            error_message = 'Bad data passed in'
            return render(request, 'todo/createTodo.html', {"forms": TodoForm, "error": error_message})


def view_todo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, todoCreator=request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, 'todo/todo.html', {"todo": todo, "forms": form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect("current_todos")
        except ValueError:
            error_message = 'Bad data passed in'
            return render(request, 'todo/todo.html', {"todo": todo, "forms": form, "error": error_message})


def complete_todo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, todoCreator=request.user)
    if request.method == "POST":
        todo.dateCompleted = timezone.now()
        todo.save()
        return redirect("current_todos")

def delete_todo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, todoCreator=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect("current_todos")