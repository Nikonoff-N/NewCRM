
from msilib.schema import Error
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from datetime import datetime
import json
from .models import *
from functools import reduce
from django.contrib.auth.decorators import login_required, user_passes_test
DAYS = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']

   
def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

@login_required
@user_passes_test(lambda u: u.groups.filter(name='admin').exists(),login_url='teachersDashbord')
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
@login_required
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
@login_required
def refreshClients(request):
    clients= Client.objects.all()
    for c in clients:
        lessons = Lesson.objects.filter(clients = c)
        credit = sum([l.price for l in lessons])
        payments = Payment.objects.filter(client = c)
        debet= sum([p.value for p in payments])
        #print(c,lessons,payments)
        c.money = debet-credit
        c.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return HttpResponseRedirect(reverse('CRM_clients', args=()))
@login_required
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
@login_required
def CRM_Lessons(request):
    if request.user.is_authenticated:
        user = request.user.username
    else:
        #user = "None"
        return HttpResponseRedirect(reverse('forbiden', args=()))
    month = datetime.today().month  
    if 'month' in request.POST:
        try:
            month = int(request.POST['month'][-2::])
        except:
            pass
    data = Lesson.objects.filter(date__month = month)
    if 'teacher' in request.POST:
        teacher = int(request.POST['teacher'])
        if teacher >= 0:
            teacher = Teacher.objects.get(pk = teacher)
            
            data = data.filter(teacher =teacher)
    if 'group' in request.POST:
        group = int(request.POST['group'])
        if group >= 0:
            group = Group.objects.get(pk = group)

            data = Lesson.objects.filter(group = group)
    data = data.order_by('-date')
    groups = Group.objects.all().order_by('archive')
    teachers = Teacher.objects.all()
    template = loader.get_template('crm/simpleLessons.html')
    

    context = {
        'groups':groups,
        'teachers':teachers,
        'lessons' : data,
    }
    return HttpResponse(template.render(context, request))    
@login_required
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
@login_required
def addLessonFromGroup(request,group_pk):
    group = Group.objects.get(pk = group_pk)
    students = group.clients.all()
    teachers = Teacher.objects.all()
    template = loader.get_template('crm/lesson.html')
    context = {
        'group':group,
        'default_teacher':group.teacher.pk,
        'active_students' : students,
        'active_teachers' : teachers
    }
    return HttpResponse(template.render(context, request))   

@login_required
def lessonSuccess(request):
    try:
        name = request.POST['name']
        teacher = int(request.POST['teacher'])
        price = float(request.POST['price'])
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d")
        students = [int(key.replace("student","")) for key in request.POST if key.startswith("student")]
        group = int(request.POST['group'])
    except:
        return HttpResponseRedirect(reverse('addLesson', args=()))
    date = datetime.strptime(request.POST['date'],"%Y-%m-%d")
    active_teacher = Teacher.objects.get(pk = teacher)
    active_students = Client.objects.filter(pk__in = students)
    group = Group.objects.get(pk = group)
    l = Lesson(teacher = active_teacher,
    name = name,
    date = date,
    price = price,
    group = group)
    l.save()
    l.clients.set(active_students)
    l.save()
    return HttpResponseRedirect(reverse('CRM_Lessons', args=()))

#========================================================
@login_required
def CRM_payments(request):
    payments = Payment.objects.order_by('-date')
    clients = Client.objects.all()
    template = loader.get_template('crm/simplePayments.html')
    context = {
        'payments' : payments,
        'clients' : clients
    }
    return HttpResponse(template.render(context, request))  
@login_required
def addPayment(request):
    try:
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

@login_required
def CRM_groups(request):
    groups = Group.objects.filter(archive = False)
    active_groups = [{
        'pk':g.pk,
        'teacher':g.teacher,
        'name':g.name,
        'clients':g.clients.all,
        'schedule':convertSchedule(g.schedule)
    } for g in groups]
    groups = Group.objects.filter(archive = True)
    archive_group = [{
        'pk':g.pk,
        'teacher':g.teacher,
        'name':g.name,
        'clients':g.clients.all,
        'schedule':convertSchedule(g.schedule)
    } for g in groups]
    template = loader.get_template('crm/simpleGroups.html')
    context = {
        'groups' : active_groups,
        'archive' : archive_group,
    }
    return HttpResponse(template.render(context, request))
@login_required
def addGroup(request):
    clients = Client.objects.all()
    teachers = Teacher.objects.all()
    template = loader.get_template('crm/addGroup.html')
    context = {
        'clients' : clients,
        'teachers':teachers
    }
    return HttpResponse(template.render(context, request))
