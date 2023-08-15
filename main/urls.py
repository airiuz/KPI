from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('signup/', views.SignupPage, name="signup"),
    path('login/', views.LoginPage, name="login"),
    path('logout/', views.LogoutPage, name="logout"),
    path('book/<int:id>/', views.book, name="book_detail"),
   


    path('sport/<int:id>/', views.sport, name='sport_detail'),
    

    path('work/<int:id>/', views.work, name='work_detail'),
    path("work/<int:work_id>/increase_score/", views.work_increase_score, name='work_increase_score'),
    path("work/<int:work_id>/reset_score/", views.work_reset_score, name='work_reset_score'),
    path("work/<int:work_id>/decrease_score/", views.work_decrease_score, name='work_decrease_score'),

    path('book/<int:id>/', views.book, name='book_detail'),
       
    path('sport/<int:id>/', views.sport, name='sport_detail'),

    path('evrika/<int:id>/', views.evrika, name='evrika_detail'),

    path("all_works/", views.all_works, name='all_works'),
    path("all_books/", views.all_books, name='all_books'),
    path("all_evrika/", views.all_evrikas, name='all_evrika'),
    path("all_sports/", views.all_sports, name='all_sports'),
    path('all_meetings/', views.all_meetings, name='all_meetings'),
    
    path('reminder/', views.reminder),
    path('book_items/', views.bookItems, name='book_items'),

    path('test/', views.get_data, name='test'),

    path('kpi_create/', views.create_kpi, name='create_kpi'),
    path('kpi/', views.kpi_view, name='kpi_detail'),
    path('kpi/<int:kpi_id>/edit/', views.edit_kpi, name='edit_kpi'),
    path('kpi/<int:kpi_id>/delete/', views.delete_kpi, name='delete_kpi'),
    
    
    path('navbar/', views.Navbar, name='navbar')

]