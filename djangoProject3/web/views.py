import json
import pathlib
import re
from .models import GeneratedTestCaseFile, DataResource
import os, re, json, datetime, pathlib
from django.http import HttpResponse

import os
import zipfile
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import SourceCodeProject, SourceCodeFile
import threading
import time
import subprocess
import sys
import tempfile
import shutil
import json
from django.http import HttpResponse

import os
import zipfile
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import SourceCodeProject, SourceCodeFile
import threading
import time

import json, os, re, tempfile, shutil, subprocess


def get_source_code_dir():
    """获取源代码存储目录"""
    return os.path.join('D:\\ruanjian', 'source_code')


def get_conda_env_name(project_id):
    """生成conda环境名称"""
    return f"project_{project_id}"


def create_conda_env(env_name, requirements_file):
    """创建conda环境并安装依赖"""
    try:
        # 检查conda是否可用
        subprocess.run(['conda', '--version'], check=True, capture_output=True)

        # 创建新环境
        subprocess.run(['conda', 'create', '-n', env_name, 'python=3.11', '-y'], check=True)

        # 激活环境并安装依赖
        if os.path.exists(requirements_file):
            # 使用conda环境中的pip安装依赖
            pip_cmd = f'conda run -n {env_name} pip install -r {requirements_file}'
            subprocess.run(pip_cmd, shell=True, check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"创建conda环境失败: {str(e)}")
        return False
    except Exception as e:
        print(f"创建conda环境时发生错误: {str(e)}")
        return False


def cleanup_conda_env(env_name):
    """清理conda环境"""
    try:
        subprocess.run(['conda', 'env', 'remove', '-n', env_name, '-y'], check=True)
    except Exception as e:
        print(f"清理conda环境失败: {str(e)}")


@csrf_exempt
def upload_source_code_zip(request):
    """上传源代码ZIP文件"""
    if request.method == 'POST':
        try:
            zip_file = request.FILES.get('file')
            if not zip_file:
                return JsonResponse({'error': '未找到ZIP文件'}, status=400)

            source_code_dir = get_source_code_dir()
            os.makedirs(source_code_dir, exist_ok=True)

            # 保存ZIP文件
            zip_path = os.path.join(source_code_dir, zip_file.name)
            with open(zip_path, 'wb+') as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)

            # 获取zip内的首个顶级目录（或文件）
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                namelist = zip_ref.namelist()
                zip_ref.extractall(source_code_dir)

                # 提取第一个非空路径前缀（如顶层目录）
                top_level_items = set([name.split('/')[0] for name in namelist if name.strip()])
                first_item = list(top_level_items)[0] if top_level_items else None

            os.remove(zip_path)

            if not first_item:
                return JsonResponse({'error': 'ZIP文件内容为空'}, status=400)

            # 创建项目记录
            project_path = os.path.join(source_code_dir, first_item)
            project = SourceCodeProject.objects.create(
                project_name=first_item,
                project_path=project_path,
                status='unanalyzed'
            )

            # 遍历项目目录，创建文件记录
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)

                    # 根据文件扩展名判断语言
                    ext = os.path.splitext(file)[1].lower()
                    language_map = {
                        '.py': 'Python',
                        '.java': 'Java',
                        '.cpp': 'C++',
                        '.js': 'JavaScript',
                        '.html': 'HTML',
                        '.css': 'CSS',
                        '.json': 'JSON',
                        '.xml': 'XML',
                        '.txt': 'Text'
                    }
                    language = language_map.get(ext, 'Unknown')

                    # 创建文件记录
                    SourceCodeFile.objects.create(
                        project=project,
                        file_name=file,
                        file_path=file_path,
                        language=language,
                        status='unanalyzed'
                    )

            return JsonResponse({
                'message': f'源代码项目上传成功',
                'project_id': project.id,
                'project_name': project.project_name
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '仅支持POST请求'}, status=405)


