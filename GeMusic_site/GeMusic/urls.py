from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('song/<str:mid>/', views.song_detail, name='song_detail'),
    path('singers/', views.singer_list, name='singer_list'),
    path('singer/<str:mid>/', views.singer_detail, name='singer_detail'),
    path('search/', views.search, name='search'),
    path('search/results/', views.search_results, name='search_results'),
]