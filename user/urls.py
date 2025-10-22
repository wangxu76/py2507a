
from django.contrib import admin
from django.urls import path
from .views import (
    index, register, login, active, center, logout, change_password,
    toggle_favorite, favorites_list, check_favorite_status, profile_edit, preference_edit,
    points_history, messages_list, message_detail, mark_message_read
)
app_name = 'user'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('active/<int:id>/', active, name='active'),
    path('center/', center, name='center'),
    path('logout/', logout, name='logout'),
    path('change_password/', change_password, name='change_password'),
    
    # 新增功能路由
    path('favorite/<int:battery_id>/', toggle_favorite, name='toggle_favorite'),
    path('favorite/<int:battery_id>/status/', check_favorite_status, name='check_favorite_status'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('profile/', profile_edit, name='profile_edit'),
    path('preference/', preference_edit, name='preference_edit'),
    path('points/', points_history, name='points_history'),
    path('messages/', messages_list, name='messages_list'),
    path('messages/<int:message_id>/', message_detail, name='message_detail'),
    path('messages/<int:message_id>/read/', mark_message_read, name='mark_message_read'),
]