from django.urls import path

from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('consultations', views.consultations_list, name='consultations'),
    path('consultations/<uuid:consultation_id>', views.view_consultation, name='view_consultation'),
    path('consultations/<uuid:consultation_id>/respond', views.respond_consultation, name='respond_consultation'),
    path('consultations/<uuid:consultation_id>/mark-reviewing', views.mark_reviewing, name='mark_reviewing'),
    path('consultations/<uuid:consultation_id>/mark-resolved', views.mark_resolved, name='mark_resolved'),
]

