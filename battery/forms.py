from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Battery, BatteryCategory, BatteryType, RentalOrder, BatteryReview


class BatterySearchForm(forms.Form):
    """电池搜索表单"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索电池名称、型号或序列号...'
        }),
        label='搜索关键词'
    )
    
    category = forms.ModelChoiceField(
        queryset=BatteryCategory.objects.all(),
        required=False,
        empty_label='全部分类',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='电池分类'
    )
    
    min_price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最低价格',
            'min': '0',
            'step': '0.01'
        }),
        label='最低价格'
    )
    
    max_price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最高价格',
            'min': '0',
            'step': '0.01'
        }),
        label='最高价格'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError('最低价格不能大于最高价格')
        
        return cleaned_data


class RentalOrderForm(forms.Form):
    """租赁订单表单"""
    rental_days = forms.IntegerField(
        min_value=1,
        max_value=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '30'
        }),
        label='租赁天数'
    )
    
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='开始时间'
    )
    
    notes = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '备注信息（可选）'
        }),
        label='备注'
    )
    
    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        
        # 获取当前时间（带时区信息）
        now = timezone.now()
        
        # 开始时间不能早于当前时间
        if start_date < now:
            raise ValidationError('开始时间不能早于当前时间')
        
        # 开始时间不能超过30天后
        max_date = now + timedelta(days=30)
        if start_date > max_date:
            raise ValidationError('开始时间不能超过30天后')
        
        return start_date
    
    def clean(self):
        cleaned_data = super().clean()
        rental_days = cleaned_data.get('rental_days')
        start_date = cleaned_data.get('start_date')
        
        if rental_days and start_date:
            end_date = start_date + timedelta(days=rental_days)
            max_end_date = timezone.now() + timedelta(days=60)
            
            if end_date > max_end_date:
                raise ValidationError('租赁结束时间不能超过60天后')
        
        return cleaned_data


class BatteryReviewForm(forms.Form):
    """电池评价表单"""
    RATING_CHOICES = [
        (1, '1星 - 很差'),
        (2, '2星 - 较差'),
        (3, '3星 - 一般'),
        (4, '4星 - 较好'),
        (5, '5星 - 很好'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        label='评分'
    )
    
    comment = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': '请分享您的使用体验...'
        }),
        label='评价内容'
    )
    
    def clean_comment(self):
        comment = self.cleaned_data['comment']
        if len(comment.strip()) < 10:
            raise ValidationError('评价内容至少需要10个字符')
        return comment


class BatteryFilterForm(forms.Form):
    """电池筛选表单"""
    category = forms.ModelChoiceField(
        queryset=BatteryCategory.objects.all(),
        required=False,
        empty_label='全部分类',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='分类'
    )
    
    battery_type = forms.ModelChoiceField(
        queryset=BatteryType.objects.all(),
        required=False,
        empty_label='全部类型',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='类型'
    )
    
    min_capacity = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最小容量',
            'min': '0',
            'step': '0.01'
        }),
        label='最小容量(Ah)'
    )
    
    max_capacity = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最大容量',
            'min': '0',
            'step': '0.01'
        }),
        label='最大容量(Ah)'
    )
    
    min_voltage = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最小电压',
            'min': '0',
            'step': '0.01'
        }),
        label='最小电压(V)'
    )
    
    max_voltage = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最大电压',
            'min': '0',
            'step': '0.01'
        }),
        label='最大电压(V)'
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', '最新发布'),
            ('daily_rental_price', '价格从低到高'),
            ('-daily_rental_price', '价格从高到低'),
            ('name', '名称A-Z'),
            ('-name', '名称Z-A'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='排序方式'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_capacity = cleaned_data.get('min_capacity')
        max_capacity = cleaned_data.get('max_capacity')
        min_voltage = cleaned_data.get('min_voltage')
        max_voltage = cleaned_data.get('max_voltage')
        
        if min_capacity and max_capacity and min_capacity > max_capacity:
            raise ValidationError('最小容量不能大于最大容量')
        
        if min_voltage and max_voltage and min_voltage > max_voltage:
            raise ValidationError('最小电压不能大于最大电压')
        
        return cleaned_data
