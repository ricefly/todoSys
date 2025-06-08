from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q # 用于复杂查询
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from django.core.paginator import Paginator # 导入 Paginator

from todo.models import Task, Category
from todo.forms import TaskForm

class TaskListView(LoginRequiredMixin, ListView):
    """任务列表视图"""
    model = Task
    template_name = 'task/list.html'
    context_object_name = 'tasks'
    paginate_by = 10 # 每页显示10条任务
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user).order_by('-created_at')
        
        # 筛选条件
        category_id = self.request.GET.get('category')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        due_date_before = self.request.GET.get('due_date_before')
        search_query = self.request.GET.get('q')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if due_date_before:
            try:
                # 注意：datetime-local 的值是 'YYYY-MM-DDTHH:MM' 格式
                due_date_before_dt = datetime.strptime(due_date_before, '%Y-%m-%dT%H:%M')
                queryset = queryset.filter(due_date__lte=due_date_before_dt)
            except ValueError:
                # 处理日期格式错误，可以选择忽略或返回错误信息
                pass
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        context['status_choices'] = Task.STATUS_CHOICES
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_due_date_before'] = self.request.GET.get('due_date_before', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Paginator 会自动在 ListView 中处理，并通过 page_obj 传递到模板
        # 这里只需要确保 context 中包含了 paginate_by 指定的每页对象即可
        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    """创建任务视图"""
    model = Task
    template_name = 'task/form.html'
    fields = ['title', 'description', 'status', 'due_date', 'priority', 'category']
    success_url = reverse_lazy('task_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '任务创建成功！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '请检查表单填写是否正确！')
        return super().form_invalid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """编辑任务视图"""
    model = Task
    template_name = 'task/form.html'
    fields = ['title', 'description', 'status', 'due_date', 'priority', 'category']
    success_url = reverse_lazy('task_list')
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '任务更新成功！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '请检查表单填写是否正确！')
        return super().form_invalid(form)

class TaskDeleteView(LoginRequiredMixin, View):
    """删除任务视图"""
    def post(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        task.delete()
        messages.success(request, '任务已删除！')
        return redirect('task_list')

class TaskBulkActionView(LoginRequiredMixin, View):
    """批量操作任务视图"""
    def post(self, request):
        action = request.POST.get('action')
        task_ids = request.POST.getlist('task_ids')
        
        if not task_ids:
            messages.error(request, '请选择要操作的任务！')
            return redirect('task_list')
        
        tasks = Task.objects.filter(id__in=task_ids, user=request.user)
        
        if action == 'delete':
            tasks.delete()
            messages.success(request, '选中的任务已删除！')
        elif action == 'complete':
            tasks.update(status='completed', completed_at=timezone.now())
            messages.success(request, '选中的任务已完成！')
        else:
            messages.error(request, '无效的操作！')
        
        return redirect('task_list')

@login_required
def task_list(request):
    """任务列表视图"""
    # 获取当前用户的所有任务
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # 获取筛选参数
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    priority = request.GET.get('priority')
    search = request.GET.get('search')
    
    # 应用筛选条件
    if status:
        tasks = tasks.filter(status=status)
    if category_id:
        tasks = tasks.filter(category_id=category_id)
    if priority:
        tasks = tasks.filter(priority=priority)
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # 获取当前用户的所有分类
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'tasks': tasks,
        'categories': categories,
        'current_status': status,
        'current_category': category_id,
        'current_priority': priority,
        'search_query': search,
    }
    return render(request, 'task/list.html', context)

@login_required
def task_create(request):
    """创建任务视图"""
    if request.method == 'POST':
        # 获取表单数据
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority')
        category_id = request.POST.get('category')
        
        # 验证必填字段
        if not title:
            messages.error(request, '任务标题不能为空！')
            return redirect('task_create')
        
        try:
            # 创建任务
            task = Task.objects.create(
                user=request.user,
                title=title,
                description=description,
                status=status,
                due_date=due_date if due_date else None,
                priority=priority if priority else 0,
                category_id=category_id if category_id else None
            )
            messages.success(request, '任务创建成功！')
            return redirect('task_list')
        except Exception as e:
            messages.error(request, f'创建任务失败：{str(e)}')
            return redirect('task_create')
    
    # 获取当前用户的所有分类
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'categories': categories,
    }
    return render(request, 'task/form.html', context)

@login_required
def task_edit(request, task_id):
    """编辑任务视图"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        # 获取表单数据
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority')
        category_id = request.POST.get('category')
        
        # 验证必填字段
        if not title:
            messages.error(request, '任务标题不能为空！')
            return redirect('task_edit', task_id=task_id)
        
        try:
            # 更新任务
            task.title = title
            task.description = description
            task.status = status
            task.due_date = due_date if due_date else None
            task.priority = priority if priority else 0
            task.category_id = category_id if category_id else None
            task.save()
            
            messages.success(request, '任务更新成功！')
            return redirect('task_list')
        except Exception as e:
            messages.error(request, f'更新任务失败：{str(e)}')
            return redirect('task_edit', task_id=task_id)
    
    # 获取当前用户的所有分类
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'task': task,
        'categories': categories,
    }
    return render(request, 'task/form.html', context)

@login_required
def task_delete(request, task_id):
    """删除任务视图"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, '任务已删除！')
    return redirect('task_list')

@login_required
def task_complete(request, task_id):
    """完成任务视图"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save()
    messages.success(request, '任务已完成！')
    return redirect('task_list')
