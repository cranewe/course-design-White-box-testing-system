import os
from django.db import models
from django.conf import settings


class SourceCodeProject(models.Model):
    """源代码项目模型"""
    project_name = models.CharField(max_length=255, verbose_name="项目名称")
    project_path = models.CharField(max_length=255, verbose_name="项目路径")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    description = models.TextField(blank=True, null=True, verbose_name="项目描述")
    status = models.CharField(max_length=20, default="unanalyzed", verbose_name="分析状态")
    execution_result = models.JSONField(null=True, blank=True, verbose_name="运行结果")

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "源代码项目"
        verbose_name_plural = "源代码项目"


class SourceCodeFile(models.Model):
    """源代码文件模型"""
    project = models.ForeignKey(SourceCodeProject, on_delete=models.CASCADE, related_name='files', verbose_name="所属项目")
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file_path = models.CharField(max_length=255, verbose_name="文件路径")
    language = models.CharField(max_length=50, verbose_name="编程语言")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    description = models.TextField(blank=True, null=True, verbose_name="文件描述")
    status = models.CharField(max_length=20, default="unanalyzed", verbose_name="分析状态")

    def __str__(self):
        return f"{self.project.project_name}/{self.file_name}"

    class Meta:
        verbose_name = "源代码文件"
        verbose_name_plural = "源代码文件"

######################################################################################################################3

from django.db import models

#保存测试用例
class GeneratedTestCaseFile(models.Model):
    # 所属项目，例如 Defects4J-Math
    project_name = models.CharField(max_length=100)

    # 生成的方法，例如 EvoSuite / LLM / Symbolic
    generation_method = models.CharField(max_length=50)

    # 生成的类名和方法
    class_name = models.CharField(max_length=255)

    # 文件名，例如 GeneratedTestCases.java
    file_name = models.CharField(max_length=200)

    # 文件的相对或绝对路径
    file_path = models.TextField()

    # 覆盖率、有效性、多样性（可选字段）
    coverage = models.FloatField(null=True, blank=True)
    effectiveness = models.FloatField(null=True, blank=True)
    diversity = models.FloatField(null=True, blank=True)

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.project_name} - {self.file_name}'

from django.utils.translation import gettext_lazy as _

class DataResource(models.Model):
    """数据资源模型"""
    
    TYPE_CHOICES = (
        ('Excel', 'Excel'),
        ('SQLServer', 'SQL Server'),
        ('XML', 'XML'),
        ('JSON', 'JSON'),
        ('CSV', 'CSV'),
    )
    
    AUTH_TYPE_CHOICES = (
        ('sqlserver', 'SQL Server Authentication'),
        ('windows', 'Windows Authentication'),
    )
    
    name = models.CharField(_('数据源名称'), max_length=100)
    type = models.CharField(_('数据源类型'), max_length=20, choices=TYPE_CHOICES)
    path = models.CharField(_('文件路径/连接信息'), max_length=255, blank=True, null=True)
    
    # Excel 特有字段
    sheet = models.CharField(_('工作表'), max_length=100, blank=True, null=True)
    
    # SQL Server 特有字段
    server = models.CharField(_('服务器地址'), max_length=100, blank=True, null=True)
    port = models.CharField(_('端口'), max_length=10, blank=True, null=True, default='1433')
    database = models.CharField(_('数据库名称'), max_length=100, blank=True, null=True)
    auth_type = models.CharField(_('身份验证类型'), max_length=20, choices=AUTH_TYPE_CHOICES, 
                                blank=True, null=True, default='sqlserver')
    username = models.CharField(_('用户名'), max_length=100, blank=True, null=True)
    password = models.CharField(_('密码'), max_length=100, blank=True, null=True)
    timeout = models.IntegerField(_('连接超时(秒)'), blank=True, null=True, default=30)
    encrypt = models.BooleanField(_('加密连接'), default=False)
    trust_server_certificate = models.BooleanField(_('信任服务器证书'), default=True)
    table = models.CharField(_('表名'), max_length=100, blank=True, null=True)
    
    # XML 特有字段
    root_path = models.CharField(_('根节点路径'), max_length=255, blank=True, null=True)
    
    # JSON 特有字段
    data_path = models.CharField(_('数据路径'), max_length=255, blank=True, null=True)
    
    # CSV 特有字段
    delimiter = models.CharField(_('分隔符'), max_length=10, blank=True, null=True, default=',')
    has_header = models.BooleanField(_('包含表头'), default=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('数据资源')
        verbose_name_plural = _('数据资源')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def get_connection_string(self):
        """获取SQL Server连接字符串"""
        if self.type != 'SQLServer':
            return None
            
        if self.auth_type == 'windows':
            # Windows 身份验证
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server}"
            if self.port and self.port != '1433':
                conn_str += f",{self.port}"
            conn_str += f";DATABASE={self.database};Trusted_Connection=yes"
        else:
            # SQL Server 身份验证
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server}"
            if self.port and self.port != '1433':
                conn_str += f",{self.port}"
            conn_str += f";DATABASE={self.database};UID={self.username};PWD={self.password}"
        
        # 添加额外的连接参数
        if self.timeout:
            conn_str += f";LoginTimeout={self.timeout}"
        
        if self.encrypt:
            conn_str += ";Encrypt=yes"
        else:
            conn_str += ";Encrypt=no"
            
        if self.trust_server_certificate:
            conn_str += ";TrustServerCertificate=yes"
        else:
            conn_str += ";TrustServerCertificate=no"
            
        return conn_str
    
    def get_display_info(self):
        """获取显示信息"""
        if self.type == 'SQLServer':
            server_info = self.server
            if self.port and self.port != '1433':
                server_info += f":{self.port}"
            return f"{server_info}/{self.database}"
        elif self.type == 'Excel':
            return f"{self.path} - {self.sheet}" if self.sheet else self.path
        else:
            return self.path or ''
    
    def is_database_type(self):
        """判断是否为数据库类型"""
        return self.type == 'SQLServer'
    
    def is_file_type(self):
        """判断是否为文件类型"""
        return self.type in ['Excel', 'XML', 'JSON', 'CSV']
    
    def validate_connection_params(self):
        """验证连接参数"""
        errors = []
        
        if self.type == 'SQLServer':
            if not self.server:
                errors.append('服务器地址不能为空')
            if not self.database:
                errors.append('数据库名称不能为空')
            if self.auth_type == 'sqlserver' and not self.username:
                errors.append('SQL Server身份验证时用户名不能为空')
                
        elif self.type in ['Excel', 'XML', 'JSON', 'CSV']:
            if not self.path:
                errors.append('文件路径不能为空')
                
        return errors

