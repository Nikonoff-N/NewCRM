from tokenize import group
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from datetime import datetime
import json
from .models import *
DAYS = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']

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
    data = [{'id':s.pk,
    'name':s.name,
    'phone':Phone.objects.filter(client = s),
    'money':s.money
    } for s in Client.objects.all()]
    #students = Client.objects.all()
    #contacts = {s:Phone.objects.get(client = s)  for s in students}
    #print(data)
    template = loader.get_template('crm/simpleClients.html')
    context = {
        'username' : user,
        'data':data,
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
        'name':"",
        'active_students' : students,
        'active_teachers' : teachers
    }
    return HttpResponse(template.render(context, request))

def addLessonFromGroup(request,group_pk):
    group = Group.objects.get(pk = group_pk)
    print(group.name)
    students = group.clients.all()
    teachers = Teacher.objects.all()
    template = loader.get_template('crm/lesson.html')
    context = {
        'name':group.name,
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
        tag = request.POST['tag']
        client = int(request.POST['client'])
        note = request.POST['note']
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d")
        value = float(request.POST['value'])
    except (KeyError):
        return render(request,'crm/addClient.html',{
            'error_message': "You didn't select a choice."
        })
    active_client = Client.objects.get(pk = client)
    p = Payment(client = active_client,
    date = date,
    value = value,
    note = note)
    p.save()
    if tag == "client":
        return HttpResponseRedirect(reverse('client_card', args=(client,)))
    else:
        return HttpResponseRedirect(reverse('CRM_payments', args=()))

#========================================================

def convertSchedule(schedule:str)->list:
    schedule = json.loads(schedule.replace("\'", "\""))
    r = []
    for day,time in schedule.items():
        r.append(DAYS[int(day)]+" "+time)
    return r

def CRM_groups(request):
    groups = Group.objects.all()
    active_groups = [{
        'pk':g.pk,
        'teacher':g.teacher,
        'name':g.name,
        'clients':g.clients.all,
        'schedule':convertSchedule(g.schedule)
    } for g in groups]
    template = loader.get_template('crm/simpleGroups.html')
    context = {
        'groups' : active_groups,
    }
    return HttpResponse(template.render(context, request))

def addGroup(request):
    clients = Client.objects.all()
    teachers = Teacher.objects.all()
    template = loader.get_template('crm/addGroup.html')
    context = {
        'clients' : clients,
        'teachers':teachers
    }
    return HttpResponse(template.render(context, request))

def addGroupSuccess(request):
    print(request.POST)
    try:
        name = request.POST['name']
        print(request.POST.getlist('student'))
        students = [int(c) for c in request.POST.getlist('student')]
        print(students)
        students = Client.objects.filter(pk__in = students)
        print(students)
        teacher = Teacher.objects.get(pk = request.POST['teacher'])
        schedule = {}
        for day in request.POST.getlist('day'):
            schedule[day] = request.POST[f"day{day}time"]
    except:
        return render(request,'crm/addGroup.html',{
            'error_message': "You didn't select a choice."
        })
    else:
        print(name)
        print(students)
        print(schedule)
        g = Group(name = name,
        schedule = str(schedule),
        teacher = teacher)
        g.save()
        g.clients.set(students)
        g.save()
        return HttpResponseRedirect(reverse('CRM_groups', args=()))

#========================================================
def checkTime(schedule)->str:
    schedule = json.loads(schedule.replace("\'", "\""))
    today = str(datetime.today().weekday())
    if today in schedule:
        return schedule[today]
    else:
        return False

def CRM_dashboard(request):
    groups = Group.objects.all()

    groups = [g for g in groups if checkTime(g.schedule)]
    active_groups = [{
        'pk':g.pk,
        'teacher':g.teacher,
        'name':g.name,
        'clients':g.clients.all,
        'schedule':convertSchedule(g.schedule)
    } for g in groups]
    template = loader.get_template('crm/simpleDashboard.html')
    context = {
        'groups' : active_groups,
    }
    return HttpResponse(template.render(context, request))

def client_card(request, client_id):
    client = Client.objects.get(pk=client_id)
    payments = Payment.objects.filter(client=client)
    group = Group.objects.filter(clients=client)
    phone = Phone.objects.filter(client=client)
    data = Lesson.objects.filter(clients=client)
    template = loader.get_template('crm/clientCard.html')
    context = {
        'client' : client,
        'payments':payments,
        'group': group,
        'phone': phone,
        'lessons': data,
    }
    return HttpResponse(template.render(context, request))

def addPhone(request):
    try:
        print(request.POST)
        client = int(request.POST['client'])
        note = request.POST['note']
        phone = int(request.POST['phone'])
    except (KeyError):
        return render(request,'crm/clientCard.html',{
            'error_message': "You didn't select a choice."
        })
    active_client = Client.objects.get(pk = client)
    p = Phone(client = active_client,
    phone = phone,
    note = note)
    p.save()
    return HttpResponseRedirect(reverse('client_card', args=(client,)))

def editName(request):
    try:
        client = int(request.POST['client'])
        name = request.POST['name']
    except (KeyError):
        return render(request,'crm/clientCard.html',{
            'error_message': "You didn't select a choice."
        })
    clients = Client.objects.get(pk = client)
    clients.name = name
    clients.save()
    return HttpResponseRedirect(reverse('client_card', args=(client,)))

# def deletePhone(request):
#     try:
#         print(request.POST)
#         client = int(request.POST['client'])
#         note = request.POST['note']
#         phone = int(request.POST['phone'])
#     except (KeyError):
#         return render(request,'crm/clientCard.html',{
#             'error_message': "You didn't select a choice."
#         })
#     active_client = Client.objects.get(pk = client)
#     p = Phone(client = active_client,
#     phone = phone,
#     note = note)
#     p.delete()
#     context = {
#         'phone': p,
#     }
#     return HttpResponseRedirect(reverse('client_card', args=(client, context)))

def editLesson(request, lesson_id):
    lesson = Lesson.objects.get(pk=lesson_id)
    context = {
        'lessons': lesson,
    }

    template = loader.get_template('crm/editLesson.html')

    return HttpResponse(template.render(context, request))

    
def editPriceLessons(request):
    try:
        lesson = int(request.POST['lesson'])
        price = int(request.POST['price'])
    except (KeyError):
        return render(request,'crm/editLesson.html',{
            'error_message': "You didn't select a choice."
        })
    lessons = Lesson.objects.get(pk=lesson)
    lessons.price = price
    lessons.save()
    return HttpResponseRedirect(reverse('editLesson', args=(lesson,)))

def deleteClient(request, client_id, lesson_id):
    lesson = Lesson.objects.get(pk=lesson_id)
    client = Client.objects.get(pk=client_id)
    lesson.clients.remove(client)
    lesson.save()
    return HttpResponseRedirect(reverse('editLesson', args=(lesson_id,)))
    