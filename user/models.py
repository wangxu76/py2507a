from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class CustomUser(AbstractUser):
    head = models.ImageField(upload_to="head/", default="head/default.jpg")
    describe = models.TextField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="账户余额")
    credit_score = models.IntegerField(
        default=100, 
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        verbose_name="信用分"
    )
    is_verified = models.BooleanField(default=False, verbose_name="是否实名认证")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="注册时间")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """用户详细资料模型"""
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="用户", related_name='profile')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="性别")
    birthday = models.DateField(null=True, blank=True, verbose_name="生日")
    address = models.TextField(max_length=200, blank=True, verbose_name="地址")
    emergency_contact = models.CharField(max_length=50, blank=True, verbose_name="紧急联系人")
    emergency_phone = models.CharField(max_length=11, blank=True, verbose_name="紧急联系电话")
    id_card = models.CharField(max_length=18, blank=True, verbose_name="身份证号")
    occupation = models.CharField(max_length=50, blank=True, verbose_name="职业")
    company = models.CharField(max_length=100, blank=True, verbose_name="公司")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 的资料"


class UserPreference(models.Model):
    """用户偏好设置模型"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="用户", related_name='preference')
    language = models.CharField(max_length=10, default='zh', verbose_name="语言偏好")
    theme = models.CharField(max_length=20, default='light', verbose_name="主题偏好")
    email_notifications = models.BooleanField(default=True, verbose_name="邮件通知")
    sms_notifications = models.BooleanField(default=True, verbose_name="短信通知")
    auto_renewal = models.BooleanField(default=False, verbose_name="自动续租")
    preferred_battery_type = models.CharField(max_length=50, blank=True, verbose_name="偏好电池类型")
    max_daily_rental = models.DecimalField(max_digits=8, decimal_places=2, default=100.0, verbose_name="最大日租金限制")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户偏好"
        verbose_name_plural = "用户偏好"
    
    def __str__(self):
        return f"{self.user.username} 的偏好设置"


class UserPoints(models.Model):
    """用户积分记录模型"""
    POINT_TYPES = [
        ('earn', '获得'),
        ('spend', '消费'),
        ('expire', '过期'),
        ('refund', '退款'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户", related_name='points_records')
    points = models.IntegerField(verbose_name="积分数量")
    point_type = models.CharField(max_length=10, choices=POINT_TYPES, verbose_name="积分类型")
    reason = models.CharField(max_length=100, verbose_name="积分原因")
    description = models.TextField(max_length=200, blank=True, verbose_name="详细说明")
    balance_after = models.IntegerField(verbose_name="操作后余额")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "积分记录"
        verbose_name_plural = "积分记录"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.point_type} {self.points}分"


class UserMessage(models.Model):
    """用户消息模型"""
    MESSAGE_TYPES = [
        ('system', '系统消息'),
        ('notification', '通知消息'),
        ('promotion', '推广消息'),
        ('reminder', '提醒消息'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户", related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name="消息类型")
    title = models.CharField(max_length=100, verbose_name="消息标题")
    content = models.TextField(verbose_name="消息内容")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    is_important = models.BooleanField(default=False, verbose_name="是否重要")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="阅读时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "用户消息"
        verbose_name_plural = "用户消息"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class UserLoginLog(models.Model):
    """用户登录日志模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户", related_name='login_logs')
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    user_agent = models.TextField(verbose_name="用户代理")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="登录时间")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="登出时间")
    is_successful = models.BooleanField(default=True, verbose_name="登录成功")
    failure_reason = models.CharField(max_length=100, blank=True, verbose_name="失败原因")
    
    class Meta:
        verbose_name = "登录日志"
        verbose_name_plural = "登录日志"
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"


class UserFavorite(models.Model):
    """用户收藏模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户", related_name='favorites')
    battery_id = models.IntegerField(verbose_name="电池ID")  # 关联battery模块的电池
    battery_name = models.CharField(max_length=100, verbose_name="电池名称")  # 冗余存储，避免跨模块查询
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")
    
    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = "用户收藏"
        ordering = ['-created_at']
        unique_together = ['user', 'battery_id']  # 每个用户对每个电池只能收藏一次
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.battery_name}"