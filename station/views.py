import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import BatteryStation, StationRental, StationReturn
from battery.models import Battery


def nearby_stations(request):
    """附近网点地图页面"""
    # 获取所有活跃的网点
    stations = BatteryStation.objects.filter(is_active=True).order_by('name')
    
    # 转换为 GeoJSON 格式（给地图使用）
    stations_data = []
    for station in stations:
        stations_data.append({
            'id': station.id,
            'name': station.name,
            'address': station.address,
            'phone': station.phone,
            'latitude': float(station.latitude),
            'longitude': float(station.longitude),
            'description': station.description,
            'business_hours': station.business_hours,
            'current_batteries': station.current_batteries,
            'max_batteries': station.max_batteries,
            'is_active': station.is_active,
        })
    
    context = {
        'stations_json': json.dumps(stations_data),
        'stations': stations,
    }
    
    return render(request, 'station/nearby_stations.html', context)


@login_required
@require_http_methods(["GET"])
def get_nearby_stations(request):
    """获取附近网点 API"""
    try:
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        radius = float(request.GET.get('radius', 5000))  # 默认 5000 米
        
        if not latitude or not longitude:
            return JsonResponse({
                'success': False,
                'message': '缺少定位信息'
            })
        
        # 获取所有网点
        stations = BatteryStation.objects.filter(is_active=True)
        nearby_stations = []
        
        for station in stations:
            # 简单的距离计算 (实际应该使用地理计算库)
            distance = calculate_distance(
                float(latitude), float(longitude),
                float(station.latitude), float(station.longitude)
            )
            
            if distance <= radius:
                nearby_stations.append({
                    'id': station.id,
                    'name': station.name,
                    'address': station.address,
                    'phone': station.phone,
                    'latitude': float(station.latitude),
                    'longitude': float(station.longitude),
                    'distance': round(distance, 2),
                    'description': station.description,
                    'business_hours': station.business_hours,
                    'current_batteries': station.current_batteries,
                    'is_active': station.is_active,
                })
        
        # 按距离排序
        nearby_stations.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'success': True,
            'data': nearby_stations,
            'count': len(nearby_stations)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两个坐标点之间的距离（米）
    使用简单的 Haversine 公式
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # 地球半径（米）
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance


@login_required
def station_detail(request, station_id):
    """网点详情页面"""
    station = get_object_or_404(BatteryStation, id=station_id, is_active=True)
    
    # 获取网点的可用电池
    available_batteries = Battery.objects.filter(status='available')[:10]
    
    # 获取用户在此网点的租赁历史
    user_rentals = StationRental.objects.filter(
        user=request.user,
        station=station
    ).order_by('-rental_date')[:5]
    
    context = {
        'station': station,
        'available_batteries': available_batteries,
        'user_rentals': user_rentals,
        'latitude': float(station.latitude),
        'longitude': float(station.longitude),
    }
    
    return render(request, 'station/station_detail.html', context)


@login_required
@require_http_methods(["POST"])
def rent_from_station(request, station_id):
    """从网点租赁电池"""
    try:
        station = get_object_or_404(BatteryStation, id=station_id, is_active=True)
        battery_id = request.POST.get('battery_id')
        rental_days = int(request.POST.get('rental_days', 1))
        
        battery = get_object_or_404(Battery, id=battery_id, status='available')
        
        # 计算租赁金额
        rental_amount = battery.daily_rental_price * rental_days
        
        # 创建租赁记录
        rental = StationRental.objects.create(
            station=station,
            user=request.user,
            battery=battery,
            rental_date=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=rental_days),
            rental_amount=rental_amount,
            status='confirmed'
        )
        
        # 更新电池状态
        battery.status = 'rented'
        battery.save()
        
        # 更新网点电池数量
        station.current_batteries += 1
        station.save()
        
        return JsonResponse({
            'success': True,
            'message': '租赁成功',
            'rental_id': rental.id
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'租赁失败: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def return_to_station(request, rental_id):
    """归还电池到网点"""
    try:
        rental = get_object_or_404(StationRental, id=rental_id, user=request.user)
        
        if rental.status == 'completed':
            return JsonResponse({
                'success': False,
                'message': '此订单已完成'
            })
        
        battery_condition = request.POST.get('battery_condition', 'good')
        return_notes = request.POST.get('notes', '')
        station = rental.station
        
        # 计算实际费用
        actual_return_date = timezone.now()
        rental.actual_return_date = actual_return_date
        
        # 计算超期费用
        days_over = max(0, (actual_return_date - rental.expected_return_date).days)
        extra_fee = Decimal(days_over) * rental.battery.daily_rental_price * Decimal('0.5')  # 超期费为日租金的50%
        
        refund_amount = rental.rental_amount
        if battery_condition == 'poor':
            refund_amount -= Decimal('50')  # 损坏扣50元
        
        refund_amount -= extra_fee
        
        # 创建归还记录
        StationReturn.objects.create(
            rental=rental,
            station=station,
            user=request.user,
            battery_condition=battery_condition,
            extra_fee=extra_fee,
            refund_amount=max(Decimal('0'), refund_amount),
            notes=return_notes
        )
        
        # 更新租赁记录状态
        rental.status = 'completed'
        rental.save()
        
        # 更新电池状态
        battery = rental.battery
        battery.status = 'available'
        battery.save()
        
        # 更新网点电池数量
        station.current_batteries -= 1
        station.save()
        
        return JsonResponse({
            'success': True,
            'message': '归还成功',
            'refund_amount': float(refund_amount)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'归还失败: {str(e)}'
        })


@login_required
def my_station_rentals(request):
    """我的网点租赁记录"""
    rentals = StationRental.objects.filter(user=request.user).order_by('-rental_date')
    
    context = {
        'rentals': rentals,
    }
    
    return render(request, 'station/my_rentals.html', context)
