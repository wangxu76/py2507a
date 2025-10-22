from django import forms
from .models import CustomUser
from captcha.fields import CaptchaField,CaptchaTextInput


# class UserRegisterForm(forms.ModelForm):
#     password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={
#         "class": "form-control",
#         "placeholder": "请输入密码"
#     }))
#     password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput(attrs={
#         "class": "form-control",
#         "placeholder": "请再次输入密码"
#     }))
#
#
#
#     captcha = CaptchaField(label="请输入验证码", error_messages={
#         "invalid": "验证码输入不正确",   # 关键 key 是 invalid
#         "required": "请输入验证码",
#     },
#         widget=CaptchaTextInput(attrs={
#           "class": "form-control"}))
#
#     class Meta:
#         model = CustomUser
#         fields = ['username']
#         widgets = {
#                 'username': forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": "请输入用户名"
#             }),
#
#         }
#
#     def clean_password(self):
#         password = self.cleaned_data.get('password')
#         if len(password) < 6:
#             raise forms.ValidationError("密码长度要大于6位")
#         return password
#
#     def clean_password2(self):
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password != password2:
#             raise forms.ValidationError("密码不一致")
#         return password2




#
# class UserLoginForm(forms.Form):
#     username = forms.CharField(label="用户名", widget=forms.TextInput(attrs={
#         "class": "form-control",
#         "placeholder": "请输入用户名"
#     }))
#     password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={
#         "class": "form-control",
#         "placeholder": "请输入密码"
#     }))
#

class UserRegisterForm(forms.ModelForm):

    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱'
        })
    )
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "请输入密码"
    }))
    password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "请再次输入密码"
    }))


    captcha = CaptchaField(label="验证码", error_messages={
        "invalid": "验证码输入不正确",   # 关键 key 是 invalid
        "required": "请输入验证码",
    },
        widget=CaptchaTextInput(attrs={
          "class": "form-control"}))

    class Meta:
        model = CustomUser
        fields = ['username','email']
        widgets = {
                'username': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "请输入用户名"
            }),

        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("密码长度要大于6位")
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError("密码不一致")
        return password2


class UserLoginForm(forms.Form):
    username = forms.CharField(label="用户名", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "请输入用户名"
    }))
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "请输入密码"
    }))


class UserInfoChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username','email', 'head','describe','date_joined','last_login']
        widgets = {
            'username': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "请输入用户名"
            }),
            'describe': forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "请输入个人描述",
                "rows": 3
            }),
            'head': forms.FileInput(attrs={
                'id': 'id_head'
            }),
            'date_joined': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'last_login': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'readonly': True
            })
        }
        labels = {
            'head': "头像",
            'username': "昵称",
            'email': "邮箱",
            'describe':'描述',
            'date_joined': '注册时间',
            'last_login': '上次登录时间'
        }



    def clean_head(self):
        head = self.cleaned_data.get('head')
        print(head, "0000")
        return head


class UserPassWordChangeForm(forms.Form):
    old_password = forms.CharField(label="原始密码", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "请输入密码"
    }))
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "请输入密码"
    }))
    password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "请再次输入密码"
    }))

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("密码长度要大于6位")
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError("密码不一致")
        return password2

