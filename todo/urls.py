from django.urls import path
from .views.user_views import RegisterView, LoginView, logout_view, ProfileView, PasswordChangeView
from .views.general_views import home
from .views.category_views import CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView, SetDefaultCategoryView
from .views.task_views import TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView, TaskBulkActionView
from .views.statistic_views import StatisticView
from captcha.views import captcha_refresh

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home, name='home'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('captcha/refresh/', captcha_refresh, name='captcha-refresh'),
    
    # 分类管理URL
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/<int:pk>/set_default/', SetDefaultCategoryView.as_view(), name='set_default_category'),

    # 任务管理URL
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/bulk_action/', TaskBulkActionView.as_view(), name='task_bulk_action'),
    
    # 统计页面URL
    path('statistic/', StatisticView.as_view(), name='statistic'),
]
