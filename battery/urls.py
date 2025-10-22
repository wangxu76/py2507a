from django.urls import path
from . import views

app_name = 'battery'

urlpatterns = [
    # 电池列表和搜索
    path('', views.battery_list, name='list'),
    path('search/', views.battery_search, name='search'),
    path('categories/', views.battery_categories, name='categories'),
    path('category/<int:category_id>/', views.category_batteries, name='category_batteries'),
    
    # 电池详情
    path('detail/<int:battery_id>/', views.battery_detail, name='detail'),
    
    # 租赁相关
    path('rent/<int:battery_id>/', views.rent_battery, name='rent'),
    path('orders/', views.my_orders, name='orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # 订单操作
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/start/', views.start_order, name='start_order'),
    path('order/<int:order_id>/complete/', views.complete_order, name='complete_order'),
    path('order/<int:order_id>/confirm/', views.confirm_order, name='confirm_order'),
    
    # 使用情况
    path('usage/', views.my_battery_usage, name='usage'),
    path('usage/<int:usage_id>/update-charge/', views.update_battery_charge, name='update_charge'),
    path('usage/<int:usage_id>/toggle/', views.toggle_discharge, name='toggle_discharge'),
    
    # 评价
    path('review/<int:battery_id>/', views.add_review, name='add_review'),
    path('review/<int:review_id>/reply/', views.add_review_reply, name='add_review_reply'),
]
