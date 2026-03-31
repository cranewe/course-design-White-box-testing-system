from rest_framework import serializers
from .models import DataResource
#####################新增
from .models import EnvironmentResource

class DataResourceSerializer(serializers.ModelSerializer):
    """数据资源序列化器"""
    
    class Meta:
        model = DataResource
        fields = '__all__'



# #####################################新增
class EnvironmentResourceSerializer(serializers.ModelSerializer):
    """环境资源配置序列化器"""
    
    class Meta:
        model = EnvironmentResource
        fields = [
            'id', 'name', 'type', 'description', 'file_name', 'file_path',
            'file_content', 'python_version', 'virtual_env_name', 
            'java_version', 'maven_version', 'group_id', 'artifact_id',
            'version', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_file_content(self, value):
        """验证文件内容"""
        if not value:
            return value
            
        # 获取环境类型 - 修复关键问题
        env_type = None
        if self.instance:
            env_type = self.instance.type
        elif hasattr(self, 'initial_data') and 'type' in self.initial_data:
            env_type = self.initial_data['type']
        else:
            # 如果无法获取类型，跳过验证
            return value
        
        if env_type == 'Python':
            # 验证 requirements.txt 格式
            try:
                lines = value.strip().split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 简单验证包名格式 - 放宽验证条件
                        if not any(op in line for op in ['==', '>=', '<=', '>', '<', '~=', '!=']):
                            # 如果没有版本号，只验证包名是否合理
                            if not line.replace('-', '').replace('_', '').replace('.', '').replace('[', '').replace(']', '').isalnum():
                                raise serializers.ValidationError(f'第{line_num}行格式不正确: {line}')
            except Exception as e:
                raise serializers.ValidationError(f'requirements.txt格式验证失败: {str(e)}')

        
        return value
    
    def validate(self, data):
        """整体验证"""
        # 根据类型设置默认文件名
        if 'type' in data and not data.get('file_name'):
            if data['type'] == 'Python':
                data['file_name'] = 'requirements.txt'
            elif data['type'] == 'Java':
                data['file_name'] = 'pom.xml'
        
        # 自动生成file_path如果为空
        if 'file_path' in data and (not data['file_path'] or data['file_path'].strip() == ''):
            name = data.get('name', 'unnamed')
            file_name = data.get('file_name', 'config')
            # 生成基于名称和文件名的路径
            data['file_path'] = f'/environment/{name}/{file_name}'
        
        # 如果没有提供file_content，生成默认内容
        if 'type' in data and not data.get('file_content'):
            if data['type'] == 'Python':
                data['file_content'] = """# Python项目依赖文件
# 示例依赖包
requests==2.28.1
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.1
"""
            elif data['type'] == 'Java':
                group_id = data.get('group_id', 'com.example')
                artifact_id = data.get('artifact_id', 'demo')
                version = data.get('version', '1.0.0')
                java_version = data.get('java_version', '11')
                
                data['file_content'] = f'''<?xml version="1.0" encoding="UTF-8"?>
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
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>'''
        
        return data