from django.core.management.base import BaseCommand
from todo.models import User, Category, Task
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = '创建测试数据'

    def handle(self, *args, **kwargs):
        # 创建测试用户
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='test123456'
            )
            self.stdout.write(self.style.SUCCESS('成功创建测试用户'))
        else:
            user = User.objects.get(username='testuser')
            self.stdout.write(self.style.SUCCESS('测试用户已存在'))

        # 创建分类
        categories = [
            {'name': '工作', 'color': '#FF5733'},
            {'name': '学习', 'color': '#33FF57'},
            {'name': '生活', 'color': '#3357FF'},
            {'name': '娱乐', 'color': '#F333FF'},
            {'name': '其他', 'color': '#FF33F3'},
        ]

        for cat_data in categories:
            Category.objects.get_or_create(
                user=user,
                name=cat_data['name'],
                defaults={'color': cat_data['color']}
            )
        self.stdout.write(self.style.SUCCESS('成功创建分类'))

        # 创建任务
        status_choices = ['not_started', 'in_progress', 'completed']
        priorities = [1, 2, 3, 4, 5]
        
        # 获取所有分类
        all_categories = Category.objects.filter(user=user)
        
        # 创建30个任务
        for i in range(30):
            # 随机选择状态和优先级
            status = random.choice(status_choices)
            priority = random.choice(priorities)
            
            # 随机选择分类
            category = random.choice(all_categories)
            
            # 创建截止日期（过去7天到未来7天之间）
            days = random.randint(-7, 7)
            due_date = timezone.now() + timedelta(days=days)
            
            # 如果是已完成的任务，设置完成时间
            completed_at = None
            if status == 'completed':
                completed_at = due_date - timedelta(days=random.randint(0, 3))
            
            # 创建任务
            Task.objects.create(
                user=user,
                title=f'测试任务 {i+1}',
                description=f'这是测试任务 {i+1} 的描述',
                category=category,
                status=status,
                priority=priority,
                due_date=due_date,
                completed_at=completed_at
            )
        
        self.stdout.write(self.style.SUCCESS('成功创建测试任务')) 