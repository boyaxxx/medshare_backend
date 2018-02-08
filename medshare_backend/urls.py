"""medshare_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from analysis import views


urlpatterns = [
    path('compute_news_hot', views.compute_news_hot),
    path('compute_users_hot', views.compute_users_hot),
    path('get_transmit_tree', views.get_transmit_tree),
    path('find_important_user', views.find_important_user),
    path('find_important_path', views.find_important_path),
    path('get_latest_news', views.get_latest_news),
    path('get_latest_users', views.get_latest_users),
    path('get_latest_news/<int:top>', views.get_latest_news),
    path('get_latest_users/<int:top>', views.get_latest_users),
    path('get_user_log/<str:viewer_id>/<int:top>', views.get_user_log),
    path('get_total_transmit_number', views.get_total_transmit_number),
    path('get_total_transmit_number/<int:top>', views.get_total_transmit_number),
    path('get_total_read_number', views.get_total_read_number),
    path('get_total_read_number/<int:top>', views.get_total_read_number),
    path('get_total_user_number', views.get_total_user_number),
    path('get_total_user_number/<int:top>', views.get_total_user_number),
    path('get_user_number', views.get_user_number),
    path('get_user_number/<int:top>', views.get_user_number),
    path('get_user_area', views.get_user_area),
    re_path(r'^$', views.index)
]