@login_required
def addGroupSuccess(request):
    try:
        name = request.POST['name']
        students = [int(c) for c in request.POST.getlist('student')]
        students = Client.objects.filter(pk__in = students)
        teacher = Teacher.objects.get(pk = request.POST['teacher'])
        schedule = {}
        for day in request.POST.getlist('day'):
            schedule[day] = request.POST[f"day{day}time"]
    except:
        return render(request,'crm/addGroup.html',{
            'error_message': "You didn't select a choice."
        })
    else:
        g = Group(name = name,
        schedule = str(schedule),
        teacher = teacher)
        g.save()
        g.clients.set(students)
        g.save()
        return HttpResponseRedirect(reverse('CRM_groups', args=()))

#========================================================
def checkTime(schedule,day)->str:
    schedule = json.loads(schedule.replace("\'", "\""))
    if day in schedule:
        return schedule[day]
    else:
        return False

@login_required
def CRM_dashboard(request):
    all_groups = Group.objects.filter(archive = False)
    today = str(datetime.today().weekday())
    groups = [g for g in all_groups if checkTime(g.schedule,today)]
    data = []
    for g in groups:
        data.extend([{'id':s.pk,
            'name':s.name,
            'phone':Phone.objects.filter(client = s),
            'money':s.money,
            'message':f"Зравствуйте, напоминаем что завтра в {checkTime(g.schedule,today)} занятие по {g.name}. Будем вас ждать"
    } for s in g.clients.all()])
    active_groups = [{
        'pk':g.pk,
        'teacher':g.teacher,
        'name':g.name,
        'clients':g.clients.all,
        'schedule':convertSchedule(g.schedule)
    } for g in groups]
    today = datetime.today().weekday()
    today = today+1 if today <6 else 0
    groups = [g for g in all_groups if checkTime(g.schedule,str(today))]
    tomorrow_data = []
    for g in groups:
        tomorrow_data.extend([{'id':s.pk,
            'name':s.name,
            'phone':Phone.objects.filter(client = s),
            'money':s.money,
            'message':f"Зравствуйте, напоминаем что завтра в {checkTime(g.schedule,today)} занятие по {g.name}. Будем вас ждать"
    } for s in g.clients.all()])
    tomorrow_active_groups = [{
        'pk':g.pk,
        'teacher':g.teacher,
        'name':g.name,
        'clients':g.clients.all,
        'schedule':convertSchedule(g.schedule)
    } for g in groups]    
    template = loader.get_template('crm/simpleDashboard.html')
    context = {
        'groups' : active_groups,
        'clients' : data,
        'tomorrow_groups' : tomorrow_active_groups,
        'tomorrow_clients' : tomorrow_data,        
    }
    return HttpResponse(template.render(context, request))

#========================================================
@login_required
def client_card(request, client_id,error_message = None):
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
        'error_message':error_message

    }
    return HttpResponse(template.render(context, request))
class phoneError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return f"[ERROR]{self.message}\n"

def fixPhone(phone:str)->int:
    remove = "() -"
    for c in remove:
        phone = phone.replace(c,"")
    if len(phone) not in (10,11) :
        raise phoneError("Неверный номер!")
    elif len(phone) == 10 :
        phone = "8" + phone
        return int(phone)
    elif len(phone) == 11 :
        phone = "8" + phone[1::]
        return int(phone)
    else:
        pass

@login_required
def addPhone(request):
    try:
        client = int(request.POST['client'])
        note = request.POST['note']
        phone = fixPhone(request.POST['phone'])
    except (KeyError):
        return render(request,'crm/clientCard.html',{
            'error_message': "Что-то пошло не так, причем серьезно!"
        })
    except phoneError as e:
        return redirect("client_card",client_id = client,error_message = e.message)
    active_client = Client.objects.get(pk = client)
    p = Phone(client = active_client,
    phone = phone,
    note = note)
    p.save()
    return HttpResponseRedirect(reverse('client_card', args=(client,)))
@login_required
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


#========================================================
@login_required
def editLesson(request, lesson_id):
    lesson = Lesson.objects.get(pk=lesson_id)
    clients = Client.objects.all()
    
    context = {
        'lessons': lesson,
        'clients': clients,
    }
    template = loader.get_template('crm/editLesson.html')

    return HttpResponse(template.render(context, request))

@login_required    
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

@login_required
def deleteLessonClient(request, client_id, lesson_id):
    client = Client.objects.get(pk=client_id)
    lesson = Lesson.objects.get(pk=lesson_id)
    lesson.clients.remove(client)
    lesson.save()
    return HttpResponseRedirect(reverse('editLesson', args=(lesson_id,)))

@login_required      
def addClientToLesson(request):
    try:
        client = request.POST['client']
        lesson = int(request.POST['lesson'])
    except (KeyError):
        return render(request,'crm/editLesson.html',{
            'error_message': "You didn't select a choice."
        })

    new_client = Client.objects.get(pk = client)
    lesson = Lesson.objects.get(pk = lesson)
    lesson.clients.add(new_client)
    lesson.save()
    return HttpResponseRedirect(reverse('editLesson', args=(lesson.pk,)))
        
    

