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
    path('CRM/addLesson/<int:group_pk>',views.addLessonFromGroup,name = 'addLessonFromGroup'),
    path('CRM/lessonSuccess',views.lessonSuccess,name = 'lessonSuccess'),
    #=====================================
    path('CRM/paymentsTab',views.CRM_payments,name = 'CRM_payments'),
    path('CRM/addPayment',views.addPayment,name = 'addPayment'),
    #===========================================================
    path('CRM/groupsTab',views.CRM_groups,name = 'CRM_groups'),
    path('CRM/addGroup',views.addGroup,name = 'addGroup'),
    path('CRM/addGroupSuccess',views.addGroupSuccess,name = 'addGroupSuccess'),
    #===========================================================
    path('CRM/dashboard',views.CRM_dashboard,name = 'dashboard'),
    #===========================================================
    path('CRM/clientCard/<int:client_id>',views.client_card, name = 'client_card'),
    path('CRM/addPhone',views.addPhone, name = 'addPhone'),
    path('CRM/editName',views.editName, name = 'editName'),
    #===========================================================
    path('CRM/editLesson/<int:lesson_id>',views.editLesson, name = 'editLesson'),
    path('CRM/deleteLessonClient/<int:lesson_id>/<int:client_id>',views.deleteLessonClient, name = 'deleteLessonClient'),
    path('CRM/editPriceLessons',views.editPriceLessons, name = 'editPriceLessons'),
    path('CRM/addClientToLesson',views.addClientToLesson, name = 'addClientToLesson'),
    #===========================================================
    path('CRM/editGroup/<int:group_id>',views.editGroup, name = 'editGroup'),
    path('CRM/addClientToGroup',views.addClientToGroup, name = 'addClientToGroup'),
    path('CRM/deleteGroupClient/<int:group_id>/<int:client_id>',views.deleteGroupClient, name = 'deleteGroupClient'),
    path('CRM/editGroupData',views.editGroupData, name = 'editGroupData'),
    #===========================================================
    path('CRM/mountlyReport',views.mountlyReport,name = 'mountlyReport'),
]