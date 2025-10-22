from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class BatteryCategory(models.Model):
    """电池分类模型"""
    name = models.CharField(max_length=50, verbose_name="分类名称")
    description = models.TextField(max_length=200, blank=True, verbose_name="分类描述")
    icon = models.CharField(max_length=50, default="glyphicon-flash", verbose_name="图标")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "电池分类"
        verbose_name_plural = "电池分类"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BatteryType(models.Model):
    """电池类型模型"""
    name = models.CharField(max_length=50, verbose_name="类型名称")
    category = models.ForeignKey(BatteryCategory, on_delete=models.CASCADE, verbose_name="所属分类")
    description = models.TextField(max_length=200, blank=True, verbose_name="类型描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "电池类型"
        verbose_name_plural = "电池类型"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Battery(models.Model):
    """电池信息模型"""
    STATUS_CHOICES = [
        ('available', '可用'),
        ('rented', '已租出'),
        ('maintenance', '维护中'),
        ('retired', '已退役'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name="电池名称")
    battery_type = models.ForeignKey(BatteryType, on_delete=models.CASCADE, verbose_name="电池类型")
    serial_number = models.CharField(max_length=50, unique=True, verbose_name="序列号")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="状态")
    
    # 技术参数
    capacity = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="容量(Ah)")
    voltage = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="电压(V)")
    power = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="功率(W)")
    weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="重量(kg)")
    
    # 租赁信息
    daily_rental_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="日租金(元)")
    deposit = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="押金(元)")
    
    # 位置信息
    location = models.CharField(max_length=100, verbose_name="存放位置")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="经度")
    
    # 图片
    image = models.ImageField(upload_to='battery_images/', default='', blank=True, verbose_name="电池图片")
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "电池信息"
        verbose_name_plural = "电池信息"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def full_specs(self):
        return f"{self.capacity}Ah {self.voltage}V {self.power}W"
    
    @property
    def image_number(self):
        """根据电池ID计算对应的图片编号（1-12循环）"""
        return ((self.id - 1) % 12) + 1
    
    @property
    def image_url(self):
        """生成图片URL"""
        return f"/static/img/素材{self.image_number}.jpg"


class BatteryUsage(models.Model):
    """电池使用记录模型"""
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="电池")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    current_charge = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="当前电量(%)"
    )
    # 放电控制：是否正在放电（使用中）。暂停时不消耗电量
    is_discharging = models.BooleanField(default=True, verbose_name="是否放电中")
    # 基线电量：上次开始放电时的电量，用于增量计算
    baseline_charge = models.IntegerField(default=100, verbose_name="基线电量(%)")
    total_usage_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="总使用时长(小时)")
    is_active = models.BooleanField(default=True, verbose_name="是否正在使用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "电池使用记录"
        verbose_name_plural = "电池使用记录"
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.battery.name}"
    
    def calculate_current_charge(self):
        """
        根据使用时长自动计算当前电量（仅在放电中计算）
        规则：每小时消耗10%的电量；功率越大，消耗越快
        """
        from django.utils import timezone
        
        if not self.is_active:
            return self.current_charge
        if not self.is_discharging:
            return self.current_charge
        
        # 计算已使用的小时数
        now = timezone.now()
        time_diff = now - self.start_time
        hours_used = time_diff.total_seconds() / 3600
        
        # 根据电池功率计算消耗率（功率越大，消耗越快）
        # 基础消耗率：10% / 小时
        # 根据功率调整：功率每增加1000W，消耗率增加1%
        base_consumption_rate = 10  # 基础消耗率 10%/小时
        power_factor = float(self.battery.power) / 1000  # 功率因子
        consumption_rate = base_consumption_rate * (1 + power_factor * 0.1)
        
        # 计算消耗的电量（基于基线电量）
        consumed_charge = hours_used * consumption_rate
        
        # 计算当前电量（不能低于0）
        calculated_charge = max(0, float(self.baseline_charge) - consumed_charge)
        
        return int(calculated_charge)


class RentalOrder(models.Model):
    """租赁订单模型"""
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('active', '使用中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name="订单号")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="电池")
    start_date = models.DateTimeField(verbose_name="开始时间")
    end_date = models.DateTimeField(verbose_name="结束时间")
    rental_days = models.IntegerField(verbose_name="租赁天数")
    daily_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="日租金")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="总金额")
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="押金")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="订单状态")
    notes = models.TextField(max_length=500, blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "租赁订单"
        verbose_name_plural = "租赁订单"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"订单 {self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"RENT{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class BatteryReview(models.Model):
    """电池评价模型"""
    RATING_CHOICES = [
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    ]
    
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="电池", related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="评分")
    comment = models.TextField(max_length=500, verbose_name="评价内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "电池评价"
        verbose_name_plural = "电池评价"
        ordering = ['-created_at']
        unique_together = ['battery', 'user']  # 每个用户对每个电池只能评价一次
    
    def __str__(self):
        return f"{self.user.username} - {self.battery.name} ({self.rating}星)"
    
    def reply_count(self):
        """获取回复数量"""
        return self.replies.count()


class ReviewReply(models.Model):
    """评价回复模型 - 用户可以对评价进行回复"""
    review = models.ForeignKey(BatteryReview, on_delete=models.CASCADE, verbose_name="评价", related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="回复用户")
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                                     verbose_name="父回复", related_name='child_replies')
    content = models.TextField(max_length=500, verbose_name="回复内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "评价回复"
        verbose_name_plural = "评价回复"
        ordering = ['created_at']
    
    def __str__(self):
        if self.parent_reply:
            return f"{self.user.username} 回复了 {self.parent_reply.user.username}"
        return f"{self.user.username} 回复了 {self.review.user.username} 的评价"