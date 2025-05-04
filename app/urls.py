from django.urls import path

from app import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register_form/', views.RegisterDataView.as_view(), name='data_form'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('', views.MainView.as_view(), name='main'),
]