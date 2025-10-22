from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone
import uuid

from .models import Battery, BatteryCategory, BatteryType, BatteryUsage, RentalOrder, BatteryReview, ReviewReply
from .forms import BatterySearchForm, RentalOrderForm, BatteryReviewForm
from user.models import UserPoints


def battery_list(request):
    """电池列表页面"""
    # 获取筛选参数
    category_id = request.GET.get('category')
    battery_type_id = request.GET.get('type')
    search_query = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    status = request.GET.get('status', 'available')
    
    # 构建查询
    batteries = Battery.objects.filter(status=status)
    
    if category_id:
        batteries = batteries.filter(battery_type__category_id=category_id)
    
    if battery_type_id:
        batteries = batteries.filter(battery_type_id=battery_type_id)
    
    if search_query:
        batteries = batteries.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(battery_type__name__icontains=search_query)
        )
    
    if min_price:
        batteries = batteries.filter(daily_rental_price__gte=min_price)
    
    if max_price:
        batteries = batteries.filter(daily_rental_price__lte=max_price)
    
    # 分页
    paginator = Paginator(batteries, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取筛选选项
    categories = BatteryCategory.objects.all()
    battery_types = BatteryType.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'battery_types': battery_types,
        'current_category': category_id,
        'current_type': battery_type_id,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'status': status,
    }
    
    return render(request, 'battery/battery_list.html', context)


def battery_detail(request, battery_id):
    """电池详情页面"""
    battery = get_object_or_404(Battery, id=battery_id)
    
    # 获取相关电池（同类型）
    related_batteries = Battery.objects.filter(
        battery_type=battery.battery_type,
        status='available'
    ).exclude(id=battery_id)[:4]
    
    # 获取评价
    reviews = BatteryReview.objects.filter(battery=battery).order_by('-created_at')[:10]
    avg_rating = BatteryReview.objects.filter(battery=battery).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    
    # 获取使用统计
    usage_stats = BatteryUsage.objects.filter(battery=battery).aggregate(
        total_usage=Count('id'),
        avg_charge=Avg('current_charge')
    )
    
    context = {
        'battery': battery,
        'related_batteries': related_batteries,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'usage_stats': usage_stats,
    }
    
    return render(request, 'battery/battery_detail.html', context)


@login_required
def rent_battery(request, battery_id):
    """租赁电池"""
    battery = get_object_or_404(Battery, id=battery_id)
    
    if not battery.is_available:
        messages.error(request, '该电池当前不可租赁')
        return redirect('battery:detail', battery_id=battery_id)
    
    if request.method == 'POST':
        form = RentalOrderForm(request.POST)
        if form.is_valid():
            # 创建租赁订单
            rental_days = form.cleaned_data['rental_days']
            start_date = form.cleaned_data['start_date']
            end_date = start_date + timedelta(days=rental_days)
            
            order = RentalOrder.objects.create(
                user=request.user,
                battery=battery,
                start_date=start_date,
                end_date=end_date,
                rental_days=rental_days,
                daily_price=battery.daily_rental_price,
                total_amount=battery.daily_rental_price * rental_days,
                deposit_amount=battery.deposit,
                status='pending'
            )
            
            # 租赁订单奖励积分
            from user.views import add_points
            add_points(request.user, 10, 'earn', '创建租赁订单', f'创建租赁订单 {order.order_number} 获得积分奖励')
            
            messages.success(request, f'租赁申请已提交，订单号：{order.order_number}')
            return redirect('battery:order_detail', order_id=order.id)
    else:
        form = RentalOrderForm()
    
    context = {
        'battery': battery,
        'form': form,
    }
    
    return render(request, 'battery/rent_battery.html', context)


@login_required
def my_orders(request):
    """我的订单"""
    orders = RentalOrder.objects.filter(user=request.user).order_by('-created_at')
    
    # 分页
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_count': orders.count(),
        'active_count': orders.filter(status='active').count(),
        'completed_count': orders.filter(status='completed').count(),
    }
    
    return render(request, 'battery/my_orders.html', context)


@login_required
def order_detail(request, order_id):
    """订单详情"""
    order = get_object_or_404(RentalOrder, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'battery/order_detail.html', context)


