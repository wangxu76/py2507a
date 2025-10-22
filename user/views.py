from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect,reverse

from django.contrib.auth.views import auth_login, auth_logout

from user.forms import UserRegisterForm, UserLoginForm, UserInfoChangeForm, UserPassWordChangeForm
from user.models import CustomUser, UserProfile, UserPreference, UserPoints, UserMessage, UserLoginLog, UserFavorite
from django.contrib.auth import login as lgi, logout as lgo
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.

@login_required(login_url='user:login')
def index(request):
    return render(request, 'user/index.html')
def register(request):
    if request.method == "POST":
        rf = UserRegisterForm(request.POST)
        if rf.is_valid():
            user = rf.save(commit=False)
            user.set_password(rf.cleaned_data['password'])

            user.is_active = False
            user.is_staff = True
            user.is_superuser = True
            user.email = rf.cleaned_data['email']
            user.save()
            url =request.build_absolute_uri(reverse('user:active', args=[user.id]))
            user.email_user("激活账户", message="", html_message=f"<a href='{url}'>点我激活账户</a>")
            return redirect(reverse('user:login'))
        else:
            return render(request, 'user/register.html', {"form": rf})
    else:
        rf = UserRegisterForm()
        return render(request, 'user/register.html', {"form": rf})

def login(request):
    if request.method == "POST":
        lf = UserLoginForm(request.POST)
        if lf.is_valid():
            user = CustomUser.objects.filter(username=lf.cleaned_data['username']).first() or CustomUser.objects.filter(email=lf.cleaned_data['username']).first()
            if user:
                if user.check_password(lf.cleaned_data['password']):
                    if user.is_active:
                        auth_login(request, user)
                        # 记录登录日志
                        log_user_login(user, request)
                        # 发送欢迎消息
                        send_message_to_user(user, 'system', '欢迎回来！', f'欢迎回来，{user.username}！感谢您的使用。')
                        
                        next_url = request.GET.get('next')
                        if next_url:
                            return redirect(next_url)
                        else:
                            return redirect(reverse('user:index'))
                    else:
                        lf.add_error("username", "该用户尚未激活")
                        return render(request, 'user/login.html', {"form": lf})
                else:
                    lf.add_error("password", "密码错误")
                    return render(request, 'user/login.html', {"form": lf})
            else:
                lf.add_error("username", "用户名不存在")
                return render(request, 'user/login.html', {"form": lf})
        else:

            return render(request, 'user/login.html', {"form": lf})

    else:
        lf = UserLoginForm()
        return render(request, 'user/login.html', {"form": lf})


def logout(request):
    auth_logout(request)
    return redirect(reverse('user:login'))


@login_required(login_url='user:login')
def center(request):
    from datetime import datetime
    if request.method == 'POST':
        cuif = UserInfoChangeForm(data=request.POST, files=request.FILES, instance=request.user)
        if cuif.is_valid():
            cuif.save()
            return redirect(reverse('user:center'))
        else:
            cuif = UserInfoChangeForm(initial={
                "username": request.user.username,
                "email":request.user.email,
                "describe": request.user.describe,
                "date_joined": request.user.date_joined,
                "last_login": request.user.last_login
            })
            return render(request, 'user/center.html', {'form':cuif,'data':[1,2,3,4,5],'datetime':datetime.now(),'users':CustomUser.objects.all()})
    else:
        cuif = UserInfoChangeForm(initial={
            "username": request.user.username,
            "email": request.user.email,
            "describe": request.user.describe,
            "date_joined": request.user.date_joined,
            "last_login": request.user.last_login
        })
        return render(request, 'user/center.html', {'form':cuif,'data':[1,2,3,4,5],'datetime':datetime.now()})
