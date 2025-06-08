from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..models import Category

class CategoryListView(LoginRequiredMixin, ListView):
    """分类列表视图"""
    model = Category
    template_name = 'category/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    """创建分类视图"""
    model = Category
    template_name = 'category/form.html'
    fields = ['name', 'color']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '分类创建成功！')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """更新分类视图"""
    model = Category
    template_name = 'category/form.html'
    fields = ['name', 'color']
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, '分类更新成功！')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """删除分类视图"""
    model = Category
    template_name = 'category/confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, '分类删除成功！')
        return super().delete(request, *args, **kwargs)

class SetDefaultCategoryView(LoginRequiredMixin, View):
    """设置默认分类视图"""
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk, user=request.user)
        # 将其他分类设置为非默认
        Category.objects.filter(user=request.user).update(is_default=False)
        # 设置当前分类为默认
        category.is_default = True
        category.save()
        messages.success(request, f'已将 {category.name} 设置为默认分类！')
        return redirect('category_list')
