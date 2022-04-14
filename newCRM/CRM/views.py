from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from datetime import datetime

from .models import *
def index(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        #user = "None"
        return HttpResponseRedirect(reverse('forbiden', args=()))

    template = loader.get_template('crm/index.html')
    context = {"username":username}
    return HttpResponse(template.render(context, request))

def loginView(request):
    template = loader.get_template('crm/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def forbiden(request):
    template = loader.get_template('crm/forbidenPage.html')
    context = {}
    return HttpResponse(template.render(context, request))

def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('index', args=()))

def loginCheck(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request,user)
        return HttpResponseRedirect(reverse('index', args=()))
    else:
        return render(request,'crm/login.html',{
            'error_message': "You didn't select a choice."
        })

#==========================================================================================================#

def CRM_clients(request):
    if request.user.is_authenticated:
        user = request.user.username
    else:
        #user = "None"
        return HttpResponseRedirect(reverse('forbiden', args=()))
    data = [{'name':s.name,
    'phone':Phone.objects.filter(client = s),
    'money':s.money
    } for s in Client.objects.all()]
    #students = Client.objects.all()
    #contacts = {s:Phone.objects.get(client = s)  for s in students}
    print(data)
    template = loader.get_template('crm/simpleClients.html')
    context = {
        'username' : user,
        'data':data
    }
    return HttpResponse(template.render(context, request))

def refreshClients(request):
    clients= Client.objects.all()
    for c in clients:
        lessons = Lesson.objects.filter(clients = c)
        credit = sum([l.price for l in lessons])
        payments = Payment.objects.filter(client = c)
        debet= sum([p.value for p in payments])
        print(c,lessons,payments)
        c.money = debet-credit
        c.save()
    return HttpResponseRedirect(reverse('CRM_clients', args=()))
def add_client(request):
    try:
        name = request.POST['name']
    except (KeyError):
        return render(request,'crm/addClient.html',{
            'error_message': "You didn't select a choice."
        })
    c = Client(name = name)
    c.save()
    return HttpResponseRedirect(reverse('CRM_clients', args=()))

#=======================================================
def CRM_Lessons(request):
    if request.user.is_authenticated:
        user = request.user.username
    else:
        #user = "None"
        return HttpResponseRedirect(reverse('forbiden', args=()))


    template = loader.get_template('crm/simpleLessons.html')
    data = Lesson.objects.order_by('-date')

    context = {
        'lessons' : data,
    }
    return HttpResponse(template.render(context, request))    

def addLesson(request):
    students = Client.objects.all()
    teachers = Teacher.objects.all()
    template = loader.get_template('crm/lesson.html')
    context = {
        'active_students' : students,
        'active_teachers' : teachers
    }
    return HttpResponse(template.render(context, request))

def lessonSuccess(request):
    print(request.POST)
    try:
        name = request.POST['name']
        teacher = int(request.POST['teacher'])
        price = float(request.POST['price'])
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d")
        students = [int(key.replace("student","")) for key in request.POST if key.startswith("student")]
    except:
        print("failed")
        return HttpResponseRedirect(reverse('addLesson', args=()))
    date = datetime.strptime(request.POST['date'],"%Y-%m-%d")
    active_teacher = Teacher.objects.get(pk = teacher)
    active_students = Client.objects.filter(pk__in = students)
    l = Lesson(teacher = active_teacher,
    name = name,
    date = date,
    price = price)
    l.save()
    l.clients.set(active_students)
    l.save()
    print(name,active_teacher,active_students,price,date)
    return HttpResponseRedirect(reverse('CRM_Lessons', args=()))

#========================================================
def CRM_payments(request):
    payments = Payment.objects.order_by('-date')
    clients = Client.objects.all()
    template = loader.get_template('crm/simplePayments.html')
    context = {
        'payments' : payments,
        'clients' : clients
    }
    return HttpResponse(template.render(context, request))  

def addPayment(request):
    try:
        print(request.POST)
        client = int(request.POST['client'])
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d")
        value = float(request.POST['value'])
    except (KeyError):
        return render(request,'crm/addClient.html',{
            'error_message': "You didn't select a choice."
        })
    active_client = Client.objects.get(pk = client)
    p = Payment(client = active_client,
    date = date,
    value = value)
    p.save()
    return HttpResponseRedirect(reverse('CRM_payments', args=()))