def change_password(request):
    if request.method == 'POST':
        cgf = UserPassWordChangeForm(request.POST)
        if cgf.is_valid():
            if request.user.check_password(cgf.cleaned_data['old_password']):
                request.user.set_password(cgf.cleaned_data['password'])
                request.user.save()

                # 修改密码从新登录
                auth_logout(request)
                return redirect(reverse('user:login'))
            else:
                cgf.add_error("old_password", "原始密码不正确")
                return render(request, 'user/change_password.html', {"form": cgf})
        else:
            return render(request, 'user/change_password.html', {"form": cgf})
    else:
        cgf = UserPassWordChangeForm()
        return render(request, 'user/change_password.html', {"form": cgf})


def active(request, id):
    user = CustomUser.objects.get(id=id)
    if user:
        user.is_active = True
        user.save()
        return redirect(reverse('user:login'))
    else:
        return HttpResponse("激活失败")


# 收藏功能
# @csrf_exempt
# @login_required(login_url='user:login')
# def toggle_favorite(request, battery_id):
#     """切换电池收藏状态"""
#     if request.method == 'POST':
#         try:
#             # 获取电池信息（需要导入battery模型）
#             from battery.models import Battery
#             battery = Battery.objects.get(id=battery_id)
#
#             favorite, created = UserFavorite.objects.get_or_create(
#                 user=request.user,
#                 battery_id=battery_id,
#                 defaults={'battery_name': battery.name}
#             )
#
#             if not created:
#                 # 如果已存在，则取消收藏
#                 favorite.delete()
#                 is_favorited = False
#                 message = "已取消收藏"
#             else:
#                 # 新增收藏
#                 is_favorited = True
#                 message = "收藏成功"
#
#             return JsonResponse({
#                 'success': True,
#                 'is_favorited': is_favorited,
#                 'message': message
#             })
#         except Exception as e:
#             print(f"收藏操作错误: {e}")
#             return JsonResponse({
#                 'success': False,
#                 'message': f'操作失败: {str(e)}'
#             })
#
#     return JsonResponse({'success': False, 'message': '请求方法错误'})

@csrf_exempt
@login_required(login_url='user:login')
def toggle_favorite(request, battery_id):
    """切换电池收藏状态"""
    if request.method == 'POST':
        try:
            from battery.models import Battery

            battery = Battery.objects.get(id=battery_id)

            favorite, created = UserFavorite.objects.get_or_create(
                user=request.user,
                battery_id=battery_id,
                defaults={'battery_name': battery.name}
            )

            if not created:
                favorite.delete()
                is_favorited = False
                message = "已取消收藏"
            else:
                is_favorited = True
                message = "收藏成功"

            return JsonResponse({
                'success': True,
                'is_favorited': is_favorited,
                'message': message
            })
        except Exception as e:
            print(f"收藏操作错误: {e}")
            return JsonResponse({
                'success': False,
                'message': f'操作失败: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': '请求方法错误'})






@login_required(login_url='user:login')
def favorites_list(request):
    """收藏列表页面"""
    from battery.models import Battery
    
    # 获取用户的收藏记录
    favorites = UserFavorite.objects.filter(user=request.user).order_by('-created_at')
    
    # 为每个收藏记录获取完整的电池信息
    favorites_with_battery = []
    for favorite in favorites:
        try:
            battery = Battery.objects.get(id=favorite.battery_id)
            favorites_with_battery.append({
                'favorite': favorite,
                'battery': battery
            })
        except Battery.DoesNotExist:
            # 如果电池已删除，跳过
            pass
    
    return render(request, 'user/favorites.html', {'favorites_with_battery': favorites_with_battery})


@csrf_exempt
@login_required(login_url='user:login')
def check_favorite_status(request, battery_id):
    """检查电池收藏状态"""
    try:
        favorite = UserFavorite.objects.filter(user=request.user, battery_id=battery_id).first()
        return JsonResponse({
            'success': True,
            'is_favorited': favorite is not None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '检查失败'
        })


