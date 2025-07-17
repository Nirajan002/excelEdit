from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_excel, name='upload_excel'),
    path('export/', views.export_excel, name='export_excel'),
    path('signup/', views.signup_view, name='signup'),
]
