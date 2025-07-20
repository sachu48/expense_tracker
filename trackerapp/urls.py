from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
 
    path('login/', auth_views.LoginView.as_view(template_name='trackerapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    path('add-expense/', views.add_expense, name='add_expense'),
  
    path('view-expenses/', views.view_expenses, name='view_expenses'),
    path('add-income/', views.add_monthly_income, name='add_monthly_income'),
]