def list_source_files(request):
    """列出所有源代码文件及其对应的测试用例"""
    try:
        # 获取所有项目
        projects = SourceCodeProject.objects.all()
        project_list = []

        for project in projects:
            # 获取项目下的所有文件
            files = project.files.all()
            file_list = []

            for file in files:
                file_list.append({
                    'id': file.id,
                    'name': file.file_name,
                    'path': file.file_path,
                    'language': file.language,
                    'status': file.status,
                    'upload_time': file.upload_time.strftime('%Y-%m-%d %H:%M:%S')
                })

            # 获取与项目相关的测试用例
            test_cases = GeneratedTestCaseFile.objects.filter(project_name=project.project_name)
            test_case_list = []
            for case in test_cases:
                test_case_list.append({
                    'id': case.id,
                    'file_name': case.file_name,
                    'file_path': case.file_path,
                    'generation_method': case.generation_method,
                    'coverage': case.coverage,
                    'effectiveness': case.effectiveness,
                    'diversity': case.diversity,
                })

            project_list.append({
                'id': project.id,
                'name': project.project_name,
                'path': project.project_path,
                'status': project.status,
                'upload_time': project.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                'files': file_list,
                'testCases': test_case_list  # 添加测试用例列表
            })

        return JsonResponse({
            'projects': project_list
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_source_file_content(request, file_id):
    """获取源代码文件内容"""
    try:
        file = SourceCodeFile.objects.get(id=file_id)

        if not os.path.exists(file.file_path):
            return JsonResponse({'error': '文件不存在'}, status=404)

        with open(file.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return JsonResponse({
            'id': file.id,
            'name': file.file_name,
            'path': file.file_path,
            'language': file.language,
            'content': content
        })

    except SourceCodeFile.DoesNotExist:
        return JsonResponse({'error': '文件不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def delete_project(request, project_id):
    """删除源代码项目及其相关的测试用例文件"""
    try:
        project = SourceCodeProject.objects.get(id=project_id)

        # 删除与项目相关的测试用例文件
        generated_test_cases = GeneratedTestCaseFile.objects.filter(project_name=project.project_name)
        for test_case in generated_test_cases:
            if os.path.exists(test_case.file_path):
                os.remove(test_case.file_path)  # 删除文件
            test_case.delete()  # 删除数据库记录

        # 删除项目目录
        if os.path.exists(project.project_path):
            import shutil
            shutil.rmtree(project.project_path)

        # 删除数据库记录（级联删除会自动删除相关的文件记录）
        project.delete()

        return JsonResponse({'message': '项目及其相关测试用例已删除'})

    except SourceCodeProject.DoesNotExist:
        return JsonResponse({'error': '项目不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def run_project(request, project_id):
    """运行指定的源代码项目和测试用例"""
    try:
        # 获取请求体中的数据
        data = json.loads(request.body)
        test_case_id = data.get('testCaseId')  # 获取测试用例ID

        project = SourceCodeProject.objects.get(id=project_id)

        # 更新项目状态为运行中
        project.status = 'running'
        project.save()

        # 在后台线程中执行运行
        def run_execution():
            try:
                # 获取项目路径
                project_path = project.project_path
                env_name = get_conda_env_name(project_id)

                # 查找指定的测试用例
                test_case = GeneratedTestCaseFile.objects.get(id=test_case_id)

                # 检查是否为Java项目
                is_java_project = any(file.language == 'Java' for file in project.files.all())
                has_pom = any(file.file_name == 'pom.xml' for file in project.files.all())

                if is_java_project and has_pom:
                    try:
                        # 使用Maven编译和运行指定的测试用例
                        working_dir = project_path

                        # 1. 清理并编译项目
                        compile_cmd = 'mvn clean compile'
                        compile_process = subprocess.Popen(
                            compile_cmd,
                            shell=True,
                            cwd=working_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        compile_stdout, compile_stderr = compile_process.communicate(timeout=60)

                        if compile_process.returncode != 0:
                            project.status = 'failed'
                            project.execution_result = {
                                'error': 'Maven编译失败',
                                'compile_stdout': compile_stdout,
                                'compile_stderr': compile_stderr
                            }
                            project.save()
                            return

                        # 2. 运行指定的测试用例
                        run_cmd = f'mvn -Dtest={test_case.file_name} test'
                        run_process = subprocess.Popen(
                            run_cmd,
                            shell=True,
                            cwd=working_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )

                        # 设置超时时间（秒）
                        timeout = 60  # 测试可能需要更长时间
                        try:
                            stdout, stderr = run_process.communicate(timeout=timeout)

                            # 更新项目状态和运行结果
                            project.status = 'completed'
                            project.execution_result = {
                                'compile_stdout': compile_stdout,
                                'compile_stderr': compile_stderr,
                                'test_stdout': stdout,
                                'test_stderr': stderr,
                                'return_code': run_process.returncode,
                                'test_case': test_case.file_name
                            }
                            project.save()

                        except subprocess.TimeoutExpired:
                            run_process.kill()
                            project.status = 'timeout'
                            project.execution_result = {
                                'error': f'测试执行超时（{timeout}秒）',
                                'compile_stdout': compile_stdout,
                                'compile_stderr': compile_stderr,
                                'test_case': test_case.file_name
                            }
                            project.save()

                    except Exception as e:
                        project.status = 'failed'
                        project.execution_result = {
                            'error': f'Maven执行错误: {str(e)}'
                        }
                        project.save()

                # 处理Python项目
                else:
                    try:
                        # 运行指定的测试用例
                        test_case_file = test_case.file_path  # 获取测试用例文件路径
                        working_dir = os.path.dirname(test_case_file)  # 获取测试文件所在目录
                        requirements_file = os.path.join(project_path, 'requirements.txt')  # 获取requirements.txt路径

                        # 创建conda环境并安装依赖
                        if not create_conda_env(env_name, requirements_file):
                            project.status = 'failed'
                            project.execution_result = {
                                'error': '创建conda环境失败'
                            }
                            project.save()
                            return

                        try:
                            # 在conda环境中运行pytest测试
                            cmd = f'conda run -n {env_name} pytest {test_case_file} -v'
                            
                            process = subprocess.Popen(
                                cmd,
                                shell=True,
                                cwd=working_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )

                            try:
                                stdout, stderr = process.communicate(timeout=30)

                                # 解析pytest输出
                                test_results = []
                                for line in stdout.split('\n'):
                                    if 'PASSED' in line or 'FAILED' in line:
                                        test_results.append(line.strip())

                                # 更新项目状态和运行结果
                                project.status = 'completed'
                                project.execution_result = {
                                    'stdout': stdout,
                                    'stderr': stderr,
                                    'return_code': process.returncode,
                                    'test_results': test_results,
                                    'test_case': test_case.file_name
                                }
                                project.save()

                            except subprocess.TimeoutExpired:
                                process.kill()
                                project.status = 'timeout'
                                project.execution_result = {
                                    'error': '测试执行超时（30秒）'
                                }
                                project.save()

                        finally:
                            # 清理conda环境
                            cleanup_conda_env(env_name)

                    except Exception as e:
                        project.status = 'failed'
                        project.execution_result = {
                            'error': str(e)
                        }
                        project.save()

            except Exception as e:
                project.status = 'failed'
                project.execution_result = {
                    'error': str(e)
                }
                project.save()

        # 启动后台执行线程
        execution_thread = threading.Thread(target=run_execution)
        execution_thread.start()

        return JsonResponse({
            'message': '项目运行已启动',
            'project_id': project.id,
            'test_case_id': test_case_id  # 返回测试用例ID
        })

    except SourceCodeProject.DoesNotExist:
        return JsonResponse({'error': '项目不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_project_result(request, project_id):
    """获取项目运行结果"""
    try:
        project = SourceCodeProject.objects.get(id=project_id)

        if not project.execution_result:
            return JsonResponse({'error': '项目尚未运行或运行结果不可用'}, status=404)

        # 格式化执行结果
        result = {
            'status': project.status,
            'output': {
                'stdout': None,
                'stderr': None
            }
        }

        # 处理Java项目的测试结果
        if 'test_stdout' in project.execution_result:
            result['output']['stdout'] = project.execution_result['test_stdout']
            result['output']['stderr'] = project.execution_result['test_stderr']
            result['compilation'] = {
                'stdout': project.execution_result.get('compile_stdout'),
                'stderr': project.execution_result.get('compile_stderr')
            }
            result['test_files'] = project.execution_result.get('test_files', [])
            result['return_code'] = project.execution_result.get('return_code')

        # 处理Python项目的执行结果
        elif 'stdout' in project.execution_result:
            result['output']['stdout'] = project.execution_result['stdout']
            result['output']['stderr'] = project.execution_result['stderr']
            result['return_code'] = project.execution_result.get('return_code')

        # 处理错误情况
        elif 'error' in project.execution_result:
            result['error'] = project.execution_result['error']
            # 如果有编译输出，也包含进来
            if 'compile_stdout' in project.execution_result:
                result['compilation'] = {
                    'stdout': project.execution_result.get('compile_stdout'),
                    'stderr': project.execution_result.get('compile_stderr')
                }

        return JsonResponse(result)

    except SourceCodeProject.DoesNotExist:
        return JsonResponse({'error': '项目不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


########################################################################################################################


def list_class(request, project_name):
    """列出所有项目文件"""
    try:
        # 在SourceCodeProject获取project_name为project_name的项目
        project = SourceCodeProject.objects.get(project_name=project_name)
        # 获取Java和Python文件
        classes = SourceCodeFile.objects.filter(
            project_id=project.id,
            language__in=['Java', 'Python']  # 同时支持Java和Python文件
        ).exclude(
            file_name__icontains='Test'
        )
        class_list = []

        for cla in classes:
            class_list.append({
                'name': cla.file_name,
                'language': cla.language  # 添加语言信息
            })

        return JsonResponse({
            'classes': class_list
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


SUFFIX_RE = r'^{basename}(\d+)$'  # 动态正则模板


def _next_suffix(base_name: str) -> int:
    """
    返回已有同名测试文件的最大数字后缀 + 1。
    若不存在数字后缀，则从 0 开始。
    """
    candidates = GeneratedTestCaseFile.objects.values_list('file_name', flat=True)
    # 使用startswith过滤
    candidates = [c for c in candidates if c.startswith(base_name)]

    max_suffix = -1
    for name in candidates:
        # DayTest0.java -> DayTest0
        stem = os.path.splitext(name)[0]
        m = re.match(SUFFIX_RE.format(basename=re.escape(base_name)), stem)
        if m:
            max_suffix = max(max_suffix, int(m.group(1)))
    return max_suffix + 1


def extract_java_fqn(class_path):
    """
    从文件路径提取 Java 类的全限定名（FQN）
    """

    # 标准化路径
    normalized_path = os.path.normpath(class_path)

    # 找到 "main/java/" 之后的路径部分
    java_index = normalized_path.find("main" + os.sep + "java" + os.sep)
    if java_index == -1:
        raise ValueError("Invalid Java source path: 'main/java/' not found")

    # 提取 "main/java/" 后面的部分
    relative_path = normalized_path[java_index + len("main" + os.sep + "java" + os.sep):]

    # 移除文件扩展名 .java
    relative_path = relative_path.replace(".java", "")

    # 将路径分隔符替换为 .
    fqn = relative_path.replace(os.sep, ".")

    return fqn


def generate1(request):
    try:
        data = json.loads(request.body)
        project_name = data.get('project')
        class_name = data.get('className')

        # 获取class的路径
        # 1. 映射项目路径
        project = SourceCodeProject.objects.get(project_name=project_name)
        project_path = project.project_path

        # 2. 编译项目
        class_dir = os.path.normpath(os.path.join(project_path, "target", "classes"))
        class_dir = class_dir.replace("\\", "/")

        tclass = SourceCodeFile.objects.get(
            project_id=project.id,
            file_name=class_name
        )

        class_name = extract_java_fqn(tclass.file_path)

        # 3. 生成测试用例的路径
        test_output_dir = os.path.join(project_path, class_name + ".evosuite-tests")
        test_output_dir = test_output_dir.replace("\\", "/")
        os.makedirs(test_output_dir, exist_ok=True)

        # 创建临时目录用于存储报告
        temp_report_dir = tempfile.mkdtemp()

        evosuite_cmd = [
            "java", "-jar", "evosuite/evosuite-1.2.0.jar",
            "-projectCP", class_dir,
            "-class", class_name,
            "-Dsearch_budget=20",
            "-Dstopping_condition=MaxTime",
            "-Dtest_dir=" + test_output_dir,
            "-Dreport_dir=" + temp_report_dir,  # 使用临时目录
            "-Dtest_scaffolding=false"
        ]
        print(evosuite_cmd)

        # 使用 Popen 启动命令，并实时读取输出

        process = subprocess.Popen(
            evosuite_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # 实时读取输出
        output = []
        for line in process.stdout:
            print(line, end="")  # 实时打印到控制台
            output.append(line)

        process.wait()  # 等待命令完成

        # 4. 读取生成的测试用例
        test_file_path = os.path.join(
            test_output_dir,
            class_name.replace(".", os.sep) + "_ESTest.java"
        )

        if not os.path.exists(test_file_path):
            return JsonResponse({"error": "未生成测试用例，EvoSuite输出：" + "".join(output)}, status=500)

        with open(test_file_path, "r", encoding="utf-8") as f:
            test_content = f.read()

        # 获取原始类名（不含包名）
        simple_class_name = class_name.split('.')[-1]
        # 获取下一个后缀
        next_suffix = _next_suffix(f"{simple_class_name}_ESTest")
        # 构建新的测试类名
        new_test_class_name = f"{simple_class_name}_ESTest{next_suffix}"

        # 替换原有的类名
        old_test_class_name = f"{simple_class_name}_ESTest"
        # 替换所有出现的类名（包括注解、注释、引用等处）
        test_content = test_content.replace(old_test_class_name, new_test_class_name)

        # 更新文件名
        new_test_file_path = os.path.join(
            test_output_dir,
            f"{new_test_class_name}.java"
        )

        # 保存新文件
        with open(new_test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        # 删除原文件
        os.remove(test_file_path)

        # 读取报告内容并解析为表格格式
        report_content = []
        for root, dirs, files in os.walk(temp_report_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # 第一行是表头
                    headers = lines[0].strip().split('\t')
                    for line in lines[1:]:
                        values = line.strip().split('\t')
                        row = dict(zip(headers, values))
                        report_content.append(row)

        # 清理临时目录
        print(report_content)
        shutil.rmtree(temp_report_dir)

        return JsonResponse({
            "message": "测试用例生成成功",
            "test_case": test_content,
            "report": report_content,  # 返回解析后的报告内容
            "test_path": new_test_file_path
        })

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


def generate2(request):
    try:
        data = json.loads(request.body)
        project_name = data.get('project')
        class_name = data.get('className')
        generation_method = data.get('generationMethod')

        # 1. 映射项目路径
        project = SourceCodeProject.objects.get(project_name=project_name)
        project_path = project.project_path

        # 2. 编译项目
        class_dir = os.path.normpath(os.path.join(project_path, "target", "classes"))
        class_dir = class_dir.replace("\\", "/")

        tclass = SourceCodeFile.objects.get(
            project_id=project.id,
            file_name=class_name
        )
        class_name = extract_java_fqn(tclass.file_path)

        # 3. 生成测试用例的路径
        test_output_dir = os.path.join(project_path, class_name + ".randoop-tests")
        test_output_dir = test_output_dir.replace("\\", "/")
        os.makedirs(test_output_dir, exist_ok=True)

        # 创建临时目录用于存储报告
        temp_report_dir = tempfile.mkdtemp()

        # 获取原始类名（不含包名）
        simple_class_name = class_name.split('.')[-1]
        test_class_name = f"{simple_class_name}Test"

        # 构建Randoop命令
        randoop_jar = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "randoop",
                                   "randoop-all-4.3.2.jar")
        randoop_cmd = [
            "java",
            "-classpath", f"{randoop_jar};{class_dir}",  # 两段 classpath 用系统分隔符拼
            "randoop.main.Main", "gentests",

            f"--testclass={class_name}",
            "--time-limit=30",  # 30 秒搜索
            "--output-limit=20",  # 总共不超 20 条测试
            "--testsperfile=100000",  # 文件上限远大于 20 ⇒ 只写 1 个文件
            "--junit-output-dir=" + test_output_dir,
            f"--regression-test-basename={test_class_name}",  # 使用原始类名+Test作为测试类名
            "--randomseed=12345",  # 固定随机种子，结果可复现

            "--only-test-public-members=true",
            "--omit-methods=java.lang.Object\\..*",  # 正则要带包名
            "--junit-reflection-allowed=false"
        ]
        print(randoop_cmd)

        # 使用 Popen 启动命令，并实时读取输出
        process = subprocess.Popen(
            randoop_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # 实时读取输出
        output = []
        for line in process.stdout:
            print(line, end="")  # 实时打印到控制台
            output.append(line)

        process.wait()  # 等待命令完成

        # 4. 读取生成的测试用例
        test_file_path = os.path.join(
            test_output_dir,
            f"{test_class_name}0.java"  # 使用新的测试类名
        )

        if not os.path.exists(test_file_path):
            return JsonResponse({"error": "未生成测试用例，Randoop输出：" + "".join(output)}, status=500)

        with open(test_file_path, "r", encoding="utf-8") as f:
            test_content = f.read()

        # 从前端传回的类名中提取简单类名（去掉.java后缀和包名）
        simple_class_name = class_name.replace(".java", "").split(".")[-1]
        # 获取下一个后缀
        next_suffix = _next_suffix(test_class_name)  # 使用test_class_name而不是simple_class_name + "Test"
        # 构建新的测试类名
        new_test_class_name = f"{simple_class_name}Test{next_suffix}"

        # 替换原有的类名
        old_test_class_name = f"{test_class_name}0"
        # 替换所有出现的类名（包括注解、注释、引用等处）
        test_content = test_content.replace(old_test_class_name, new_test_class_name)

        # 从class_name中提取包名
        package_name = ".".join(class_name.replace(".java", "").split(".")[:-1])
        # 在测试代码开头添加package声明
        test_content = f"package {package_name};\n\n" + test_content

        # 更新文件名
        new_test_file_path = os.path.join(
            test_output_dir,
            f"{new_test_class_name}.java"
        )

        # 保存新文件
        with open(new_test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        # 删除原文件
        os.remove(test_file_path)

        # 解析测试用例
        test_cases = []
        # 简单地按方法分割测试用例
        import re
        methods = re.findall(r'@Test\s+public void test\d+\(\)[^}]*}', test_content)

        for i, method in enumerate(methods):  # 返回所有测试用例
            test_cases.append({
                "title": f"Randoop生成 - 测试用例 {i + 1}",
                "code": method.strip()
            })

        # 生成简单的报告内容
        report_content = [{
            "Total Tests": str(len(methods)),
            "Generation Time": "30 seconds",
            "Random Seed": "12345"
        }]

        return JsonResponse({
            "message": "测试用例生成成功",
            "test_case": test_content,
            "report": report_content,
            "test_path": test_file_path
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def save_testcases(request):
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)

    data = json.loads(request.body)

    project_name = data.get("project")  # 前端传来的项目名
    class_name = data.get("className")  # 原类名（含 .java）
    generation_method = data.get("generationMethod")
    result = data.get("result", {})
    test_cases = data.get("testCases", [])

    # ─────────────────────────────────────────────────────────────
    # 1. 取得项目路径、被测文件路径
    # ─────────────────────────────────────────────────────────────

    try:
        project_obj = SourceCodeProject.objects.get(project_name=project_name)
    except SourceCodeProject.DoesNotExist:
        return JsonResponse({"error": "项目不存在"}, status=404)

    try:
        src_file = SourceCodeFile.objects.get(project_id=project_obj.id,
                                              file_name=class_name)
    except SourceCodeFile.DoesNotExist:
        return JsonResponse({"error": "源码文件不存在"}, status=404)

    # 判断是否为Java文件
    is_java_file = class_name.endswith('.java')

    # 获取完整的类名（包含包名）- 只处理Java文件
    if is_java_file:
        full_class_name = extract_java_fqn(src_file.file_path)
        # 提取包名
        package_name = ".".join(full_class_name.split(".")[:-1])
    else:
        # 非Java文件不需要包名
        package_name = ""
        full_class_name = class_name

    # ─────────────────────────────────────────────────────────────
    # 2. 计算*测试*文件完整路径
    #    src/main/java/.../Foo.java → src/test/java/.../FooTest.java
    # ─────────────────────────────────────────────────────────────
    
    # 从文件名中提取类名（去掉扩展名）
    simple_class_name = os.path.splitext(class_name)[0]

    old_path = pathlib.Path(src_file.file_path).as_posix()
    
    # 判断是否为Java文件
    is_java_file = class_name.endswith('.java')
    
    if is_java_file:
        # Java文件保持原有的复杂路径处理
        new_path = (old_path
                    .replace("/src/main/", "/src/test/")  # 目录改 main → test
                    .replace("\\", "/"))
    else:
        # 非Java文件直接保存到src/test目录下
        project_path = project_obj.project_path
        print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        print(project_path)
        new_path = os.path.join(project_path, class_name)
        new_path = new_path.replace("\\", "/")

    # 根据不同的生成方法处理文件名
    if generation_method == "LLM":
        # 获取下一个后缀
        next_suffix = _next_suffix(f"{simple_class_name}Test")
        new_test_class_name = f"{simple_class_name}Test{next_suffix}"
        if is_java_file:
            new_path = re.sub(r"([^/]+)\.java$", f"{new_test_class_name}.java", new_path)
        else:
            # 非Java文件直接使用新的测试类名
            file_ext = os.path.splitext(class_name)[1]  # 获取原始文件扩展名
            new_path = os.path.join(os.path.dirname(new_path), f"{new_test_class_name}{file_ext}")
            new_path = new_path.replace("\\", "/")
    elif generation_method == "EvoSuite":
        # EvoSuite只用于Java文件
        next_suffix = _next_suffix(f"{simple_class_name}_ESTest")
        new_test_class_name = f"{simple_class_name}_ESTest{next_suffix}"
        new_path = re.sub(r"([^/]+)\.java$", f"{new_test_class_name}.java", new_path)
    elif generation_method == "Symbolic":
        next_suffix = _next_suffix(f"{simple_class_name}Test")
        new_test_class_name = f"{simple_class_name}Test{next_suffix}"
        if is_java_file:
            new_path = re.sub(r"([^/]+)\.java$", f"{new_test_class_name}.java", new_path)
        else:
            # 非Java文件直接使用新的测试类名
            file_ext = os.path.splitext(class_name)[1]  # 获取原始文件扩展名
            new_path = os.path.join(os.path.dirname(new_path), f"{new_test_class_name}{file_ext}")
            new_path = new_path.replace("\\", "/")

    # 2-2. 确保目录存在
    target_path = pathlib.Path(new_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # 3. 写测试用例内容
    # ─────────────────────────────────────────────────────────────

    with target_path.open("w", encoding="utf-8") as f:
        if generation_method == "LLM" and test_cases:
            # 对于LLM方法，只保存第一个测试用例
            first_case = test_cases[0]
            # 替换测试用例内容中的类名
            test_content = first_case['code']
            # 只有在Java文件时才添加package声明
            if package_name and new_test_class_name.endswith('.java'):  # 只在Java文件且包名非空时添加package声明
                test_content = f"package {package_name};\n\n" + test_content
            old_test_class_name = f"{simple_class_name}Test"
            test_content = test_content.replace(old_test_class_name, new_test_class_name)
            f.write(f"// {first_case['title']}\n{test_content}\n\n")
        else:
            # 其他方法保存所有测试用例
            for case in test_cases:
                f.write(f"// {case['title']}\n{case['code']}\n\n")

    # ─────────────────────────────────────────────────────────────
    # 4. 写数据库
    # ─────────────────────────────────────────────────────────────

    GeneratedTestCaseFile.objects.create(
        project_name=project_obj,
        generation_method=generation_method,
        class_name=class_name,
        file_name=target_path.name,
        file_path=str(target_path),
        coverage=result.get("coverage"),
        effectiveness=result.get("effectiveness"),
        diversity=result.get("diversity"),
    )

    return JsonResponse({"message": "保存成功", "file_path": str(target_path)})


###################################################################################################################


def generate(request):
    try:
        data = json.loads(request.body)
        project = data.get('project')
        class_name = data.get('className')
        generation_method = data.get('generationMethod')

        print(f"接收到的数据: project={project}, class_name={class_name}, method={generation_method}")

        # 根据不同的生成方法处理
        # if generation_method == 'EvoSuite':
        #     result = generate_with_evosuite(project, class_name, method_name)
        if generation_method == 'LLM':
            print("开始调用LLM生成测试用例")
            result = generate_with_llm(project, class_name)
            print(f"LLM生成结果: {result}")
        # elif generation_method == 'Symbolic':
        #     result = generate_with_symbolic(project, class_name, method_name)
        else:
            return JsonResponse({'error': '不支持的生成方法'}, status=400)

        return JsonResponse(result)

    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        return JsonResponse({'error': f'JSON解析错误: {str(e)}'}, status=400)
    except Exception as e:
        import traceback
        print(f"发生错误: {str(e)}")
        print(f"错误堆栈: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)


from openai import OpenAI

client = OpenAI(
    api_key="sk-45419d65418944dc88190bf13f19fb96",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


def generate_with_llm(project, class_name):
    try:
        # Get the project and file from the database
        project_obj = SourceCodeProject.objects.get(project_name=project)
        source_file = SourceCodeFile.objects.get(
            project=project_obj,
            file_name=class_name
        )

        if not os.path.exists(source_file.file_path):
            return {"error": f"文件未找到：{source_file.file_path}"}

        try:
            with open(source_file.file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # 根据文件类型选择不同的提示词
            if source_file.language == 'Java':
                prompt = f"""
你是一名专业的软件测试工程师。请根据以下Java类的代码，为其生成两个简洁的JUnit测试用例代码。

【项目】：{project}
【类名】：{class_name}

请输出测试用例，要求：
- 使用JUnit格式
- 每个测试用例不超过10行代码
- 只包含最基本的测试逻辑
- 不要添加任何注释
- 用Markdown代码块格式输出，仅Java代码
不要生成任何别的信息和文字，生成两个测试用例
现在请基于以下代码进行生成：
```java
{source_code}
```"""
            else:  # Python
                prompt = f"""
你是一名专业的软件测试工程师。请根据以下Python代码，为其生成两个简洁的pytest测试用例代码。

【项目】：{project}
【文件名】：{class_name}

请输出测试用例，要求：
- 使用pytest格式
- 每个测试用例不超过10行代码
- 只包含最基本的测试逻辑
- 不要添加任何注释
- 用Markdown代码块格式输出，仅Python代码
不要生成任何别的信息和文字，生成两个测试用例
现在请基于以下代码进行生成：
```python
{source_code}
```"""

            # 设置超时时间和最大令牌数
            response = client.chat.completions.create(
                model="qwen2.5-vl-32b-instruct",
                messages=[
                    {"role": "system",
                     "content": "你是专业的软件测试工程师，请生成简洁的测试用例，每个测试用例不超过10行代码，不要添加任何注释"},
                    {"role": "user", "content": prompt}
                ],
                timeout=20,  # 20秒超时
                max_tokens=500  # 限制生成的令牌数
            )

            ai_text = response.choices[0].message.content
            print("API响应内容:", ai_text)

            import re
            # 根据语言选择正确的代码块标记
            lang = 'python' if source_file.language == 'Python' else 'java'
            code_blocks = re.findall(f'```(?:{lang})?\n(.*?)```', ai_text, re.DOTALL)

            test_cases = []
            for i, code in enumerate(code_blocks):
                test_cases.append({
                    "title": f"LLM生成 - 测试用例 {i + 1}",
                    "code": code.strip()
                })

            if not test_cases:
                return {"error": "未能成功生成测试用例，请重试"}

            return {
                "coverage": 80,
                "effectiveness": 85,
                "diversity": 90,
                "testCases": test_cases
            }

        except Exception as e:
            print(f"生成测试用例时出错: {str(e)}")
            return {"error": f"生成测试用例失败: {str(e)}"}

    except SourceCodeProject.DoesNotExist:
        return {"error": f"项目未找到：{project}"}
    except SourceCodeFile.DoesNotExist:
        return {"error": f"源代码文件未找到：{class_name}"}
    

##############################################################测试用例新增
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
import json
from .models import GeneratedTestCaseFile

@method_decorator(csrf_exempt, name='dispatch')
class TestCaseListView(View):
    """获取测试用例列表"""
    def get(self, request):
        try:
            # 获取分页参数
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            
            # 获取过滤参数
            project_name = request.GET.get('project_name', '')
            generation_method = request.GET.get('generation_method', '')
            
            # 构建查询
            queryset = GeneratedTestCaseFile.objects.all().order_by('-created_at')
            
            if project_name:
                queryset = queryset.filter(project_name__icontains=project_name)
            if generation_method:
                queryset = queryset.filter(generation_method=generation_method)
            
            # 分页
            paginator = Paginator(queryset, size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            test_cases = []
            for test_case in page_obj:
                test_cases.append({
                    'id': test_case.id,
                    'project_name': test_case.project_name,
                    'generation_method': test_case.generation_method,
                    'class_name': test_case.class_name,
                    'file_name': test_case.file_name,
                    'file_path': test_case.file_path,
                    'coverage': test_case.coverage,
                    'effectiveness': test_case.effectiveness,
                    'diversity': test_case.diversity,
                    'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return JsonResponse({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'test_cases': test_cases,
                    'total': paginator.count,
                    'page': page,
                    'size': size,
                    'total_pages': paginator.num_pages
                }
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'获取失败: {str(e)}'
            })

@method_decorator(csrf_exempt, name='dispatch')
class TestCaseDetailView(View):
    """测试用例详情、更新、删除"""
    
    def get(self, request, test_case_id):
        """获取测试用例详情"""
        try:
            test_case = GeneratedTestCaseFile.objects.get(id=test_case_id)
            
            # 读取测试用例文件内容
            test_case_content = ""
            try:
                with open(test_case.file_path, 'r', encoding='utf-8') as f:
                    test_case_content = f.read()
            except Exception as e:
                test_case_content = f"无法读取文件内容: {str(e)}"
            
            return JsonResponse({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'id': test_case.id,
                    'project_name': test_case.project_name,
                    'generation_method': test_case.generation_method,
                    'class_name': test_case.class_name,
                    'file_name': test_case.file_name,
                    'file_path': test_case.file_path,
                    'coverage': test_case.coverage,
                    'effectiveness': test_case.effectiveness,
                    'diversity': test_case.diversity,
                    'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': test_case_content
                }
            })
        except GeneratedTestCaseFile.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'message': '测试用例不存在'
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'获取失败: {str(e)}'
            })
    
    def put(self, request, test_case_id):
        """更新测试用例"""
        try:
            test_case = GeneratedTestCaseFile.objects.get(id=test_case_id)
            data = json.loads(request.body)
            
            # 更新字段
            if 'project_name' in data:
                test_case.project_name = data['project_name']
            if 'generation_method' in data:
                test_case.generation_method = data['generation_method']
            if 'class_name' in data:
                test_case.class_name = data['class_name']
            if 'file_name' in data:
                test_case.file_name = data['file_name']
            if 'coverage' in data:
                test_case.coverage = data['coverage']
            if 'effectiveness' in data:
                test_case.effectiveness = data['effectiveness']
            if 'diversity' in data:
                test_case.diversity = data['diversity']
            
            test_case.save()
            
            # 如果有文件内容更新，写入文件
            if 'content' in data:
                try:
                    with open(test_case.file_path, 'w', encoding='utf-8') as f:
                        f.write(data['content'])
                except Exception as e:
                    return JsonResponse({
                        'code': 500,
                        'message': f'更新文件内容失败: {str(e)}'
                    })
            
            return JsonResponse({
                'code': 200,
                'message': '更新成功'
            })
        except GeneratedTestCaseFile.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'message': '测试用例不存在'
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'更新失败: {str(e)}'
            })
    
    def delete(self, request, test_case_id):
        """删除测试用例"""
        try:
            test_case = GeneratedTestCaseFile.objects.get(id=test_case_id)
            
            # 删除文件
            try:
                import os
                if os.path.exists(test_case.file_path):
                    os.remove(test_case.file_path)
            except Exception as e:
                print(f"删除文件失败: {str(e)}")
            
            # 删除数据库记录
            test_case.delete()
            
            return JsonResponse({
                'code': 200,
                'message': '删除成功'
            })
        except GeneratedTestCaseFile.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'message': '测试用例不存在'
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'删除失败: {str(e)}'
            })
    

############################################################合并

import pyodbc
import pandas as pd
import xml.etree.ElementTree as ET
import json
import os
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *


class DataResourceViewSet(viewsets.ModelViewSet):
    """数据资源视图集"""
    
    queryset = DataResource.objects.all()
    serializer_class = DataResourceSerializer
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """测试数据库连接"""
        
        server = request.data.get('server')  
        port = request.data.get('port', 1433)  # SQL Server默认端口1433
        database = request.data.get('database')
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            # 构建SQL Server连接字符串
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
            
            # 尝试连接数据库
            conn = pyodbc.connect(connection_string)
            
            # 连接成功，获取表列表
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                ORDER BY TABLE_NAME
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return Response({
                'success': True,
                'message': f'连接成功! 已找到数据库: {database}',
                'tables': tables
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'连接失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def preview_data(self, request):
        """预览数据"""
        
        resource_type = request.data.get('type')
        
        try:
            if resource_type == 'Excel':
                return self._preview_excel(request)
            elif resource_type == 'SQLServer':  # 改为SQLServer
                return self._preview_sqlserver(request)
            elif resource_type == 'XML':
                return self._preview_xml(request)
            elif resource_type == 'JSON':
                return self._preview_json(request)
            elif resource_type == 'CSV':
                return self._preview_csv(request)
            else:
                return Response({
                    'success': False,
                    'message': f'不支持的数据源类型: {resource_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'预览数据失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _preview_excel(self, request):
        """预览Excel数据"""
        
        file_path = self._get_file_path(request.data.get('path'))
        sheet_name = request.data.get('sheet')
        
        # 读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # 获取可用的工作表
        xl = pd.ExcelFile(file_path)
        sheets = xl.sheet_names
        
        # 将数据转换为字典列表
        data = df.head(10).to_dict('records')
        columns = [{'prop': col, 'label': col} for col in df.columns]
        
        return Response({
            'success': True,
            'data': data,
            'columns': columns,
            'sheets': sheets
        })
    
    def _preview_sqlserver(self, request):
        """预览SQL Server数据"""
        
        server = request.data.get('server')  # 改为server
        port = request.data.get('port', 1433)  # SQL Server默认端口
        database = request.data.get('database')
        username = request.data.get('username')
        password = request.data.get('password')
        table = request.data.get('table')
        
        # 构建SQL Server连接字符串
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
        
        # 连接SQL Server数据库
        conn = pyodbc.connect(connection_string)
        
        # 查询表数据 - SQL Server使用TOP而不是LIMIT
        query = f"SELECT TOP 10 * FROM [{table}]"  # 使用方括号包围表名以防关键字冲突
        df = pd.read_sql(query, conn)
        
        # 关闭连接
        conn.close()
        
        # 将数据转换为字典列表
        data = df.to_dict('records')
        columns = [{'prop': col, 'label': col} for col in df.columns]
        
        return Response({
            'success': True,
            'data': data,
            'columns': columns
        })
    
    def _preview_xml(self, request):
        """预览XML数据"""
        
        file_path = self._get_file_path(request.data.get('path'))
        root_path = request.data.get('rootPath')
        
        # 解析XML文件
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 处理根节点路径
        if root_path:
            elements = root.findall(root_path)
        else:
            elements = [root]
        
        # 提取数据
        data = []
        columns_set = set()
        
        for elem in elements[:10]:  # 仅处理前10个元素
            item = {}
            for child in elem:
                item[child.tag] = child.text
                columns_set.add(child.tag)
            data.append(item)
        
        # 构建列定义
        columns = [{'prop': col, 'label': col} for col in columns_set]
        
        return Response({
            'success': True,
            'data': data,
            'columns': columns
        })
    
    def _preview_json(self, request):
        """预览JSON数据"""
        
        file_path = self._get_file_path(request.data.get('path'))
        data_path = request.data.get('dataPath')
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 处理数据路径
        if data_path:
            path_parts = data_path.split('.')
            for part in path_parts:
                if part in json_data:
                    json_data = json_data[part]
                else:
                    return Response({
                        'success': False,
                        'message': f'数据路径无效: {data_path}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # 确保数据是列表
        if not isinstance(json_data, list):
            json_data = [json_data]
        
        # 只取前10个记录
        data = json_data[:10]
        
        # 构建列定义
        columns_set = set()
        for item in data:
            for key in item.keys():
                columns_set.add(key)
        
        columns = [{'prop': col, 'label': col} for col in columns_set]
        
        return Response({
            'success': True,
            'data': data,
            'columns': columns
        })
    
    def _preview_csv(self, request):
        """预览CSV数据"""
        
        file_path = self._get_file_path(request.data.get('path'))
        delimiter = request.data.get('delimiter', ',')
        has_header = request.data.get('hasHeader', True)
        
        # 读取CSV文件
        df = pd.read_csv(
            file_path,
            delimiter=delimiter,
            header=0 if has_header else None
        )
        
        # 如果没有标题，则添加默认标题
        if not has_header:
            df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
        
        # 将数据转换为字典列表
        data = df.head(10).to_dict('records')
        columns = [{'prop': col, 'label': col} for col in df.columns]
        
        return Response({
            'success': True,
            'data': data,
            'columns': columns
        })
    
    def _get_file_path(self, file_name):
        """获取文件的完整路径"""
        
        return os.path.join(settings.DATA_FILES_ROOT, file_name)
    
    @action(detail=False, methods=['post'])
    def upload_file(self, request):
        """上传数据文件"""
        
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'message': '未提供文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # 确保目录存在
        os.makedirs(settings.DATA_FILES_ROOT, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(settings.DATA_FILES_ROOT, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        return Response({
            'success': True,
            'message': '文件上传成功',
            'path': file.name
        })
    
    @action(detail=False, methods=['get'])
    def filter(self, request):
        """过滤数据源"""
    
        keyword = request.query_params.get('keyword', '')
        type_filter = request.query_params.get('type', '')
    
        queryset = DataResource.objects.all()
    
        if keyword:
            queryset = queryset.filter(name__icontains=keyword)
    
        if type_filter:
            queryset = queryset.filter(type=type_filter)
    
        queryset = queryset.order_by('id')
    
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

# ###############################################新增

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import JsonResponse
import json
import os
import datetime

from .models import EnvironmentResource, DataResource
from .serializers import EnvironmentResourceSerializer, DataResourceSerializer


class EnvironmentResourceViewSet(viewsets.ModelViewSet):
    """环境资源配置ViewSet"""
    queryset = EnvironmentResource.objects.all()
    serializer_class = EnvironmentResourceSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def create(self, request, *args, **kwargs):
        """创建环境资源配置"""
        try:
            print(f"Request data: {request.data}")
            print(f"Request content type: {request.content_type}")
            
            # 创建环境资源目录
            env_dir = r'D:\ruanjian\source_code'
            os.makedirs(env_dir, exist_ok=True)
            
            # Get file content from request
            file_content = request.data.get('file_content', '')
            file_name = request.data.get('file_name', '')
            
            # Generate unique filename if needed
            if not file_name:
                if request.data.get('type') == 'Python':
                    file_name = 'requirements.txt'
                elif request.data.get('type') == 'Java':
                    file_name = 'pom.xml'
            
            # Create a subdirectory for this resource (optional, for better organization)
            resource_name = request.data.get('name', 'default').replace(' ', '_')
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            sub_dir = os.path.join(env_dir, f"{resource_name}")
            os.makedirs(sub_dir, exist_ok=True)
            
            # Full file path
            file_path = os.path.join(sub_dir, file_name)
            
            # Write file content to disk
            if file_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            
            # Update request data with real file path
            mutable_data = request.data.copy()
            mutable_data['file_path'] = file_path
            
            # Process with serializer
            serializer = self.get_serializer(data=mutable_data)
            
            if serializer.is_valid():
                instance = serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                # If validation fails, clean up the created file
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(sub_dir) and not os.listdir(sub_dir):
                    os.rmdir(sub_dir)
                
                print(f"Serializer errors: {serializer.errors}")
                return Response(
                    {
                        'errors': serializer.errors,
                        'message': '数据验证失败'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            print(f"Create error: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'message': '创建环境资源配置失败'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """更新环境资源配置"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Check if file content is being updated
            if 'file_content' in request.data:
                file_content = request.data.get('file_content', '')
                
                # If file_path exists, update the file
                if instance.file_path and os.path.exists(instance.file_path):
                    with open(instance.file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                else:
                    # Create new file if path doesn't exist
                    env_dir = r'D:\ruanjian\source_code'
                    os.makedirs(env_dir, exist_ok=True)
                    
                    resource_name = instance.name.replace(' ', '_')
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    sub_dir = os.path.join(env_dir, f"{resource_name}")
                    os.makedirs(sub_dir, exist_ok=True)
                    
                    file_name = instance.file_name or ('requirements.txt' if instance.type == 'Python' else 'pom.xml')
                    file_path = os.path.join(sub_dir, file_name)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    # Update the file_path in request data
                    mutable_data = request.data.copy()
                    mutable_data['file_path'] = file_path
                    request._full_data = mutable_data
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(
                    {
                        'errors': serializer.errors,
                        'message': '数据验证失败'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {
                    'error': str(e),
                    'message': '更新环境资源配置失败'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """删除环境资源配置"""
        try:
            instance = self.get_object()
            
            # Delete the actual file if it exists
            if instance.file_path and os.path.exists(instance.file_path):
                os.remove(instance.file_path)
                
                # Try to remove the parent directory if it's empty
                parent_dir = os.path.dirname(instance.file_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
            
            # Call parent destroy method
            return super().destroy(request, *args, **kwargs)
            
        except Exception as e:
            return Response(
                {
                    'error': str(e),
                    'message': '删除环境资源配置失败'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def upload_file(self, request):
        """文件上传接口"""
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response(
                    {'error': '未找到上传的文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read file content
            file_content = uploaded_file.read().decode('utf-8')
            
            # Determine type based on filename
            file_name = uploaded_file.name
            if file_name.endswith('.txt') or file_name == 'requirements.txt':
                env_type = 'Python'
            elif file_name.endswith('.xml') or file_name == 'pom.xml':
                env_type = 'Java'
            else:
                return Response(
                    {'error': '不支持的文件类型，仅支持requirements.txt和pom.xml'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the environment resources directory
            env_dir = r'D:\ruanjian\source_code'
            os.makedirs(env_dir, exist_ok=True)
            
            # Create subdirectory
            resource_name = request.data.get('name', f'上传的{env_type}环境配置').replace(' ', '_')
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            sub_dir = os.path.join(env_dir, f"{resource_name}")
            os.makedirs(sub_dir, exist_ok=True)
            
            # Save file to disk
            file_path = os.path.join(sub_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.read())
            
            # Construct data
            data = {
                'name': request.data.get('name', f'上传的{env_type}环境配置'),
                'type': env_type,
                'file_name': file_name,
                'file_path': file_path,  # Real file path
                'file_content': file_content,
                'description': request.data.get('description', '')
            }
            
            # Add type-specific fields
            if env_type == 'Python':
                data['python_version'] = request.data.get('python_version', '')
                data['virtual_env_name'] = request.data.get('virtual_env_name', '')
            elif env_type == 'Java':
                data['java_version'] = request.data.get('java_version', '')
                data['maven_version'] = request.data.get('maven_version', '')
                data['group_id'] = request.data.get('group_id', '')
                data['artifact_id'] = request.data.get('artifact_id', '')
                data['version'] = request.data.get('version', '1.0.0')
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Clean up if validation fails
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(sub_dir) and not os.listdir(sub_dir):
                    os.rmdir(sub_dir)
                
                return Response(
                    {
                        'errors': serializer.errors,
                        'message': '文件内容验证失败'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {
                    'error': str(e),
                    'message': '文件上传失败'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_file(self, request, pk=None):
        """下载配置文件"""
        try:
            instance = self.get_object()
            
            # Read file content from disk if file exists
            file_content = instance.file_content
            if instance.file_path and os.path.exists(instance.file_path):
                with open(instance.file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            
            response = JsonResponse({
                'file_name': instance.file_name,
                'file_content': file_content,
                'file_path': instance.file_path,
                'type': instance.type
            })
            
            return response
            
        except Exception as e:
            return Response(
                {
                    'error': str(e),
                    'message': '下载文件失败'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['get'])
    def filter(self, request):
        queryset = self.get_queryset()
        keyword = request.query_params.get('keyword', '')
        resource_type = request.query_params.get('type', '')
        if keyword:
            queryset = queryset.filter(name__icontains=keyword)
        if resource_type:
            queryset = queryset.filter(type=resource_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

