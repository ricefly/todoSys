from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Category, Task

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True, label='邮箱')
    avatar = forms.ImageField(required=False, label='头像')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定义表单字段的标签和帮助文本
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        self.fields['username'].help_text = '必填。150个字符或更少。只能包含字母、数字和 @/./+/-/_ 符号。'
        self.fields['password1'].help_text = '密码必须包含至少8个字符，不能是纯数字，不能与用户名相似。'
        self.fields['password2'].help_text = '请再次输入密码以确认。'

class UserLoginForm(forms.Form):
    """用户登录表单"""
    username = forms.CharField(label='用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    captcha = forms.CharField(label='验证码', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['captcha'].widget.attrs.update({'class': 'form-control'})

class CategoryForm(forms.ModelForm):
    """分类表单"""
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].label = '分类名称'
        self.fields['color'].label = '分类颜色'

    def clean_name(self):
        name = self.cleaned_data['name']
        if Category.objects.filter(user=self.user, name=name).exists():
            raise forms.ValidationError('该分类名称已存在')
        return name

class TaskForm(forms.ModelForm):
    """任务表单"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date', 'priority', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # 只显示当前用户的分类
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
        # 设置字段标签
        self.fields['title'].label = '标题'
        self.fields['description'].label = '描述'
        self.fields['status'].label = '状态'
        self.fields['due_date'].label = '截止日期'
        self.fields['priority'].label = '优先级'
        self.fields['category'].label = '分类' 