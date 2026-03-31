from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter
from . import views
from .views import generate, DataResourceViewSet,TestCaseListView, TestCaseDetailView

# 创建 DRF 路由器
router = DefaultRouter()
router.register(r'data-resources', DataResourceViewSet)
router.register(r'environment-resources', views.EnvironmentResourceViewSet)

urlpatterns = [
    # 原有的传统 URL 模式
    path('generate1/', views.generate1),
    path('generate2/', views.generate2),
    path('generate/', views.generate, name='generate'),
    path('save_testcases/', views.save_testcases),
    path('list_class/<str:project_name>/', views.list_class),
    path('source-code/upload-zip/', views.upload_source_code_zip, name='upload_source_code_zip'),
    path('source-code/list/', views.list_source_files, name='list_source_files'),
    path('source-code/<int:file_id>/content/', views.get_source_file_content, name='get_source_file_content'),
    path('source-code/delete/<int:project_id>/', views.delete_project, name='delete_source_files'),
    path('source-code/<int:project_id>/run/', views.run_project, name='run_project'),
    path('source-code/<int:project_id>/result/', views.get_project_result, name='get_project_result'),
    
    path('test-cases/', TestCaseListView.as_view(), name='test_case_list'),
    path('test-cases/<int:test_case_id>/', TestCaseDetailView.as_view(), name='test_case_detail'),


   path('', include(router.urls)),  # 不加 'api/' 前缀
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
