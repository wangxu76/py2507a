from django.db import models
from django.contrib.auth import get_user_model
from battery.models import Battery
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class BatteryStation(models.Model):
    """电池租赁网点模型"""
    name = models.CharField(max_length=100, verbose_name="网点名称")
    address = models.CharField(max_length=200, verbose_name="详细地址")
    phone = models.CharField(max_length=20, verbose_name="联系电话")
    
    # 地理位置信息
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="经度")
    
    # 网点信息
    description = models.TextField(max_length=500, blank=True, verbose_name="网点描述")
    business_hours = models.CharField(max_length=50, default="09:00-21:00", verbose_name="营业时间")
    
    # 网点容量
    max_batteries = models.IntegerField(default=100, verbose_name="最大存放电池数")
    current_batteries = models.IntegerField(default=0, verbose_name="当前存放电池数")
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否营业")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "电池网点"
        verbose_name_plural = "电池网点"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StationRental(models.Model):
    """网点租赁记录模型"""
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    station = models.ForeignKey(BatteryStation, on_delete=models.CASCADE, verbose_name="网点", related_name='rentals')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", related_name='station_rentals')
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="电池")
    
    # 租赁信息
    rental_date = models.DateTimeField(verbose_name="租赁时间")
    expected_return_date = models.DateTimeField(verbose_name="预期归还时间")
    actual_return_date = models.DateTimeField(null=True, blank=True, verbose_name="实际归还时间")
    
    # 租赁金额
    rental_amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="租赁金额")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    
    # 备注
    notes = models.TextField(max_length=500, blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "网点租赁记录"
        verbose_name_plural = "网点租赁记录"
        ordering = ['-rental_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.battery.name} ({self.station.name})"


class StationReturn(models.Model):
    """网点归还记录模型"""
    rental = models.OneToOneField(StationRental, on_delete=models.CASCADE, verbose_name="租赁记录", related_name='return_record')
    station = models.ForeignKey(BatteryStation, on_delete=models.CASCADE, verbose_name="归还网点", related_name='returns')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    
    # 归还信息
    return_date = models.DateTimeField(auto_now_add=True, verbose_name="归还时间")
    battery_condition = models.CharField(
        max_length=20,
        choices=[
            ('excellent', '完好'),
            ('good', '良好'),
            ('fair', '一般'),
            ('poor', '有损坏'),
        ],
        default='good',
        verbose_name="电池状态"
    )
    
    # 费用计算
    extra_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="额外费用")
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="退款金额")
    
    notes = models.TextField(max_length=500, blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "网点归还记录"
        verbose_name_plural = "网点归还记录"
        ordering = ['-return_date']
    
    def __str__(self):
        return f"{self.user.username} 在 {self.station.name} 归还电池"
