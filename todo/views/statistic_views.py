from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from ..models import Task, Category

class StatisticView(LoginRequiredMixin, View):
    """统计视图"""
    template_name = 'statistic/index.html'
    
    def get(self, request):
        # 获取当前用户的任务
        user_tasks = Task.objects.filter(user=request.user)
        
        # 任务状态统计
        status_stats = user_tasks.values('status').annotate(count=Count('id'))
        # 将状态统计转换为列表并添加中文显示
        status_stats = [
            {
                'status': stat['status'],
                'get_status_display': dict(Task.STATUS_CHOICES)[stat['status']],
                'count': stat['count']
            }
            for stat in status_stats
        ]
        
        # 分类任务数量统计
        category_stats = Category.objects.filter(user=request.user).annotate(
            task_count=Count('tasks')
        ).values('name', 'color', 'task_count')
        
        # 最近7天完成情况
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_completion = user_tasks.filter(
            status='completed',
            completed_at__gte=seven_days_ago
        ).extra(
            select={'date': "DATE(completed_at)"}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # 任务优先级分布
        priority_stats = user_tasks.values('priority').annotate(count=Count('id'))
        
        # 即将到期任务（3天内）
        three_days_later = timezone.now() + timedelta(days=3)
        upcoming_tasks = user_tasks.filter(
            due_date__lte=three_days_later,
            status__in=['not_started', 'in_progress']
        ).order_by('due_date')
        
        # 计算总体完成率
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(status='completed').count()
        completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        
        context = {
            'status_stats': status_stats,
            'category_stats': category_stats,
            'daily_completion': daily_completion,
            'priority_stats': priority_stats,
            'upcoming_tasks': upcoming_tasks,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate,
        }
        
        return render(request, self.template_name, context)
