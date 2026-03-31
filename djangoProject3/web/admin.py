from django.contrib import admin
from .models import DataResource

@admin.register(DataResource)
class DataResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'path', 'created_at', 'updated_at')
    list_filter = ('type',)
    search_fields = ('name', 'path')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'type', 'path')
        }),
        ('Excel 配置', {
            'fields': ('sheet',),
            'classes': ('collapse',),
        }),
        ('SQL Server 配置', {
            'fields': ('server', 'port', 'database', 'authType', 'username', 'password', 'timeout', 'encrypt', 'trustServerCertificate', 'table'),
            'classes': ('collapse',),
        }),
        ('XML 配置', {
            'fields': ('root_path',),
            'classes': ('collapse',),
        }),
        ('JSON 配置', {
            'fields': ('data_path',),
            'classes': ('collapse',),
        }),
        ('CSV 配置', {
            'fields': ('delimiter', 'has_header'),
            'classes': ('collapse',),
        }),
    )