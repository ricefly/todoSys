from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

def user_avatar_path(instance, filename):
    """生成用户头像的存储路径"""
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 使用用户ID和用户名组合作为目录名
    return os.path.join('avatars', f'user_{instance.id}_{instance.username}', f'avatar.{ext}')

class User(AbstractUser):
    """用户模型"""
    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, verbose_name='头像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def create_default_category(self):
        """创建默认分类"""
        Category.objects.get_or_create(
            user=self,
            name='未分类',
            defaults={
                'color': '#808080',  # 灰色
                'is_default': True
            }
        )

@receiver(post_save, sender=User)
def create_user_default_category(sender, instance, created, **kwargs):
    """用户创建时自动创建默认分类"""
    if created:
        instance.create_default_category()

class Category(models.Model):
    """分类模型"""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', verbose_name='用户')
    color = models.CharField(max_length=20, null=True, blank=True, verbose_name='分类颜色')
    is_default = models.BooleanField(default=False, verbose_name='是否默认分类')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'name']  # 同一用户下分类名称不能重复

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 如果是默认分类，确保同一用户下只有一个默认分类
        if self.is_default:
            Category.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # 获取用户的默认分类
        default_category = Category.objects.filter(user=self.user, is_default=True).first()
        if default_category and default_category != self:
            # 将该分类下的所有任务转移到默认分类
            Task.objects.filter(category=self).update(category=default_category)
        super().delete(*args, **kwargs)

class Task(models.Model):
    """待办事项模型"""
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
    ]

    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='完成状态')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='截止日期')
    priority = models.IntegerField(default=0, verbose_name='优先级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='分类')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name='用户')

    class Meta:
        verbose_name = '待办事项'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']  # 按创建时间倒序排列

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 如果任务没有分类，自动分配到用户的默认分类
        if not self.category and self.user:
            default_category = Category.objects.filter(user=self.user, is_default=True).first()
            if default_category:
                self.category = default_category
        
        # 处理完成时间
        if self.status == 'completed' and not self.completed_at:
            # 如果状态变为已完成且没有完成时间，则记录当前时间
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            # 如果状态不是已完成，则清空完成时间
            self.completed_at = None
            
        super().save(*args, **kwargs)