# 用户资料管理
@login_required(login_url='user:login')
def profile_edit(request):
    """用户资料编辑"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # 这里可以添加ProfileForm，暂时用简单的方式处理
        profile.gender = request.POST.get('gender', '')
        profile.birthday = request.POST.get('birthday') or None
        profile.address = request.POST.get('address', '')
        profile.emergency_contact = request.POST.get('emergency_contact', '')
        profile.emergency_phone = request.POST.get('emergency_phone', '')
        profile.occupation = request.POST.get('occupation', '')
        profile.company = request.POST.get('company', '')
        profile.save()
        
        messages.success(request, '资料更新成功')
        return redirect('user:profile_edit')
    
    return render(request, 'user/profile_edit.html', {'profile': profile})


# 用户偏好设置
@login_required(login_url='user:login')
def preference_edit(request):
    """用户偏好设置"""
    preference, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        preference.language = request.POST.get('language', 'zh')
        preference.theme = request.POST.get('theme', 'light')
        preference.email_notifications = request.POST.get('email_notifications') == 'on'
        preference.sms_notifications = request.POST.get('sms_notifications') == 'on'
        preference.auto_renewal = request.POST.get('auto_renewal') == 'on'
        preference.preferred_battery_type = request.POST.get('preferred_battery_type', '')
        preference.max_daily_rental = request.POST.get('max_daily_rental', 100.0)
        preference.save()
        
        messages.success(request, '偏好设置已保存')
        return redirect('user:preference_edit')
    
    return render(request, 'user/preference_edit.html', {'preference': preference})


# 积分系统
@login_required(login_url='user:login')
def points_history(request):
    """积分记录页面"""
    points_records = UserPoints.objects.filter(user=request.user).order_by('-created_at')
    
    # 计算总积分
    total_points = sum(record.points for record in points_records if record.point_type == 'earn')
    spent_points = sum(abs(record.points) for record in points_records if record.point_type == 'spend')
    current_points = total_points - spent_points
    
    return render(request, 'user/points_history.html', {
        'points_records': points_records,
        'total_points': total_points,
        'spent_points': spent_points,
        'current_points': current_points
    })


def add_points(user, points, point_type, reason, description=''):
    """添加积分记录"""
    with transaction.atomic():
        # 计算当前积分余额
        earned = sum(record.points for record in user.points_records.filter(point_type='earn'))
        spent = sum(abs(record.points) for record in user.points_records.filter(point_type='spend'))
        current_balance = earned - spent
        
        # 创建积分记录
        UserPoints.objects.create(
            user=user,
            points=points,
            point_type=point_type,
            reason=reason,
            description=description,
            balance_after=current_balance + points if point_type == 'earn' else current_balance - abs(points)
        )


# 消息系统
@login_required(login_url='user:login')
def messages_list(request):
    """消息列表"""
    user_messages = UserMessage.objects.filter(user=request.user).order_by('-created_at')
    
    # 统计未读消息
    unread_count = user_messages.filter(is_read=False).count()
    
    return render(request, 'user/messages.html', {
        'messages': user_messages,
        'unread_count': unread_count
    })


@login_required(login_url='user:login')
def message_detail(request, message_id):
    """消息详情"""
    try:
        message = UserMessage.objects.get(id=message_id, user=request.user)
        
        # 标记为已读
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        return render(request, 'user/message_detail.html', {'message': message})
    except UserMessage.DoesNotExist:
        return HttpResponse("消息不存在")


@login_required(login_url='user:login')
def mark_message_read(request, message_id):
    """标记消息为已读"""
    if request.method == 'POST':
        try:
            message = UserMessage.objects.get(id=message_id, user=request.user)
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
            return JsonResponse({'success': True})
        except UserMessage.DoesNotExist:
            return JsonResponse({'success': False, 'message': '消息不存在'})
    
    return JsonResponse({'success': False, 'message': '请求方法错误'})


# 登录日志
def log_user_login(user, request):
    """记录用户登录"""
    try:
        UserLoginLog.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_successful=True
        )
    except Exception as e:
        print(f"记录登录日志失败: {e}")


def get_client_ip(request):
    """获取客户端IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# 发送消息
def send_message_to_user(user, message_type, title, content, is_important=False):
    """给用户发送消息"""
    UserMessage.objects.create(
        user=user,
        message_type=message_type,
        title=title,
        content=content,
        is_important=is_important
    )