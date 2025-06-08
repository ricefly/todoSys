from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from todo.forms import UserRegisterForm
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.contrib.auth.mixins import LoginRequiredMixin
from captcha.fields import CaptchaField
from django import forms

class RegisterView(View):
    """用户注册视图"""
    def get(self, request):
        # 生成验证码
        captcha_key = CaptchaStore.generate_key()
        captcha_image = captcha_image_url(captcha_key)
        
        return render(request, 'user/register.html', {
            'form': UserRegisterForm(),
            'captcha_key': captcha_key,
            'captcha_image': captcha_image,
        })
    
    def post(self, request):
        form = UserRegisterForm(request.POST, request.FILES)
        captcha_key = request.POST.get('captcha_key')
        captcha_response = request.POST.get('captcha')
        
        # 验证验证码
        if not CaptchaStore.objects.filter(hashkey=captcha_key).exists():
            messages.error(request, '验证码已过期，请重新获取')
            return self.get(request)
        
        captcha = CaptchaStore.objects.get(hashkey=captcha_key)
        if not captcha.response == captcha_response.lower():
            messages.error(request, '验证码错误')
            return self.get(request)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！请登录。')
            return redirect('login')
        
        # 如果表单验证失败，重新生成验证码并留在注册页面
        messages.error(request, '注册失败，请检查输入。')
        captcha_key = CaptchaStore.generate_key()
        captcha_image = captcha_image_url(captcha_key)
        
        return render(request, 'user/register.html', {
            'form': form,
            'captcha_key': captcha_key,
            'captcha_image': captcha_image,
        })

class LoginForm(forms.Form):
    """登录表单"""
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )
    captcha = CaptchaField(
        label='验证码',
        error_messages={
            'invalid': '验证码错误'
        }
    )

class LoginView(View):
    """登录视图"""
    template_name = 'user/login.html'
    
    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('home')
            else:
                messages.error(request, '用户名或密码错误！')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
        
        return render(request, self.template_name, {'form': form})

def logout_view(request):
    """用户登出视图"""
    logout(request)
    messages.success(request, '您已成功退出登录！')
    return redirect('login')

class ProfileView(LoginRequiredMixin, View):
    """个人资料视图"""
    template_name = 'user/profile.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        user = request.user
        email = request.POST.get('email')
        avatar = request.FILES.get('avatar')
        
        # 更新邮箱
        if email and email != user.email:
            user.email = email
        
        # 更新头像
        if avatar:
            user.avatar = avatar
        
        try:
            user.save()
            messages.success(request, '个人资料更新成功！')
        except Exception as e:
            messages.error(request, f'更新失败：{str(e)}')
        
        return redirect('profile')

@method_decorator(login_required, name='dispatch')
class PasswordChangeView(View):
    """修改密码视图"""
    def get(self, request):
        return render(request, 'user/password_change.html', {
            'form': PasswordChangeForm(request.user)
        })
    
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # 更新密码后重新登录
            login(request, user)
            messages.success(request, '密码修改成功！')
            return redirect('profile')
        return render(request, 'user/password_change.html', {
            'form': form
        })
