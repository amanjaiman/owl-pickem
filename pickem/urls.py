from django.urls import path

from . import views

app_name = 'pickem'
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signup/confirm', views.signupaction, name="signupaction"),
    path('login/', views.loginview, name='loginview'),
    path('login/confirm', views.loginaction, name="loginaction"),
    path('logout/', views.logoutaction, name="logoutaction"),
    path('makepredictions/', views.makepredictions, name="makepredictions"),
    path('adminaction/', views.adminaction, name="adminaction"),
    path('leaderboard/', views.leaderboard, name="leaderboard"),
    path('<str:username>/history/', views.userhistory, name="userhistory"),
    path('importschedule', views.import_schedule, name="import_schedule"),
    path('pastweeks/', views.pastweeks, name="pastweeks")
]