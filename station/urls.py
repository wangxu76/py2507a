from django.urls import path
from . import views

app_name = 'station'

urlpatterns = [
    # 地图和网点列表
    path('nearby/', views.nearby_stations, name='nearby'),
    path('api/nearby/', views.get_nearby_stations, name='get_nearby'),
    
    # 网点详情
    path('<int:station_id>/', views.station_detail, name='detail'),
    
    # 租赁和归还
    path('<int:station_id>/rent/', views.rent_from_station, name='rent'),
    path('rental/<int:rental_id>/return/', views.return_to_station, name='return'),
    
    # 用户记录
    path('rentals/', views.my_station_rentals, name='my_rentals'),
]
