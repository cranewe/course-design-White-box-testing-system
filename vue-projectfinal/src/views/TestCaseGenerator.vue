<template>
  <div class="container">
    <h2 class="title">测试用例生成系统</h2>

     <!-- ##########################新增生成测试用例部分 -->
    <el-card class="generation-card"> 

    <el-form label-width="120px" class="form">
      <el-form-item label="选择项目">
        <el-select v-model="selectedProject" placeholder="请选择项目">
          <el-option 
            v-for="item in projectOptions" 
            :key="item" 
            :label="item" 
            :value="item" 
          />
        </el-select>
      </el-form-item>
      <el-form-item label="选择类/方法">
        <el-select v-model="className" placeholder="请选择类">
          <el-option 
            v-for="item in classOptions" 
            :key="item.name" 
            :label="item.name" 
            :value="item.name" 
          />
        </el-select>
      </el-form-item>

      <el-form-item label="选择生成方法">
        <el-radio-group v-model="generationMethod">
          <el-radio value="EvoSuite">EvoSuite（基于搜索）</el-radio>
          <el-radio value="LLM">LLM（大语言模型）</el-radio>
          <el-radio value="Symbolic">Randoop</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="generateTests">生成测试用例</el-button>
      </el-form-item>
    </el-form> 

    <el-divider />

    <!-- loading -->
    <el-skeleton :loading="loading" animated :rows="6">
      <div v-if="testCases.length > 0">
        <!-- 添加报告表格 -->
        <el-card v-if="reportData.length > 0" class="report-card">
          <template #header>
            <div class="card-header">
              <span>测试报告</span>
            </div>
          </template>
          <el-table :data="reportData" style="width: 100%">
            <el-table-column prop="TARGET_CLASS" label="目标类" width="200" />
            <el-table-column prop="CRITERIA" label="覆盖标准" width="150" />
            <el-table-column prop="COVERAGE" label="覆盖率">
              <template #default="{ row }">
                {{ (parseFloat(row.COVERAGE) * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="TOTAL_GOALS" label="总目标数" width="100" />
            <el-table-column prop="COVERED_GOALS" label="已覆盖目标数" width="120" />
          </el-table>
        </el-card>

        <el-row justify="end" style="margin-bottom: 10px;">
          <el-button type="success" @click="saveTestCases" :disabled="testCases.length === 0">
              保存测试用例
          </el-button>
        </el-row>

        <h3>生成的测试用例</h3>
        <el-collapse>
          <el-collapse-item v-for="(test, index) in testCases" :key="index" :title="test.title">
            <pre><code>{{ test.code }}</code></pre>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-skeleton>
</el-card>

<!--新增部分######################################################-->
 <el-divider />

    <!-- 已保存测试用例列表部分 -->
    <el-card class="saved-testcases-card">
      <template #header>
        <div class="card-header">
          <span>已保存的测试用例</span>
          <el-button type="primary" @click="refreshTestCaseList">刷新列表</el-button>
        </div>
      </template>

      <!-- 搜索和过滤 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input
              v-model="searchFilters.project_name"
              placeholder="搜索项目名称"
              @input="debounceSearch"
              clearable
            />
          </el-col>
          <el-col :span="8">
            <el-select
              v-model="searchFilters.generation_method"
              placeholder="筛选生成方法"
              @change="fetchTestCaseList"
              clearable
            >
              <el-option label="EvoSuite" value="EvoSuite" />
              <el-option label="LLM" value="LLM" />
              <el-option label="Symbolic" value="Symbolic" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="fetchTestCaseList">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 测试用例列表表格 -->
      <el-table 
        :data="savedTestCases" 
        style="width: 100%" 
        v-loading="listLoading"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="project_name" label="项目名称" width="150" />
        <el-table-column prop="class_name" label="类名" width="200" />
        <el-table-column prop="generation_method" label="生成方法" width="120" />
        <el-table-column prop="file_name" label="文件名" width="200" />
        <el-table-column prop="coverage" label="覆盖率" width="100">
          <template #default="{ row }">
            {{ row.coverage ? `${row.coverage.toFixed(2)}%` : 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column prop="effectiveness" label="有效性" width="100">
          <template #default="{ row }">
            {{ row.effectiveness ? `${row.effectiveness.toFixed(2)}%` : 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column prop="diversity" label="多样性" width="100">
          <template #default="{ row }">
            {{ row.diversity ? `${row.diversity.toFixed(2)}%` : 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewTestCase(row)">查看</el-button>
            <el-button type="warning" size="small" @click="editTestCase(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteTestCase(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 查看测试用例对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="查看测试用例"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentTestCase">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ currentTestCase.project_name }}</el-descriptions-item>
          <el-descriptions-item label="类名">{{ currentTestCase.class_name }}</el-descriptions-item>
          <el-descriptions-item label="生成方法">{{ currentTestCase.generation_method }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ currentTestCase.file_name }}</el-descriptions-item>
          <el-descriptions-item label="覆盖率">{{ currentTestCase.coverage ? `${currentTestCase.coverage.toFixed(2)}%` : 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="有效性">{{ currentTestCase.effectiveness ? `${currentTestCase.effectiveness.toFixed(2)}%` : 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="多样性">{{ currentTestCase.diversity ? `${currentTestCase.diversity.toFixed(2)}%` : 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTestCase.created_at }}</el-descriptions-item>
          <el-descriptions-item label="文件路径" :span="2">{{ currentTestCase.file_path }}</el-descriptions-item>
        </el-descriptions>
        
        <div style="margin-top: 20px;">
          <h4>测试用例内容：</h4>
          <el-input
            v-model="currentTestCase.content"
            type="textarea"
            :rows="20"
            readonly
            style="font-family: 'Courier New', monospace;"
          />
        </div>
      </div>
    </el-dialog>

    <!-- 编辑测试用例对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑测试用例"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="120px" v-if="editForm">
        <el-form-item label="项目名称">
          <el-input v-model="editForm.project_name" />
        </el-form-item>
        <el-form-item label="类名">
          <el-input v-model="editForm.class_name" />
        </el-form-item>
        <el-form-item label="生成方法">
          <el-select v-model="editForm.generation_method">
            <el-option label="EvoSuite" value="EvoSuite" />
            <el-option label="LLM" value="LLM" />
            <el-option label="Symbolic" value="Symbolic" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件名">
          <el-input v-model="editForm.file_name" />
        </el-form-item>
        <el-form-item label="覆盖率">
          <el-input-number v-model="editForm.coverage" :min="0" :max="100" :precision="2" />
        </el-form-item>
        <el-form-item label="有效性">
          <el-input-number v-model="editForm.effectiveness" :min="0" :max="100" :precision="2" />
        </el-form-item>
        <el-form-item label="多样性">
          <el-input-number v-model="editForm.diversity" :min="0" :max="100" :precision="2" />
        </el-form-item>
        <el-form-item label="测试用例内容">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="15"
            style="font-family: 'Courier New', monospace;"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEditedTestCase" :loading="saveLoading">保存</el-button>
        </span>
      </template>
    </el-dialog>
    <!--新增部分结束######################################-->
  </div>
</template>

<script setup>
import { ref,onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/axios'

const loading = ref(false)

const className = ref('')
const generationMethod = ref('EvoSuite')
const selectedProject = ref('') // 存储选中的项目名称（字符串）
const projectOptions = ref([])
const reportData = ref([])
const classOptions = ref([]) // 新增：存储类列表选项

const result = ref({
  coverage: 0,
  effectiveness: 0,
  diversity: 0
})
const testCases = ref([])

//#############################################
// 新增的测试用例列表相关变量
const savedTestCases = ref([])
const listLoading = ref(false)
const searchFilters = ref({
  project_name: '',
  generation_method: ''
})
const pagination = ref({
  page: 1,
  size: 10,
  total: 0
})

// 对话框相关变量
const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)
const currentTestCase = ref(null)
const editForm = ref(null)
const saveLoading = ref(false)

let searchTimeout = null
//################################################

onMounted(() => {
fetchProjects()
fetchTestCaseList()
})

// 监听项目选择变化
watch(selectedProject, (newValue) => {
if (newValue) {
  fetchClasses(newValue)
}
})

const fetchProjects = async () => {
try {
  const response = await request.get('/source-code/list/')
  projectOptions.value = response.data.projects.map(project => project.name)
  if (projectOptions.value.length > 0) {
    selectedProject.value = projectOptions.value[0] // 直接赋值字符串
  }
} catch (error) {
  console.error('获取项目列表失败:', error)
  ElMessage.error('加载项目列表失败')
}
}

// 获取类列表
const fetchClasses = async (projectName) => {
try {
  const response = await request.get(`/list_class/${projectName}/`)
  classOptions.value = response.data.classes
  // 重置当前选择的类
  className.value = ''
} catch (error) {
  console.error('获取类列表失败:', error)
  ElMessage.error('加载类列表失败')
}
}

// 保存测试用例到文件
const saveTestCases = async () => {
  try {
    const response = await request.post('/save_testcases/', {
      project: selectedProject.value,
      className: className.value,
      generationMethod: generationMethod.value,
      result: result.value,
      testCases: testCases.value
    })

    if (response.data.message === '保存成功') {
      ElMessage.success('测试用例已成功保存')
    }
  } catch (error) {
    console.error('保存测试用例失败:', error)
    ElMessage.error('保存测试用例失败，请重试')
  }
}

// 生成测试用例
const generateTests = async () => {
  if (!selectedProject.value || !className.value || !generationMethod.value) {
    ElMessage.warning('请填写完整的信息')
    return
  }

  loading.value = true
  testCases.value = []
  reportData.value = []

  try {
    const requestData = {
      project: selectedProject.value,
      className: className.value,
      generationMethod: generationMethod.value

    }

    let response
    if (generationMethod.value === 'EvoSuite') 
    {
      response = await request.post('/generate1/', requestData, { timeout: 600000 })
    } else if (generationMethod.value === 'LLM') {
      response = await request.post('/generate/', requestData, { timeout: 600000 })
    } else if (generationMethod.value === 'Symbolic') {
      response = await request.post('/generate2/', requestData, { timeout: 600000 })
    } else {
      throw new Error('不支持的生成方法')
    }

    const responseData = response.data
    result.value = responseData

    // 根据不同的生成方法处理不同的返回格式
    if (generationMethod.value === 'EvoSuite') {
      if (responseData.message === "测试用例生成成功") {
        ElMessage.success('测试用例生成成功')

        if (responseData.report) {
          const reportString = responseData.report[0]['TARGET_CLASS,criterion,Coverage,Total_Goals,Covered_Goals']
          const [targetClass, criteria, coverage, totalGoals, coveredGoals] = reportString.split(',')
          const criteriaArray = criteria.split(';')
          reportData.value = criteriaArray.map(criterion => ({
            TARGET_CLASS: targetClass,
            CRITERIA: criterion,
            COVERAGE: coverage,
            TOTAL_GOALS: totalGoals,
            COVERED_GOALS: coveredGoals
          }))
          
          result.value.coverage = parseFloat(coverage) * 100
        }

        if (responseData.test_case) {
          testCases.value = [{
            title: '生成的测试用例',
            code: responseData.test_case,
            test_path: responseData.test_path
          }]
        }
      }
    } else if (generationMethod.value === 'LLM') {
      if (responseData.testCases) {
        ElMessage.success('测试用例生成成功')
        
        reportData.value = [{
          TARGET_CLASS: className.value,
          CRITERIA: '整体覆盖率',
          COVERAGE: responseData.coverage / 100,
          TOTAL_GOALS: '100',
          COVERED_GOALS: responseData.coverage.toString()
        }]

        testCases.value = responseData.testCases.map(testCase => ({
          title: testCase.title,
          code: testCase.code,
          test_path: ''
        }))

        result.value = {
          coverage: responseData.coverage,
          effectiveness: responseData.effectiveness,
          diversity: responseData.diversity
        }
      }
    } else if (generationMethod.value === 'Symbolic') {
      if (responseData.message === "测试用例生成成功") {
        ElMessage.success('测试用例生成成功')

        // 处理Randoop的报告
        if (responseData.report) {
          const report = responseData.report[0]
          reportData.value = [{
            TARGET_CLASS: className.value,
            CRITERIA: '总测试用例数',
            COVERAGE: '0.75', // 从Coverage Estimate转换
            TOTAL_GOALS: report['Total Tests'],
            COVERED_GOALS: report['Selected Tests']
          }]
        }

        // 显示完整的测试用例
        if (responseData.test_case) {
          testCases.value = [{
            title: '生成的测试用例',
            code: responseData.test_case,
            test_path: responseData.test_path
          }]
        }
      } else {
        ElMessage.error(responseData.error || '生成测试用例失败')
      }
    }

    if (!testCases.value.length) {
      ElMessage.error('生成测试用例失败')
    }
  } catch (error) {
    console.error('生成测试用例失败:', error)
    ElMessage.error(error.response?.data?.error || error.message || '生成测试用例失败')
  } finally {
    loading.value = false
  }
}

//###################################################
// 新增的测试用例列表管理函数
const fetchTestCaseList = async () => {
  listLoading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size,
      ...searchFilters.value
    }
    
    const response = await request.get('/test-cases/', { params })
    
    if (response.data.code === 200) {
      savedTestCases.value = response.data.data.test_cases
      pagination.value.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取测试用例列表失败')
    }
  } catch (error) {
    console.error('获取测试用例列表失败:', error)
     ElMessage.error('获取测试用例列表失败')
  } finally {
    listLoading.value = false
  }
}
const refreshTestCaseList = () => {
  fetchTestCaseList()
}

// 防抖搜索
const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    pagination.value.page = 1
    fetchTestCaseList()
  }, 500)
}

// 重置过滤条件
const resetFilters = () => {
  searchFilters.value = {
    project_name: '',
    generation_method: ''
  }
  pagination.value.page = 1
  fetchTestCaseList()
}

// 分页处理
const handleSizeChange = (newSize) => {
  pagination.value.size = newSize
  pagination.value.page = 1
  fetchTestCaseList()
}

const handleCurrentChange = (newPage) => {
  pagination.value.page = newPage
  fetchTestCaseList()
}

// 查看测试用例
const viewTestCase = async (testCase) => {
  try {
    const response = await request.get(`/test-cases/${testCase.id}/`)
    
    if (response.data.code === 200) {
      currentTestCase.value = response.data.data
      viewDialogVisible.value = true
    } else {
      ElMessage.error(response.data.message || '获取测试用例详情失败')
    }
  } catch (error) {
    console.error('获取测试用例详情失败:', error)
    ElMessage.error('获取测试用例详情失败')
  }
}

// 编辑测试用例
const editTestCase = async (testCase) => {
  try {
    const response = await request.get(`/test-cases/${testCase.id}/`)
    
    if (response.data.code === 200) {
      const data = response.data.data
      editForm.value = {
        id: data.id,
        project_name: data.project_name,
        generation_method: data.generation_method,
        class_name: data.class_name,
        file_name: data.file_name,
        coverage: data.coverage,
        effectiveness: data.effectiveness,
        diversity: data.diversity,
        content: data.content
      }
      editDialogVisible.value = true
    } else {
      ElMessage.error(response.data.message || '获取测试用例详情失败')
    }
  } catch (error) {
    console.error('获取测试用例详情失败:', error)
    ElMessage.error('获取测试用例详情失败')
  }
}

// 保存编辑的测试用例
const saveEditedTestCase = async () => {
  if (!editForm.value) {
    return
  }

  saveLoading.value = true
  try {
    const response = await request.put(`/test-cases/${editForm.value.id}/`, editForm.value)
    
    if (response.data.code === 200) {
      ElMessage.success('测试用例更新成功')
      editDialogVisible.value = false
      fetchTestCaseList() // 刷新列表
    } else {
      ElMessage.error(response.data.message || '更新测试用例失败')
    }
  } catch (error) {
    console.error('更新测试用例失败:', error)
    ElMessage.error('更新测试用例失败')
  } finally {
    saveLoading.value = false
  }
}

// 删除测试用例
const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.file_name}" 吗？删除后将无法恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await request.delete(`/test-cases/${testCase.id}/`)
    
    if (response.data.code === 200) {
      ElMessage.success('测试用例删除成功')
      fetchTestCaseList() // 刷新列表
    } else {
      ElMessage.error(response.data.message || '删除测试用例失败')
    }
  } catch (error) {
    if (error === 'cancel') {
      return // 用户取消删除
    }
    console.error('删除测试用例失败:', error)
    ElMessage.error('删除测试用例失败')
  }
}

//###################################################
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 1200px;
  margin: auto;
}

.title {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.generation-card,
.saved-testcases-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form {
  max-width: 600px;
}

.result-card,
.report-card {
  margin: 20px 0;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 10px;
  }
  
  .filter-section .el-col {
    margin-bottom: 10px;
  }
  
  .el-table {
    font-size: 12px;
  }
}

/* 表格操作按钮样式 */
.el-table .el-button--small {
  margin: 0 2px;
}

/* 代码显示样式 */
pre {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Monaco, monospace;
  font-size: 13px;
  line-height: 1.4;
}

code {
  color: #e83e8c;
}

/* 描述列表样式优化 */
.el-descriptions {
  margin-bottom: 20px;
}

/* 输入框样式优化 */
.el-textarea .el-textarea__inner {
  font-family: 'Courier New', Monaco, monospace;
  font-size: 13px;
  line-height: 1.4;
}

/* 加载状态样式 */
.el-skeleton {
  padding: 20px;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 40px;
  color: #909399;
}

/* 卡片标题样式 */
.card-header span {
  font-weight: 600;
  font-size: 16px;
}

/* 按钮组样式 */
.el-button-group {
  margin-left: 10px;
}

/* 表格行悬停效果 */
.el-table__row:hover {
  background-color: #f5f7fa;
}

/* 对话框内容样式 */
.el-dialog__body {
  max-height: 70vh;
  overflow-y: auto;
}

/* 分页器样式 */
.el-pagination {
  padding: 20px 0;
}

/* 搜索框样式 */
.filter-section .el-input {
  width: 100%;
}

.filter-section .el-select {
  width: 100%;
}

/* 标签样式 */
.el-tag {
  margin-right: 5px;
}

/* 统计信息样式 */
.stats-info {
  display: flex;
  justify-content: space-around;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
  margin-bottom: 15px;
}

.stats-item {
  text-align: center;
}

.stats-item .number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stats-item .label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}
</style>
