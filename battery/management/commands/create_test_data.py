from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from battery.models import BatteryCategory, BatteryType, Battery, BatteryUsage, RentalOrder, BatteryReview
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = '创建电池租赁系统的测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始创建测试数据...')
        
        # 创建电池分类
        categories_data = [
            {'name': '锂电池', 'description': '高能量密度，长寿命，适用于各种设备', 'icon': 'glyphicon-flash'},
            {'name': '铅酸电池', 'description': '成本低，技术成熟，适用于储能系统', 'icon': 'glyphicon-cog'},
            {'name': '镍氢电池', 'description': '环保无污染，适用于混合动力车辆', 'icon': 'glyphicon-leaf'},
            {'name': '燃料电池', 'description': '清洁能源，零排放，未来发展方向', 'icon': 'glyphicon-fire'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = BatteryCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'创建分类: {category.name}')
        
        # 创建电池类型
        battery_types_data = [
            # 锂电池类型
            {'name': '磷酸铁锂电池', 'category': categories[0], 'description': '安全性高，循环寿命长'},
            {'name': '三元锂电池', 'category': categories[0], 'description': '能量密度高，充电速度快'},
            {'name': '钛酸锂电池', 'category': categories[0], 'description': '超长寿命，快充能力强'},
            
            # 铅酸电池类型
            {'name': 'AGM电池', 'category': categories[1], 'description': '免维护，密封性好'},
            {'name': '胶体电池', 'category': categories[1], 'description': '抗震动，深循环性能好'},
            
            # 镍氢电池类型
            {'name': '标准镍氢电池', 'category': categories[2], 'description': '环保无污染，成本适中'},
            {'name': '高容量镍氢电池', 'category': categories[2], 'description': '容量大，续航能力强'},
            
            # 燃料电池类型
            {'name': '质子交换膜燃料电池', 'category': categories[3], 'description': '效率高，启动快'},
            {'name': '固体氧化物燃料电池', 'category': categories[3], 'description': '高温运行，效率极高'},
        ]
        
        battery_types = []
        for type_data in battery_types_data:
            battery_type, created = BatteryType.objects.get_or_create(
                name=type_data['name'],
                category=type_data['category'],
                defaults=type_data
            )
            battery_types.append(battery_type)
            if created:
                self.stdout.write(f'创建电池类型: {battery_type.name}')
        
        # 创建电池
        battery_names = [
            '绿色能源电池A1', '环保动力电池B2', '高效储能电池C3', '智能电池D4', '超级电池E5',
            '新能源电池F6', '环保电池G7', '高效电池H8', '智能储能电池I9', '超级储能电池J10',
            '绿色动力电池K11', '环保储能电池L12', '高效动力电池M13', '智能动力电池N14', '超级动力电池O15',
            '新能源储能电池P16', '环保动力电池Q17', '高效储能电池R18', '智能储能电池S19', '超级储能电池T20'
        ]
        
        locations = [
            '北京朝阳区', '上海浦东新区', '深圳南山区', '广州天河区', '杭州西湖区',
            '成都高新区', '武汉东湖高新区', '西安高新区', '南京江宁区', '苏州工业园区'
        ]
        
        batteries = []
        for i, name in enumerate(battery_names):
            battery_type = random.choice(battery_types)
            
            # 根据电池类型设置不同的技术参数
            if '磷酸铁锂' in battery_type.name:
                capacity = Decimal(random.uniform(50, 100))
                voltage = Decimal(random.uniform(3.2, 3.3))
                power = capacity * voltage
                weight = Decimal(random.uniform(15, 25))
            elif '三元锂' in battery_type.name:
                capacity = Decimal(random.uniform(60, 120))
                voltage = Decimal(random.uniform(3.6, 3.7))
                power = capacity * voltage
                weight = Decimal(random.uniform(12, 20))
            elif '铅酸' in battery_type.category.name:
                capacity = Decimal(random.uniform(40, 80))
                voltage = Decimal(random.uniform(12, 12.8))
                power = capacity * voltage
                weight = Decimal(random.uniform(20, 35))
            else:
                capacity = Decimal(random.uniform(30, 70))
                voltage = Decimal(random.uniform(1.2, 1.5))
                power = capacity * voltage
                weight = Decimal(random.uniform(10, 18))
            
            battery, created = Battery.objects.get_or_create(
                name=name,
                defaults={
                    'battery_type': battery_type,
                    'serial_number': f'BAT{1000+i:04d}',
                    'status': random.choice(['available', 'available', 'available', 'rented', 'maintenance']),
                    'capacity': capacity,
                    'voltage': voltage,
                    'power': power,
                    'weight': weight,
                    'daily_rental_price': Decimal(random.uniform(50, 200)),
                    'deposit': Decimal(random.uniform(500, 2000)),
                    'location': random.choice(locations),
                    'latitude': Decimal(random.uniform(39.0, 40.0)),
                    'longitude': Decimal(random.uniform(116.0, 117.0)),
                }
            )
            batteries.append(battery)
            if created:
                self.stdout.write(f'创建电池: {battery.name}')
        
        # 创建测试用户（如果不存在）
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_active': True,
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('创建测试用户: testuser')
        
        # 创建一些使用记录
        for i in range(10):
            battery = random.choice(batteries)
            user = test_user
            
            start_time = datetime.now() - timedelta(days=random.randint(1, 30))
            end_time = start_time + timedelta(hours=random.randint(1, 72))
            
            usage, created = BatteryUsage.objects.get_or_create(
                battery=battery,
                user=user,
                start_time=start_time,
                defaults={
                    'end_time': end_time if random.choice([True, False]) else None,
                    'current_charge': random.randint(20, 100),
                    'total_usage_hours': Decimal(random.uniform(1, 72)),
                    'is_active': random.choice([True, False]),
                }
            )
            if created:
                self.stdout.write(f'创建使用记录: {usage.battery.name}')
        
        # 创建一些租赁订单
        for i in range(5):
            battery = random.choice(batteries)
            user = test_user
            
            start_date = datetime.now() + timedelta(days=random.randint(1, 7))
            rental_days = random.randint(1, 7)
            end_date = start_date + timedelta(days=rental_days)
            
            order, created = RentalOrder.objects.get_or_create(
                user=user,
                battery=battery,
                start_date=start_date,
                defaults={
                    'end_date': end_date,
                    'rental_days': rental_days,
                    'daily_price': battery.daily_rental_price,
                    'total_amount': battery.daily_rental_price * rental_days,
                    'deposit_amount': battery.deposit,
                    'status': random.choice(['pending', 'confirmed', 'active', 'completed']),
                    'notes': f'测试订单 {i+1}',
                }
            )
            if created:
                self.stdout.write(f'创建租赁订单: {order.order_number}')
        
        # 创建一些评价
        for i in range(8):
            battery = random.choice(batteries)
            user = test_user
            
            review, created = BatteryReview.objects.get_or_create(
                battery=battery,
                user=user,
                defaults={
                    'rating': random.randint(3, 5),
                    'comment': f'这个{battery.name}非常好用，性能稳定，续航能力强，强烈推荐！',
                }
            )
            if created:
                self.stdout.write(f'创建评价: {review.battery.name}')
        
        self.stdout.write(
            self.style.SUCCESS('测试数据创建完成！')
        )
        self.stdout.write(f'创建了 {len(categories)} 个分类')
        self.stdout.write(f'创建了 {len(battery_types)} 个电池类型')
        self.stdout.write(f'创建了 {len(batteries)} 个电池')
        self.stdout.write('创建了测试用户: testuser (密码: testpass123)')