@login_required
def my_battery_usage(request):
    """我的电池使用情况"""
    # 获取当前用户正在使用的电池
    active_usage = BatteryUsage.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    # 如果有正在使用的电池，更新其电量和使用时长（仅放电时）
    if active_usage:
        time_diff = timezone.now() - active_usage.start_time
        active_usage.total_usage_hours = round(time_diff.total_seconds() / 3600, 2)
        if active_usage.is_discharging:
            calculated_charge = active_usage.calculate_current_charge()
            active_usage.current_charge = calculated_charge
            # 0% 自动结束
            if active_usage.current_charge <= 0:
                active_usage.is_active = False
                active_usage.end_time = timezone.now()
                active_usage.save()
                # 完成对应订单
                order = RentalOrder.objects.filter(user=request.user, battery=active_usage.battery, status='active').first()
                if order:
                    order.status = 'completed'
                    order.save()
            else:
                active_usage.save()
    
    # 获取历史使用记录
    usage_history = BatteryUsage.objects.filter(
        user=request.user
    ).order_by('-start_time')
    
    # 分页
    paginator = Paginator(usage_history, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_usage': active_usage,
        'page_obj': page_obj,
    }
    
    return render(request, 'battery/my_usage.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_discharge(request, usage_id):
    """开始/停止放电切换，停止时不再消耗电量；开始时重置基线"""
    usage = get_object_or_404(BatteryUsage, id=usage_id, user=request.user, is_active=True)
    action = request.POST.get('action')  # 'start' or 'stop'
    now = timezone.now()

    if action == 'stop':
        usage.is_discharging = False
        usage.save()
        return JsonResponse({'success': True, 'is_discharging': usage.is_discharging})
    elif action == 'start':
        # 重置起算点
        usage.start_time = now
        usage.baseline_charge = usage.current_charge
        usage.is_discharging = True
        usage.save()
        return JsonResponse({'success': True, 'is_discharging': usage.is_discharging})

    return JsonResponse({'success': False, 'error': '无效操作'})


@login_required
@require_http_methods(["POST"])
def update_battery_charge(request, usage_id):
    """更新电池电量"""
    usage = get_object_or_404(BatteryUsage, id=usage_id, user=request.user, is_active=True)
    
    new_charge = request.POST.get('charge')
    if new_charge:
        try:
            charge = int(new_charge)
            if 0 <= charge <= 100:
                usage.current_charge = charge
                usage.save()
                return JsonResponse({'success': True, 'charge': charge})
        except ValueError:
            pass
    
    return JsonResponse({'success': False, 'error': '无效的电量值'})


@login_required
def battery_categories(request):
    """电池分类页面"""
    categories = BatteryCategory.objects.annotate(
        battery_count=Count('batterytype__battery')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'battery/categories.html', context)


def category_batteries(request, category_id):
    """分类下的电池列表"""
    category = get_object_or_404(BatteryCategory, id=category_id)
    batteries = Battery.objects.filter(
        battery_type__category=category,
        status='available'
    ).order_by('-created_at')
    
    # 分页
    paginator = Paginator(batteries, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'battery/category_batteries.html', context)


@login_required
def add_review(request, battery_id):
    """添加电池评价"""
    battery = get_object_or_404(Battery, id=battery_id)
    
    # 检查用户是否已经评价过
    existing_review = BatteryReview.objects.filter(
        battery=battery,
        user=request.user
    ).first()
    
    if request.method == 'POST':
        form = BatteryReviewForm(request.POST)
        if form.is_valid():
            if existing_review:
                # 更新现有评价
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.save()
                messages.success(request, '评价已更新')
            else:
                # 创建新评价
                BatteryReview.objects.create(
                    battery=battery,
                    user=request.user,
                    rating=form.cleaned_data['rating'],
                    comment=form.cleaned_data['comment']
                )
                
                # 评价奖励积分
                from user.views import add_points
                add_points(request.user, 15, 'earn', '发表电池评价', f'对电池 {battery.name} 发表评价获得积分奖励')
                
                messages.success(request, '评价已提交')
            
            return redirect('battery:detail', battery_id=battery_id)
    else:
        if existing_review:
            form = BatteryReviewForm(initial={
                'rating': existing_review.rating,
                'comment': existing_review.comment
            })
        else:
            form = BatteryReviewForm()
    
    context = {
        'battery': battery,
        'form': form,
        'existing_review': existing_review,
    }
    
    return render(request, 'battery/add_review.html', context)


def battery_search(request):
    """电池搜索页面"""
    form = BatterySearchForm(request.GET)
    batteries = []
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        
        batteries = Battery.objects.filter(status='available')
        
        if search_query:
            batteries = batteries.filter(
                Q(name__icontains=search_query) |
                Q(serial_number__icontains=search_query) |
                Q(battery_type__name__icontains=search_query)
            )
        
        if category:
            batteries = batteries.filter(battery_type__category=category)
        
        if min_price:
            batteries = batteries.filter(daily_rental_price__gte=min_price)
        
        if max_price:
            batteries = batteries.filter(daily_rental_price__lte=max_price)
        
        batteries = batteries.order_by('-created_at')
    
    # 分页
    paginator = Paginator(batteries, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
    }
    
    return render(request, 'battery/search.html', context)


@login_required
@require_http_methods(["POST"])
def add_review_reply(request, review_id):
    """添加评论回复"""
    review = get_object_or_404(BatteryReview, id=review_id)
    content = request.POST.get('content', '').strip()
    parent_reply_id = request.POST.get('parent_reply_id')
    
    if not content:
        return JsonResponse({
            'success': False,
            'error': '回复内容不能为空'
        })
    
    if len(content) < 2:
        return JsonResponse({
            'success': False,
            'error': '回复内容至少需要2个字符'
        })
    
    # 创建回复
    reply_data = {
        'review': review,
        'user': request.user,
        'content': content
    }
    
    parent_reply = None
    # 如果是回复其他人的回复
    if parent_reply_id:
        parent_reply = get_object_or_404(ReviewReply, id=parent_reply_id)
        reply_data['parent_reply'] = parent_reply
    
    reply = ReviewReply.objects.create(**reply_data)
    
    # 返回新回复的HTML
    reply_to_html = f'<span class="reply-to">回复 @{parent_reply.user.username}</span>' if parent_reply else ''
    reply_html = f"""
    <div class="reply-item" id="reply-{reply.id}">
        <div class="reply-header">
            <div class="reply-user">
                <i class="glyphicon glyphicon-user"></i>
                <strong>{reply.user.username}</strong>
                {reply_to_html}
            </div>
            <span class="reply-date">{reply.created_at.strftime('%Y-%m-%d %H:%M')}</span>
        </div>
        <div class="reply-content">{reply.content}</div>
        <div class="reply-actions">
            <button class="btn-reply-to-reply" onclick="replyToReply({review.id}, {reply.id}, '{reply.user.username}')">
                <i class="glyphicon glyphicon-share-alt"></i> 回复
            </button>
        </div>
    </div>
    """
    
    return JsonResponse({
        'success': True,
        'message': '回复成功',
        'reply_html': reply_html,
        'reply_count': review.reply_count()
    })


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """取消订单"""
    order = get_object_or_404(RentalOrder, id=order_id, user=request.user)
    
    if order.status != 'pending':
        return JsonResponse({
            'success': False,
            'error': '只能取消待确认的订单'
        })
    
    # 更新订单状态
    order.status = 'cancelled'
    order.save()
    
    messages.success(request, '订单已取消')
    return JsonResponse({
        'success': True,
        'message': '订单已取消'
    })


@login_required
@require_http_methods(["POST"])
def start_order(request, order_id):
    """开始使用订单（将订单状态从已确认改为使用中）"""
    order = get_object_or_404(RentalOrder, id=order_id, user=request.user)
    
    if order.status != 'confirmed':
        return JsonResponse({
            'success': False,
            'error': '只能开始已确认的订单'
        })
    
    # 检查用户是否已经有正在使用的电池
    active_usage = BatteryUsage.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if active_usage:
        return JsonResponse({
            'success': False,
            'error': f'您当前正在使用 {active_usage.battery.name}，请先结束当前电池的使用后再开始新的租赁'
        })
    
    # 更新订单状态
    order.status = 'active'
    order.save()
    
    # 更新电池状态为已租出
    battery = order.battery
    battery.status = 'rented'
    battery.save()
    
    # 创建电池使用记录
    BatteryUsage.objects.create(
        battery=battery,
        user=request.user,
        start_time=timezone.now(),
        current_charge=100,  # 假设初始电量为100%
        is_active=True
    )
    
    messages.success(request, '已开始使用电池')
    return JsonResponse({
        'success': True,
        'message': '已开始使用电池'
    })


@login_required
@require_http_methods(["POST"])
def complete_order(request, order_id):
    """完成租赁（结算订单）"""
    order = get_object_or_404(RentalOrder, id=order_id, user=request.user)
    
    if order.status != 'active':
        return JsonResponse({
            'success': False,
            'error': '只能完成使用中的订单'
        })
    
    # 更新订单状态
    order.status = 'completed'
    order.save()
    
    # 完成订单奖励积分
    from user.views import add_points
    add_points(request.user, 20, 'earn', '完成租赁订单', f'完成租赁订单 {order.order_number} 获得积分奖励')
    
    # 更新电池状态为可用
    battery = order.battery
    battery.status = 'available'
    battery.save()
    
    # 结束电池使用记录
    active_usage = BatteryUsage.objects.filter(
        battery=battery,
        user=request.user,
        is_active=True
    ).first()
    
    if active_usage:
        active_usage.end_time = timezone.now()
        active_usage.is_active = False
        # 计算总使用时长
        time_diff = active_usage.end_time - active_usage.start_time
        active_usage.total_usage_hours = time_diff.total_seconds() / 3600
        active_usage.save()
    
    messages.success(request, f'租赁已完成！押金 ¥{order.deposit_amount} 将在3-5个工作日内退还')
    return JsonResponse({
        'success': True,
        'message': f'租赁已完成！押金 ¥{order.deposit_amount} 将在3-5个工作日内退还',
        'deposit': float(order.deposit_amount)
    })


@login_required
@require_http_methods(["POST"])
def confirm_order(request, order_id):
    """确认订单（管理员操作，这里允许用户自己确认用于测试）"""
    order = get_object_or_404(RentalOrder, id=order_id, user=request.user)
    
    if order.status != 'pending':
        return JsonResponse({
            'success': False,
            'error': '只能确认待确认的订单'
        })
    
    # 更新订单状态
    order.status = 'confirmed'
    order.save()
    
    messages.success(request, '订单已确认')
    return JsonResponse({
        'success': True,
        'message': '订单已确认'
    })