###########################################################新增

class EnvironmentResource(models.Model):
    """环境资源配置模型"""
    
    TYPE_CHOICES = (
        ('Python', 'Python (requirements.txt)'),
        ('Java', 'Java (pom.xml)'),
    )
    
    name = models.CharField(_('环境资源名称'), max_length=100)
    type = models.CharField(_('环境资源类型'), max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(_('描述'), blank=True, null=True)
    
    # 文件相关字段
    file_name = models.CharField(_('文件名'), max_length=100)  # requirements.txt 或 pom.xml
    file_path = models.CharField(_('文件路径'), max_length=255,blank=True, null=True)
    file_content = models.TextField(_('文件内容'), blank=True, null=True)
    
    # Python 特有字段
    python_version = models.CharField(_('Python版本'), max_length=20, blank=True, null=True)
    virtual_env_name = models.CharField(_('虚拟环境名称'), max_length=100, blank=True, null=True)
    
    # Java 特有字段
    java_version = models.CharField(_('Java版本'), max_length=20, blank=True, null=True)
    maven_version = models.CharField(_('Maven版本'), max_length=20, blank=True, null=True)
    group_id = models.CharField(_('Group ID'), max_length=100, blank=True, null=True)
    artifact_id = models.CharField(_('Artifact ID'), max_length=100, blank=True, null=True)
    version = models.CharField(_('项目版本'), max_length=50, blank=True, null=True, default='1.0.0')
    
    # 通用字段
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('环境资源配置')
        verbose_name_plural = _('环境资源配置')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def get_file_extension(self):
        """获取文件扩展名"""
        if self.type == 'Python':
            return '.txt'
        elif self.type == 'Java':
            return '.xml'
        return ''
    
    def get_default_file_name(self):
        """获取默认文件名"""
        if self.type == 'Python':
            return 'requirements.txt'
        elif self.type == 'Java':
            return 'pom.xml'
        return ''
    
    def validate_file_content(self):
        """验证文件内容格式"""
        errors = []
        
        if self.type == 'Python':
            # 验证 requirements.txt 格式
            if self.file_content:
                lines = self.file_content.strip().split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 简单验证包名格式
                        if '==' not in line and '>=' not in line and '<=' not in line and '>' not in line and '<' not in line:
                            if not line.replace('-', '').replace('_', '').replace('.', '').isalnum():
                                errors.append(f'第{line_num}行格式不正确: {line}')
        
        # elif self.type == 'Java':
        #     # 验证 pom.xml 基本结构
        #     if self.file_content:
        #         required_tags = ['<project>', '<modelVersion>', '<groupId>', '<artifactId>', '<version>']
        #         for tag in required_tags:
        #             if tag not in self.file_content:
        #                 errors.append(f'缺少必要的XML标签: {tag}')
        
        return errors
    
    def generate_default_content(self):
        """生成默认文件内容"""
        if self.type == 'Python':
            return """# Python项目依赖文件
# 示例依赖包
requests==2.28.1
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.1
"""
        elif self.type == 'Java':
            group_id = self.group_id or 'com.example'
            artifact_id = self.artifact_id or 'demo'
            version = self.version or '1.0.0'
            java_version = self.java_version or '11'
            
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>{group_id}</groupId>
    <artifactId>{artifact_id}</artifactId>
    <version>{version}</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>{java_version}</maven.compiler.source>
        <maven.compiler.target>{java_version}</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <!-- 示例依赖 -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>{java_version}</source>
                    <target>{java_version}</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>"""
        return ""