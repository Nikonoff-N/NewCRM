from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login',views.loginView,name = 'loginView'),
    path('loginSuccess',views.loginCheck,name = 'loginCheck'),
    path('forbiden',views.forbiden,name = 'forbiden'),
    path('logout',views.logoutView,name = 'logoutView'),

    #=====================================
    path('CRM/clientsTab',views.CRM_clients,name = 'CRM_clients'),
    path('CRM/addClient',views.add_client,name = 'add_client'),
    path('CRM/refreshClients',views.refreshClients,name = 'refreshClients'),
    #=====================================
    path('CRM/lessonsTab',views.CRM_Lessons,name = 'CRM_Lessons'),
    path('CRM/addLesson',views.addLesson,name = 'addLesson'),
    path('CRM/lessonSuccess',views.lessonSuccess,name = 'lessonSuccess'),
    #=====================================
    path('CRM/paymentsTab',views.CRM_payments,name = 'CRM_payments'),
    path('CRM/addPayment',views.addPayment,name = 'addPayment'),
]