#========================================================
@login_required
def editGroup(request, group_id):
    group = Group.objects.get(pk=group_id)
    clients = Client.objects.all()
    active_group = {
        'pk':group.pk,
        'teacher':group.teacher,
        'name':group.name,
        'clients':group.clients.all,
        'schedule':convertSchedule(group.schedule),
        'archive':group.archive,
    }

    context = {
        'group': active_group,
        'clients' : clients,
    }
    template = loader.get_template('crm/editGroup.html')

    return HttpResponse(template.render(context, request))
@login_required
def addClientToGroup(request):
    try:
        client = request.POST['client']
        group = int(request.POST['group'])
    except (KeyError):
        return render(request,'crm/editLesson.html',{
            'error_message': "You didn't select a choice."
        })
    new_client = Client.objects.get(pk = client)
    group = Group.objects.get(pk = group)
    group.clients.add(new_client)
    group.save()
    return HttpResponseRedirect(reverse('editGroup', args=(group.pk,)))
    
@login_required
def deleteGroupClient(request, client_id, group_id):
    client = Client.objects.get(pk=client_id)    
    group = Group.objects.get(pk=group_id)
    group.clients.remove(client)
    group.save()
    return HttpResponseRedirect(reverse('editGroup', args=(group_id,)))
@login_required
def editGroupData(request):
    try:
        group = int(request.POST['group'])
        schedule = {}
        for day in request.POST.getlist('day'):
            schedule[day] = request.POST[f"day{day}time"]
    except:
        return render(request,'crm/editGroup.html',{
            'error_message': "You didn't select a choice."
        })
    else:
        if not schedule:
           return HttpResponseRedirect(reverse('editGroup', args=(group,)))  
        else:
            for i in schedule:
                if schedule[i] == "":
                    return HttpResponseRedirect(reverse('editGroup', args=(group,)))    
        g = Group.objects.get(pk=group)
        g.schedule = str(schedule)
        g.save()  
        return HttpResponseRedirect(reverse('editGroup', args=(group,)))
@login_required
def switch_archive_group(request,group_id):
    g = Group.objects.get(pk=group_id)
    g.archive = not g.archive
    g.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#====================================================================
@login_required
@user_passes_test(lambda u: u.groups.filter(name='admin').exists(),login_url='teachersDashbord')
def mountlyReport(request):
    pay = 130
    if 'month' in request.POST:
        today = int(request.POST['month'][-2::])
    else:
        today = datetime.today().month
    active_lessons = Lesson.objects.filter(
        date__year=2022,
        date__month = today)
    totalLessonsPeopleCount = sum([l.clients.all().count() for l in active_lessons])
    totalLessonsMoneyCount = sum([l.clients.all().count()*l.price for l in active_lessons])
    active_payments = Payment.objects.filter(        
        date__year=2022,
        date__month = today)
    totalPayAll = sum([p.value for p in active_payments])
    totalPayDiff = totalPayAll-totalLessonsMoneyCount
    active_clients = Client.objects.filter(money__lte = -1)
    teacher_data = []
    totalHighRoll = 0
    for t in Teacher.objects.all():
        t_lessons = active_lessons.filter(teacher = t).filter(date__month = today)
        hourCount = sum([l.clients.all().count() for l in t_lessons])
        totalPay = sum([l.clients.all().count()*l.price for l in t_lessons])
        payday = sum([l.clients.all().count()*pay for l in t_lessons])
        totalHighRoll+=totalPay - payday
        data = {'name':t.name,
        'lessonCount':t_lessons.count,
        'hourCount':hourCount,
        'eff':hourCount/t_lessons.count() if t_lessons.count()>0 else 0,
        'totalPay':totalPay,
        'payday':payday,
        'highroll':totalPay - payday,
        'lessonHystory':t_lessons
        }
        teacher_data.append(data)

    
    template = loader.get_template('crm/report.html')
    context = {
        'totalLessonsCount' : active_lessons.count,
        'totalLessonsPeopleCount' : totalLessonsPeopleCount,
        'totalLessonsMoneyCount' : totalLessonsMoneyCount,
        'totalPayCount' : active_payments.count,
        'totalPay' : totalPayAll,
        'totalPayDiff' : totalPayDiff,
        'clients' : active_clients,
        'teacher_data':teacher_data,
        'totalHighRoll':totalHighRoll
    }
    return HttpResponse(template.render(context, request))

#==============================================================================
@login_required
def teachersDashbord(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        #user = "None"
        return HttpResponseRedirect(reverse('forbiden', args=()))
    
    # groups = Group.objects.all()

    # groups = [g for g in groups if checkTime(g.schedule)]
    # active_groups = [{
    #     'pk':g.pk,
    #     'teacher':g.teacher,
    #     'name':g.name,
    #     'clients':g.clients.all,
    #     'schedule':convertSchedule(g.schedule)
    # } for g in groups]
    template = loader.get_template('crm/teachersDashboard.html')
    context ={
        "username":username,
       # 'groups' : active_groups,
    }
    return HttpResponse(template.render(context, request))