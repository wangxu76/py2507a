import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'New_energy_battery.settings')
django.setup()

from station.models import BatteryStation

# 添加北京网点
BatteryStation.objects.create(
    name='中关村旗舰网点',
    address='北京市海淀区中关村大街1号',
    phone='010-12345678',
    latitude=39.9728,
    longitude=116.3272,
    description='北京最大的电池租赁站点，距离地铁2号线中关村站300米',
    business_hours='08:00-22:00',
    max_batteries=100,
    current_batteries=50,
    is_active=True
)

# 添加上海网点
BatteryStation.objects.create(
    name='浦东陆家嘴网点',
    address='上海市浦东新区世纪大道100号',
    phone='021-87654321',
    latitude=31.2293,
    longitude=121.5009,
    description='上海金融中心网点，提供专业电池租赁服务',
    business_hours='07:00-23:00',
    max_batteries=150,
    current_batteries=80,
    is_active=True
)

# 添加深圳网点
BatteryStation.objects.create(
    name='南山科技园网点',
    address='深圳市南山区高新南一路999号',
    phone='0755-12345678',
    latitude=22.5321,
    longitude=113.9321,
    description='深圳科技园网点，专业服务科技企业',
    business_hours='09:00-21:00',
    max_batteries=120,
    current_batteries=65,
    is_active=True
)

print('✅ 已成功添加3个测试网点！')
print('网点列表:')
for station in BatteryStation.objects.all():
    print(f'  - {station.name} ({station.phone})')
