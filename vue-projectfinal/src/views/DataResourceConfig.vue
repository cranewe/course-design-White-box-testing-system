<template>
  <div class="data-resource-config">
    <el-page-header title="返回" @back="goBack">
      <template #content>
        <h2>数据资源配置</h2>
      </template>
      <template #extra>
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon> 添加数据源
        </el-button>
        <el-button type="success" @click="showAddEnvironmentDialog" style="margin-left: 10px;">
          <el-icon><Setting /></el-icon> 添加环境资源
        </el-button>
      </template>
    </el-page-header>

    <!-- 资源类型切换标签 -->
    <el-card class="tab-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="数据源" name="datasource">
          <!-- 数据源过滤器 -->
          <el-card class="filter-card">
            <el-form :inline="true" :model="filterForm">
              <el-form-item label="搜索数据源">
                <el-input v-model="filterForm.keyword" placeholder="输入数据源名称"></el-input>
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="filterForm.type" placeholder="所有类型">
                  <el-option label="Excel" value="Excel"></el-option>
                  <el-option label="SQL Server" value="SQLServer"></el-option>
                  <el-option label="XML" value="XML"></el-option>
                  <el-option label="JSON" value="JSON"></el-option>
                  <el-option label="CSV" value="CSV"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="searchDataSources">搜索</el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 数据源列表 -->
          <el-card>
            <template #header>
              <div class="card-header">
                <span>数据源列表</span>
                <div>
                  <el-tag type="info">总计: {{ dataSources.length }}</el-tag>
                </div>
              </div>
            </template>

            <el-table :data="paginatedDataSources" style="width: 100%">
              <el-table-column prop="name" label="数据源名称"></el-table-column>
              <el-table-column prop="type" label="类型">
                <template #default="{ row }">
                  <el-tag :type="getTypeTagType(row.type)">
                    {{ row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="path" label="文件路径/连接信息"></el-table-column>
              <el-table-column prop="sheet" label="工作表/表名" v-if="hasSheetOrTableColumn"></el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="editDataSource(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-pagination
              class="pagination"
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 30, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredDataSources.length"
            />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="环境资源" name="environment">
          <!-- 环境资源过滤器 -->
          <el-card class="filter-card">
            <el-form :inline="true" :model="environmentFilterForm">
              <el-form-item label="搜索环境资源">
                <el-input v-model="environmentFilterForm.keyword" placeholder="输入环境资源名称"></el-input>
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="environmentFilterForm.type" placeholder="所有类型">
                  <el-option label="Python" value="Python"></el-option>
                  <el-option label="Java" value="Java"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="searchEnvironmentResources">搜索</el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 环境资源列表 -->
          <el-card>
            <template #header>
              <div class="card-header">
                <span>环境资源列表</span>
                <div>
                  <el-tag type="info">总计: {{ environmentResources.length }}</el-tag>
                </div>
              </div>
            </template>

            <el-table :data="paginatedEnvironmentResources" style="width: 100%">
              <el-table-column prop="name" label="环境资源名称"></el-table-column>
              <el-table-column prop="type" label="类型">
                <template #default="{ row }">
                  <el-tag :type="getEnvironmentTypeTagType(row.type)">
                    {{ row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="file_name" label="配置文件"></el-table-column>
              <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
              <el-table-column prop="is_active" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="editEnvironmentResource(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="confirmDeleteEnvironment(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-pagination
              class="pagination"
              v-model:current-page="environmentCurrentPage"
              v-model:page-size="environmentPageSize"
              :page-sizes="[10, 20, 30, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredEnvironmentResources.length"
            />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加/编辑数据源对话框 -->
    <el-dialog v-model="dataSourceDialogVisible" :title="isEdit ? '编辑数据源' : '添加数据源'" width="50%">
      <div class="data-source-type-selection" v-if="!isEdit">
        <h3>数据源类型</h3>
        <el-radio-group v-model="selectedType" class="data-source-type-group">
          <el-radio-button label="Excel">
            <el-icon><Document /></el-icon> Excel 电子表格
          </el-radio-button>
          <el-radio-button label="SQLServer">
            <el-icon><Platform /></el-icon> SQL Server 数据库
          </el-radio-button>
          <el-radio-button label="XML">
            <el-icon><Document /></el-icon> XML 文件
          </el-radio-button>
          <el-radio-button label="JSON">
            <el-icon><Document /></el-icon> JSON 文件
          </el-radio-button>
          <el-radio-button label="CSV">
            <el-icon><Document /></el-icon> CSV 文件
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- Excel表格配置 -->
      <div v-if="selectedType === 'Excel' || (isEdit && dataSourceForm.type === 'Excel')">
        <h3>Excel 数据源配置</h3>
        <el-form :model="dataSourceForm" label-width="120px">
          <el-form-item label="数据源名称" required>
            <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称"></el-input>
          </el-form-item>
          <el-form-item label="文件路径" required>
            <el-input v-model="dataSourceForm.path" placeholder="选择Excel文件">
              <template #append>
                <el-button @click="openFileBrowser('excel')">浏览</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="工作表">
            <el-select v-model="dataSourceForm.sheet" placeholder="选择工作表">
              <el-option v-for="sheet in availableSheets" :key="sheet" :label="sheet" :value="sheet"></el-option>
            </el-select>
          </el-form-item>
        </el-form>

        <!-- 预览数据 -->
        <div class="preview-data" v-if="dataSourceForm.path && dataSourceForm.sheet">
          <h3>预览数据</h3>
          <el-table :data="previewData" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col.prop" :prop="col.prop" :label="col.label"></el-table-column>
          </el-table>
        </div>
      </div>

      <!-- SQL Server数据库配置部分 -->
      <div v-if="selectedType === 'SQLServer' || (isEdit && dataSourceForm.type === 'SQLServer')">
        <h3>SQL Server 数据库配置</h3>
        <el-form :model="dataSourceForm" label-width="120px">
          <el-form-item label="数据源名称" required>
            <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称"></el-input>
          </el-form-item>
          <el-form-item label="服务器地址" required>
            <el-input v-model="dataSourceForm.server" placeholder="例如: localhost 或 192.168.1.100"></el-input>
          </el-form-item>
          <el-form-item label="端口">
            <el-input v-model="dataSourceForm.port" placeholder="例如: 1433 (默认端口)"></el-input>
          </el-form-item>
          <el-form-item label="数据库名称" required>
            <el-input v-model="dataSourceForm.database" placeholder="输入数据库名称"></el-input>
          </el-form-item>
          <el-form-item label="身份验证">
            <el-radio-group v-model="dataSourceForm.authType">
              <el-radio label="sqlserver">SQL Server 身份验证</el-radio>
              <el-radio label="windows">Windows 身份验证</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="用户名" required v-if="dataSourceForm.authType === 'sqlserver'">
            <el-input v-model="dataSourceForm.username" placeholder="输入用户名"></el-input>
          </el-form-item>
          <el-form-item label="密码" required v-if="dataSourceForm.authType === 'sqlserver'">
            <el-input v-model="dataSourceForm.password" type="password" placeholder="输入密码"></el-input>
          </el-form-item>
          <el-form-item label="连接超时(秒)">
            <el-input-number v-model="dataSourceForm.timeout" :min="1" :max="300" placeholder="30"></el-input-number>
          </el-form-item>
          <el-form-item label="加密连接">
            <el-switch v-model="dataSourceForm.encrypt"></el-switch>
          </el-form-item>
          <el-form-item label="信任服务器证书">
            <el-switch v-model="dataSourceForm.trustServerCertificate"></el-switch>
          </el-form-item>
          <el-button class="connect-btn" type="primary" @click="testConnection">测试连接</el-button>
        </el-form>

        <!-- 预览数据 -->
        <div class="preview-data" v-if="dataSourceForm.table && sqlServerConnectionStatus === 'success'">
          <h3>预览数据</h3>
          <el-table :data="previewData" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col.prop" :prop="col.prop" :label="col.label"></el-table-column>
          </el-table>
        </div>
      </div>

      <!-- XML文件配置 -->
      <div v-if="selectedType === 'XML' || (isEdit && dataSourceForm.type === 'XML')">
        <h3>XML 文件配置</h3>
        <el-form :model="dataSourceForm" label-width="120px">
          <el-form-item label="数据源名称" required>
            <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称"></el-input>
          </el-form-item>
          <el-form-item label="文件路径" required>
            <el-input v-model="dataSourceForm.path" placeholder="选择XML文件">
              <template #append>
                <el-button @click="openFileBrowser('xml')">浏览</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="根节点路径">
            <el-input v-model="dataSourceForm.rootPath" placeholder="例如: /root/items"></el-input>
          </el-form-item>
        </el-form>

        <!-- 预览数据 -->
        <div class="preview-data" v-if="dataSourceForm.path">
          <h3>预览数据</h3>
          <el-table :data="previewData" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col.prop" :prop="col.prop" :label="col.label"></el-table-column>
          </el-table>
        </div>
      </div>

      <!-- JSON文件配置 -->
      <div v-if="selectedType === 'JSON' || (isEdit && dataSourceForm.type === 'JSON')">
        <h3>JSON 文件配置</h3>
        <el-form :model="dataSourceForm" label-width="120px">
          <el-form-item label="数据源名称" required>
            <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称"></el-input>
          </el-form-item>
          <el-form-item label="文件路径" required>
            <el-input v-model="dataSourceForm.path" placeholder="选择JSON文件">
              <template #append>
                <el-button @click="openFileBrowser('json')">浏览</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="数据路径">
            <el-input v-model="dataSourceForm.dataPath" placeholder="例如: data.items"></el-input>
          </el-form-item>
        </el-form>

        <!-- 预览数据 -->
        <div class="preview-data" v-if="dataSourceForm.path">
          <h3>预览数据</h3>
          <el-table :data="previewData" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col.prop" :prop="col.prop" :label="col.label"></el-table-column>
          </el-table>
        </div>
      </div>

      <!-- CSV文件配置 -->
      <div v-if="selectedType === 'CSV' || (isEdit && dataSourceForm.type === 'CSV')">
        <h3>CSV 文件配置</h3>
        <el-form :model="dataSourceForm" label-width="120px">
          <el-form-item label="数据源名称" required>
            <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称"></el-input>
          </el-form-item>
          <el-form-item label="文件路径" required>
            <el-input v-model="dataSourceForm.path" placeholder="选择CSV文件">
              <template #append>
                <el-button @click="openFileBrowser('csv')">浏览</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="分隔符">
            <el-select v-model="dataSourceForm.delimiter" placeholder="选择分隔符">
              <el-option label="逗号(,)" value=","></el-option>
              <el-option label="分号(;)" value=";"></el-option>
              <el-option label="制表符(Tab)" value="\t"></el-option>
              <el-option label="竖线(|)" value="|"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="包含表头">
            <el-switch v-model="dataSourceForm.hasHeader"></el-switch>
          </el-form-item>
        </el-form>

        <!-- 预览数据 -->
        <div class="preview-data" v-if="dataSourceForm.path">
          <h3>预览数据</h3>
          <el-table :data="previewData" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col.prop" :prop="col.prop" :label="col.label"></el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dataSourceDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteDataSource" v-if="isEdit">删除数据源</el-button>
          <el-button type="primary" @click="submitDataSource">{{ isEdit ? '保存配置' : '保存配置' }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加/编辑环境资源对话框 -->
    <el-dialog 
      v-model="environmentDialogVisible" 
      :title="isEditEnvironment ? '编辑环境资源' : '添加环境资源'" 
      width="60%"
      :close-on-click-modal="false"
    >
      <div class="environment-type-selection" v-if="!isEditEnvironment">
        <h3>环境资源类型</h3>
        <el-radio-group v-model="selectedEnvironmentType" class="environment-type-group">
          <el-radio-button label="Python">
            <el-icon><Document /></el-icon> Python (requirements.txt)
          </el-radio-button>
          <el-radio-button label="Java">
            <el-icon><Platform /></el-icon> Java (pom.xml)
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- Python环境配置 -->
      <div v-if="selectedEnvironmentType === 'Python' || (isEditEnvironment && environmentForm.type === 'Python')">
        <h3>Python 环境配置</h3>
        <el-form :model="environmentForm" label-width="140px">
          <el-form-item label="环境资源名称" required>
            <el-input v-model="environmentForm.name" placeholder="请输入环境资源名称"></el-input>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="environmentForm.description" type="textarea" placeholder="请输入描述信息"></el-input>
          </el-form-item>
          <el-form-item label="Python版本">
            <el-select v-model="environmentForm.python_version" placeholder="选择Python版本">
              <el-option label="Python 3.8" value="3.8"></el-option>
              <el-option label="Python 3.9" value="3.9"></el-option>
              <el-option label="Python 3.10" value="3.10"></el-option>
              <el-option label="Python 3.11" value="3.11"></el-option>
              <el-option label="Python 3.12" value="3.12"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="虚拟环境名称">
            <el-input v-model="environmentForm.virtual_env_name" placeholder="例如: myproject_env"></el-input>
          </el-form-item>
          <el-form-item label="是否启用">
            <el-switch v-model="environmentForm.is_active"></el-switch>
          </el-form-item>
        </el-form>

        <!-- requirements.txt 内容编辑 -->
        <div class="file-content-section">
          <div class="file-header">
            <h4>requirements.txt 文件内容</h4>
            <el-button type="primary" size="small" @click="generateDefaultPythonContent">生成默认内容</el-button>
          </div>
          <el-input
            v-model="environmentForm.file_content"
            type="textarea"
            :rows="10"
            placeholder="请输入 requirements.txt 文件内容，例如：&#10;requests==2.28.1&#10;numpy==1.24.3&#10;pandas==2.0.3"
          ></el-input>
        </div>
      </div>

      <!-- Java环境配置 -->
      <div v-if="selectedEnvironmentType === 'Java' || (isEditEnvironment && environmentForm.type === 'Java')">
        <h3>Java 环境配置</h3>
        <el-form :model="environmentForm" label-width="140px">
          <el-form-item label="环境资源名称" required>
            <el-input v-model="environmentForm.name" placeholder="请输入环境资源名称"></el-input>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="environmentForm.description" type="textarea" placeholder="请输入描述信息"></el-input>
          </el-form-item>
          <el-form-item label="Java版本">
            <el-select v-model="environmentForm.java_version" placeholder="选择Java版本">
              <el-option label="Java 8" value="8"></el-option>
              <el-option label="Java 11" value="11"></el-option>
              <el-option label="Java 17" value="17"></el-option>
              <el-option label="Java 21" value="21"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Maven版本">
            <el-select v-model="environmentForm.maven_version" placeholder="选择Maven版本">
              <el-option label="Maven 3.6.3" value="3.6.3"></el-option>
              <el-option label="Maven 3.8.6" value="3.8.6"></el-option>
              <el-option label="Maven 3.9.4" value="3.9.4"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Group ID">
            <el-input v-model="environmentForm.group_id" placeholder="例如: com.example"></el-input>
          </el-form-item>
          <el-form-item label="Artifact ID">
            <el-input v-model="environmentForm.artifact_id" placeholder="例如: demo"></el-input>
          </el-form-item>
          <el-form-item label="项目版本">
            <el-input v-model="environmentForm.version" placeholder="例如: 1.0.0"></el-input>
          </el-form-item>
          <el-form-item label="是否启用">
            <el-switch v-model="environmentForm.is_active"></el-switch>
          </el-form-item>
        </el-form>

        <!-- pom.xml 内容编辑 -->
        <div class="file-content-section">
          <div class="file-header">
            <h4>pom.xml 文件内容</h4>
            <el-button type="primary" size="small" @click="generateDefaultJavaContent">生成默认内容</el-button>
          </div>
          <el-input
            v-model="environmentForm.file_content"
            type="textarea"
            :rows="15"
            placeholder="请输入 pom.xml 文件内容"
          ></el-input>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="environmentDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteEnvironmentResource" v-if="isEditEnvironment">删除环境资源</el-button>
          <el-button type="primary" @click="submitEnvironmentResource">{{ isEditEnvironment ? '保存配置' : '保存配置' }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteConfirmVisible" title="确认删除" width="30%">
      <p>确定要删除数据源 "{{ currentDataSource?.name }}" 吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteConfirmVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteDataSource">确认删除</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除环境资源确认对话框 -->
    <el-dialog v-model="deleteEnvironmentConfirmVisible" title="确认删除" width="30%">
      <p>确定要删除环境资源 "{{ currentEnvironmentResource?.name }}" 吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteEnvironmentConfirmVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteEnvironmentResource">确认删除</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- sqlserver连接测试结果提示 -->
    <el-dialog v-model="sqlserverTestResultVisible" :title="sqlserverTestResult.success ? '连接成功' : '连接失败'" width="30%">
      <p>{{ sqlserverTestResult.message }}</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="sqlserverTestResultVisible = false">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { Plus, Document, Platform, Setting } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import request from '../utils/axios'

const router = useRouter()
const store = useStore()

// 在组件创建时获取数据源列表
onMounted(async () => {
  await fetchDataSources()
  await fetchEnvironmentResources()
})

// 标签页控制
const activeTab = ref('datasource')

// 表单数据
const filterForm = ref({
  keyword: '',
  type: ''
})

// 环境资源过滤表单
const environmentFilterForm = ref({
  keyword: '',
  type: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 环境资源分页
const environmentCurrentPage = ref(1)
const environmentPageSize = ref(10)

// 对话框控制
const dataSourceDialogVisible = ref(false)
const environmentDialogVisible = ref(false)
const deleteConfirmVisible = ref(false)
const deleteEnvironmentConfirmVisible = ref(false)
const sqlserverTestResultVisible = ref(false)
const isEdit = ref(false)
const isEditEnvironment = ref(false)
const selectedType = ref('Excel')
const selectedEnvironmentType = ref('Python')

// sqlserver连接测试结果
const sqlserverTestResult = ref({
  success: false,
  message: ''
})
const sqlServerConnectionStatus = ref('') // 'success', 'error', 'loading', ''

// 数据源表单
const dataSourceForm = reactive({
  id: null,
  name: '',
  type: 'Excel',
  path: '',
  // Excel
  sheet: '',
// SQL Server
  server: 'localhost',
  port: '1433',
  database: '',
  authType: 'sqlserver',
  username: '',
  password: '',
  timeout: 30,
  encrypt: false,
  trustServerCertificate: true,
  table: '',
  // XML
  rootPath: '',
  // JSON
  dataPath: '',
  // CSV
  delimiter: ',',
  hasHeader: true
})

// 环境资源表单
const environmentForm = reactive({
  id: null,
  name: '',
  type: 'Python',
  description: '',
  file_name: '',
  file_path: '',
  file_content: '',
  // Python 特有字段
  python_version: '3.11',
  virtual_env_name: '',
  // Java 特有字段
  java_version: '11',
  maven_version: '3.9.4',
  group_id: 'com.example',
  artifact_id: 'demo',
  version: '1.0.0',
  // 通用字段
  is_active: true
})

// 当前操作的数据源和环境资源
const currentDataSource = ref(null)
const currentEnvironmentResource = ref(null)

// 可用的工作表/表名
const availableSheets = ref(['Projects', 'Bugs', 'TestCases'])
const availableTables = ref([])

// 预览数据
const previewData = ref([
  { id: 1, name: 'Chart', language: 'Java', bugs: 26 },
  { id: 2, name: 'Math', language: 'Java', bugs: 106 },
  { id: 3, name: 'Time', language: 'Java', bugs: 27 }
])

// 预览列
const previewColumns = ref([
  { prop: 'id', label: 'ID' },
  { prop: 'name', label: '项目名称' },
  { prop: 'language', label: '语言' },
  { prop: 'bugs', label: '缺陷数' }
])

// 从store获取数据源和环境资源
const dataSources = computed(() => store.state.dataSources || [])
const environmentResources = computed(() => store.state.environmentResources || [])

// 是否显示工作表/表名列
const hasSheetOrTableColumn = computed(() => {
  return dataSources.value.some(ds => 
    ds.type === 'Excel' || 
    ds.type === 'SQLServer'
  )
})

// 过滤后的数据源
const filteredDataSources = computed(() => {
  return dataSources.value.filter(dataSource => {
    const matchesKeyword = dataSource.name.toLowerCase().includes(filterForm.value.keyword.toLowerCase())
    const matchesType = filterForm.value.type ? 
      dataSource.type === filterForm.value.type : true
    return matchesKeyword && matchesType
  })
})

// 过滤后的环境资源
const filteredEnvironmentResources = computed(() => {
  return environmentResources.value.filter(resource => {
    const matchesKeyword = resource.name.toLowerCase().includes(environmentFilterForm.value.keyword.toLowerCase())
    const matchesType = environmentFilterForm.value.type ? 
      resource.type === environmentFilterForm.value.type : true
    return matchesKeyword && matchesType
  })
})

// 分页后的数据源
const paginatedDataSources = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDataSources.value.slice(start, end)
})

// 分页后的环境资源
const paginatedEnvironmentResources = computed(() => {
  const start = (environmentCurrentPage.value - 1) * environmentPageSize.value
  const end = start + environmentPageSize.value
  return filteredEnvironmentResources.value.slice(start, end)
})

// 修改类型监听器
watch(() => selectedType.value, (newType) => {
  dataSourceForm.type = newType
  
  if (newType === 'Excel') {
    dataSourceForm.sheet = 'Projects'
  } else if (newType === 'SQLServer') {
    // 初始化SQL Server特有的字段
    dataSourceForm.server = 'localhost'
    dataSourceForm.port = '1433'
    dataSourceForm.database = ''
    dataSourceForm.authType = 'sqlserver'
    dataSourceForm.username = ''
    dataSourceForm.password = ''
    dataSourceForm.timeout = 30
    dataSourceForm.encrypt = false
    dataSourceForm.trustServerCertificate = true
    dataSourceForm.table = ''
  } else if (newType === 'CSV') {
    dataSourceForm.delimiter = ','
    dataSourceForm.hasHeader = true
  }
})

// 环境资源类型监听器
watch(() => selectedEnvironmentType.value, (newType) => {
  environmentForm.type = newType
  
  if (newType === 'Python') {
    environmentForm.file_name = 'requirements.txt'
    environmentForm.python_version = '3.11'
  } else if (newType === 'Java') {
    environmentForm.file_name = 'pom.xml'
    environmentForm.java_version = '11'
    environmentForm.maven_version = '3.9.4'
    environmentForm.group_id = 'com.example'
    environmentForm.artifact_id = 'demo'
    environmentForm.version = '1.0.0'
  }
})

// 监听store.state.dataSources的变化
watch(() => store.state.dataSources, (newSources) => {
  console.log('DataSources updated in store:', newSources.length)
  // 强制组件更新
  nextTick(() => {
    // 通过修改页码来触发重新渲染
    const currentPageValue = currentPage.value
    currentPage.value = 0
    nextTick(() => {
      currentPage.value = currentPageValue
    })
  })
}, { deep: true })

// 监听store.state.environmentResources的变化
watch(() => store.state.environmentResources, (newResources) => {
  console.log('EnvironmentResources updated in store:', newResources.length)
  nextTick(() => {
    const currentPageValue = environmentCurrentPage.value
    environmentCurrentPage.value = 0
    nextTick(() => {
      environmentCurrentPage.value = currentPageValue
    })
  })
}, { deep: true })

// 标签页切换处理
function handleTabChange(tab) {
  activeTab.value = tab
  if (tab === 'environment') {
    fetchEnvironmentResources()
  } else {
    fetchDataSources()
  }
}

// 修改获取SQL Server可用表的函数
async function fetchAvailableTables() {
  sqlServerConnectionStatus.value = 'loading'
  try {
    const response = await request.post('/data-resources/test_connection/', {
      type: 'SQLServer',
      server: dataSourceForm.server,
      port: dataSourceForm.port,
      database: dataSourceForm.database,
      authType: dataSourceForm.authType,
      username: dataSourceForm.username,
      password: dataSourceForm.password,
      timeout: dataSourceForm.timeout,
      encrypt: dataSourceForm.encrypt,
      trustServerCertificate: dataSourceForm.trustServerCertificate
    })
    
    if (response.data.success) {
      availableTables.value = response.data.tables
      sqlServerConnectionStatus.value = 'success'
    } else {
      sqlServerConnectionStatus.value = 'error'
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('获取表列表失败:', error)
    sqlServerConnectionStatus.value = 'error'
    ElMessage.error(error.message || '获取表列表失败')
  }
}

// 修改测试SQL Server连接函数
async function testConnection() {
  sqlServerConnectionStatus.value = 'loading'
  try {
    const response = await request.post('/data-resources/test_connection/', {
      type: 'SQLServer',
      server: dataSourceForm.server,
      port: dataSourceForm.port,
      database: dataSourceForm.database,
      authType: dataSourceForm.authType,
      username: dataSourceForm.username,
      password: dataSourceForm.password,
      timeout: dataSourceForm.timeout,
      encrypt: dataSourceForm.encrypt,
      trustServerCertificate: dataSourceForm.trustServerCertificate
    })
    
    sqlserverTestResult.value = {
      success: response.data.success,
      message: response.data.message
    }
    
    if (response.data.success) {
      sqlServerConnectionStatus.value = 'success'
      availableTables.value = response.data.tables
    } else {
      sqlServerConnectionStatus.value = 'error'
    }
    
    sqlserverTestResultVisible.value = true
  } catch (error) {
    sqlserverTestResult.value = {
      success: false,
      message: '连接失败: ' + (error.message || '无法连接到SQL Server数据库')
    }
    sqlServerConnectionStatus.value = 'error'
    sqlserverTestResultVisible.value = true
  }
}

// 修改类型标签样式函数
function getTypeTagType(type) {
  const typeMap = {
    'Excel': '',
    'SQLServer': 'info',
    'XML': 'success',
    'JSON': 'warning',
    'CSV': 'danger'
  }
  return typeMap[type] || 'info'
}

// 环境资源类型标签样式
function getEnvironmentTypeTagType(type) {
  const typeMap = {
    'Python': 'success',
    'Java': 'warning'
  }
  return typeMap[type] || 'info'
}

// 返回上一页
function goBack() {
  router.go(-1)
}

// 修改显示添加对话框函数
function showAddDialog() {
  isEdit.value = false
  selectedType.value = 'Excel'
  Object.assign(dataSourceForm, {
    id: null,
    name: '',
    type: 'Excel',
    path: '',
    sheet: 'Projects',
    server: 'localhost',
    port: '1433',
    database: '',
    authType: 'sqlserver',
    username: '',
    password: '',
    timeout: 30,
    encrypt: false,
    trustServerCertificate: true,
    table: '',
    rootPath: '',
    dataPath: '',
    delimiter: ',',
    hasHeader: true
  })
  dataSourceDialogVisible.value = true
}

// 显示添加环境资源对话框
function showAddEnvironmentDialog() {
  isEditEnvironment.value = false
  selectedEnvironmentType.value = 'Python'
  Object.assign(environmentForm, {
    id: null,
    name: '',
    type: 'Python',
    description: '',
    file_name: 'requirements.txt',
    file_path: '',
    file_content: '',
    python_version: '3.11',
    virtual_env_name: '',
    java_version: '11',
    maven_version: '3.9.4',
    group_id: 'com.example',
    artifact_id: 'demo',
    version: '1.0.0',
    is_active: true
  })
  environmentDialogVisible.value = true
}

// 修改编辑数据源函数
function editDataSource(dataSource) {
  isEdit.value = true
  currentDataSource.value = dataSource
  selectedType.value = dataSource.type
  Object.assign(dataSourceForm, {
    id: dataSource.id,
    name: dataSource.name,
    type: dataSource.type,
    path: dataSource.path,
    sheet: dataSource.sheet || 'Projects',
    server: dataSource.server || 'localhost',
    port: dataSource.port || '1433',
    database: dataSource.database || '',
    authType: dataSource.authType || 'sqlserver',
    username: dataSource.username || '',
    password: dataSource.password || '',
    timeout: dataSource.timeout || 30,
    encrypt: dataSource.encrypt || false,
    trustServerCertificate: dataSource.trustServerCertificate !== undefined ? dataSource.trustServerCertificate : true,
    table: dataSource.table || '',
    rootPath: dataSource.rootPath || '',
    dataPath: dataSource.dataPath || '',
    delimiter: dataSource.delimiter || ',',
    hasHeader: dataSource.hasHeader !== undefined ? dataSource.hasHeader : true
  })
  
  // 如果是SQL Server类型，获取可用的表
  if (dataSource.type === 'SQLServer' && 
      dataSource.server && 
      dataSource.database) {
    fetchAvailableTables()
  }
  
  dataSourceDialogVisible.value = true
}

// 编辑环境资源
function editEnvironmentResource(resource) {
  isEditEnvironment.value = true
  currentEnvironmentResource.value = resource
  selectedEnvironmentType.value = resource.type
  Object.assign(environmentForm, {
    id: resource.id,
    name: resource.name,
    type: resource.type,
    description: resource.description || '',
    file_name: resource.file_name || '',
    file_path: resource.file_path || '',
    file_content: resource.file_content || '',
    python_version: resource.python_version || '3.11',
    virtual_env_name: resource.virtual_env_name || '',
    java_version: resource.java_version || '11',
    maven_version: resource.maven_version || '3.9.4',
    group_id: resource.group_id || 'com.example',
    artifact_id: resource.artifact_id || 'demo',
    version: resource.version || '1.0.0',
    is_active: resource.is_active !== undefined ? resource.is_active : true
  })
  environmentDialogVisible.value = true
}

// 确认删除
function confirmDelete(dataSource) {
  currentDataSource.value = dataSource
  deleteConfirmVisible.value = true
}

// 确认删除环境资源
function confirmDeleteEnvironment(resource) {
  currentEnvironmentResource.value = resource
  deleteEnvironmentConfirmVisible.value = true
}

// 获取数据源列表
async function fetchDataSources() {
  try {
    const params = {}
    if (filterForm.value.keyword) {
      params.keyword = filterForm.value.keyword
    }
    if (filterForm.value.type) {
      params.type = filterForm.value.type
    }

    console.log('Fetching data sources with params:', params)
    const response = await request.get('/data-resources/filter/', { params })
    console.log('Received response data:', response.data)
    
    // Ensure store updates correctly
    store.commit('setDataSources', response.data)
    console.log('Updated store dataSources:', store.state.dataSources)
    
    // Force UI refresh
    currentPage.value = 1
    
    return response.data
  } catch (error) {
    console.error('获取数据源列表失败:', error)
    ElMessage.error('获取数据源列表失败')
    return []
  }
}

// 获取环境资源列表
async function fetchEnvironmentResources() {
  try {
    const params = {}
    if (environmentFilterForm.value.keyword) {
      params.keyword = environmentFilterForm.value.keyword
    }
    if (environmentFilterForm.value.type) {
      params.type = environmentFilterForm.value.type
    }

    console.log('Fetching environment resources with params:', params)
    const response = await request.get('/environment-resources/filter/', { params })
    console.log('Received environment response data:', response.data)
    
    // 确保store正确更新
    store.commit('setEnvironmentResources', response.data)
    console.log('Updated store environmentResources:', store.state.environmentResources)
    
    // 强制UI刷新
    environmentCurrentPage.value = 1
    
    return response.data
  } catch (error) {
    console.error('获取环境资源列表失败:', error)
    ElMessage.error('获取环境资源列表失败')
    return []
  }
}

// 删除数据源 - 改进版
async function deleteDataSource() {
  if (currentDataSource.value) {
    try {
      await request.delete(`/data-resources/${currentDataSource.value.id}/`)
      ElMessage.success('数据源删除成功')
      
      // 完全刷新数据
      const updatedData = await fetchDataSources()
      
      // 更新store
      store.commit('setDataSources', updatedData)
      
      deleteConfirmVisible.value = false
      dataSourceDialogVisible.value = false
    } catch (error) {
      console.error('删除数据源失败:', error)
      ElMessage.error('删除数据源失败: ' + (error.message || '未知错误'))
    }
  }
}

// 删除环境资源
async function deleteEnvironmentResource() {
  if (currentEnvironmentResource.value) {
    try {
      await request.delete(`/environment-resources/${currentEnvironmentResource.value.id}/`)
      ElMessage.success('环境资源删除成功')
      
      // 完全刷新数据
      const updatedData = await fetchEnvironmentResources()
      
      // 更新store
      store.commit('setEnvironmentResources', updatedData)
      
      deleteEnvironmentConfirmVisible.value = false
      environmentDialogVisible.value = false
    } catch (error) {
      console.error('删除环境资源失败:', error)
      ElMessage.error('删除环境资源失败: ' + (error.message || '未知错误'))
    }
  }
}

// 修改提交数据源表单函数中的验证部分
async function submitDataSource() {
  if (!dataSourceForm.name) {
    ElMessage.warning('请输入数据源名称')
    return
  }
  
  if (dataSourceForm.type === 'Excel' ||
      dataSourceForm.type === 'XML' ||
      dataSourceForm.type === 'JSON' ||
      dataSourceForm.type === 'CSV') {
    if (!dataSourceForm.path) {
      ElMessage.warning(`请选择${dataSourceForm.type}文件`)
      return
    }
  } else if (dataSourceForm.type === 'SQLServer') {
    if (!dataSourceForm.server || !dataSourceForm.database) {
      ElMessage.warning('请填写SQL Server连接信息')
      return
    }
    if (dataSourceForm.authType === 'sqlserver' && !dataSourceForm.username) {
      ElMessage.warning('使用SQL Server身份验证时，请填写用户名')
      return
    }
  }
  
  try {
    const formData = {
      name: dataSourceForm.name,
      type: dataSourceForm.type,
      path: dataSourceForm.path
    }
    
    // 根据类型添加特定字段
    if (dataSourceForm.type === 'Excel') {
      formData.sheet = dataSourceForm.sheet
    } else if (dataSourceForm.type === 'SQLServer') {
      formData.server = dataSourceForm.server
      formData.port = dataSourceForm.port
      formData.database = dataSourceForm.database
      formData.auth_type = dataSourceForm.authType
      formData.username = dataSourceForm.username
      formData.password = dataSourceForm.password
      formData.timeout = dataSourceForm.timeout
      formData.encrypt = dataSourceForm.encrypt
      formData.trust_server_certificate = dataSourceForm.trustServerCertificate
      formData.table = dataSourceForm.table
    } else if (dataSourceForm.type === 'XML') {
      formData.root_path = dataSourceForm.rootPath
    } else if (dataSourceForm.type === 'JSON') {
      formData.data_path = dataSourceForm.dataPath
    } else if (dataSourceForm.type === 'CSV') {
      formData.delimiter = dataSourceForm.delimiter
      formData.has_header = dataSourceForm.hasHeader
    }
    
    let response
    if (isEdit.value) {
      response = await request.put(`/data-resources/${dataSourceForm.id}/`, formData)
      ElMessage.success('数据源更新成功')
    } else {
      response = await request.post('/data-resources/', formData)
      ElMessage.success('数据源添加成功')
    }
    
    const updatedData = await fetchDataSources()
    store.commit('setDataSources', updatedData)
    dataSourceDialogVisible.value = false
  } catch (error) {
    console.error('保存数据源失败:', error)
    ElMessage.error('保存数据源失败: ' + (error.message || '未知错误'))
  }
}

// 提交环境资源表单
async function submitEnvironmentResource() {
  if (!environmentForm.name) {
    ElMessage.warning('请输入环境资源名称')
    return
  }
  
  if (!environmentForm.file_content) {
    ElMessage.warning('请输入文件内容')
    return
  }
  
  try {
    const formData = {
      name: environmentForm.name,
      type: environmentForm.type,
      description: environmentForm.description,
      file_name: environmentForm.file_name,
      file_path: environmentForm.file_path,
      file_content: environmentForm.file_content,
      is_active: environmentForm.is_active
    }
    
    // 根据类型添加特定字段
    if (environmentForm.type === 'Python') {
      formData.python_version = environmentForm.python_version
      formData.virtual_env_name = environmentForm.virtual_env_name
    } else if (environmentForm.type === 'Java') {
      formData.java_version = environmentForm.java_version
      formData.maven_version = environmentForm.maven_version
      formData.group_id = environmentForm.group_id
      formData.artifact_id = environmentForm.artifact_id
      formData.version = environmentForm.version
    }
    
    let response
    if (isEditEnvironment.value) {
      response = await request.put(`/environment-resources/${environmentForm.id}/`, formData)
      ElMessage.success('环境资源更新成功')
    } else {
      response = await request.post('/environment-resources/', formData)
      ElMessage.success('环境资源添加成功')
    }
    
    const updatedData = await fetchEnvironmentResources()
    store.commit('setEnvironmentResources', updatedData)
    environmentDialogVisible.value = false
  } catch (error) {
    console.error('保存环境资源失败:', error)
    ElMessage.error('保存环境资源失败: ' + (error.message || '未知错误'))
  }
}

// 搜索数据源
async function searchDataSources() {
  console.log('Search with:', filterForm.value)
  // 重置分页到第一页
  currentPage.value = 1
  // 获取数据源列表
  await fetchDataSources()
}

// 搜索环境资源
async function searchEnvironmentResources() {
  console.log('Search environment with:', environmentFilterForm.value)
  // 重置分页到第一页
  environmentCurrentPage.value = 1
  // 获取环境资源列表
  await fetchEnvironmentResources()
}

// 生成默认Python内容
function generateDefaultPythonContent() {
  const group_id = environmentForm.group_id || 'com.example'
  const artifact_id = environmentForm.artifact_id || 'demo'
  const version = environmentForm.version || '1.0.0'
  
  environmentForm.file_content = `# Python项目依赖文件
# 项目: ${environmentForm.name || 'Python Project'}
# Python版本: ${environmentForm.python_version || '3.11'}

# 基础依赖包
requests==2.31.0
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.1

# 开发工具
pytest==7.4.0
black==23.3.0
flake8==6.0.0

# 可选依赖
# scipy==1.11.1
# scikit-learn==1.3.0
# jupyter==1.0.0`
}

// 生成默认Java内容
function generateDefaultJavaContent() {
  const group_id = environmentForm.group_id || 'com.example'
  const artifact_id = environmentForm.artifact_id || 'demo'
  const version = environmentForm.version || '1.0.0'
  const java_version = environmentForm.java_version || '11'
  
  environmentForm.file_content = `<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>${group_id}</groupId>
    <artifactId>${artifact_id}</artifactId>
    <version>${version}</version>
    <packaging>jar</packaging>
    
    <name>${environmentForm.name || 'Java Project'}</name>
    <description>${environmentForm.description || 'Java project description'}</description>
    
    <properties>
        <maven.compiler.source>${java_version}</maven.compiler.source>
        <maven.compiler.target>${java_version}</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.9.3</junit.version>
    </properties>
    
    <dependencies>
        <!-- JUnit 5 测试框架 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>\${junit.version}</version>
            <scope>test</scope>
        </dependency>
        
        <!-- Apache Commons Lang -->
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.12.0</version>
        </dependency>
        
        <!-- Jackson JSON处理 -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.15.2</version>
        </dependency>
        
        <!-- 日志框架 -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>2.0.7</version>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <version>1.4.8</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>${java_version}</source>
                    <target>${java_version}</target>
                </configuration>
            </plugin>
            
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.1.2</version>
            </plugin>
        </plugins>
    </build>
</project>`
}

/// 上传文件
async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await request.post('/data-resources/upload_file/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      dataSourceForm.path = response.data.path
      ElMessage.success(`文件上传成功: ${file.name}`)
      return true
    } else {
      ElMessage.error(response.data.message || '文件上传失败')
      return false
    }
  } catch (error) {
    console.error('文件上传失败:', error)
    ElMessage.error('文件上传失败: ' + (error.message || '未知错误'))
    return false
  }
}

// 打开文件浏览器
function openFileBrowser(fileType) {
  const fileInput = document.createElement('input')
  fileInput.type = 'file'
  
  // 根据文件类型设置接受的文件扩展名
  switch(fileType) {
    case 'excel':
      fileInput.accept = '.xlsx,.xls,.xlsm'
      break
    case 'xml':
      fileInput.accept = '.xml'
      break
    case 'json':
      fileInput.accept = '.json'
      break
    case 'csv':
      fileInput.accept = '.csv'
      break
    default:
      fileInput.accept = '*'
  }
  
  // 文件选择事件处理
  fileInput.onchange = async (event) => {
    const file = event.target.files[0]
    if (file) {
      // 上传文件到后端
      const uploaded = await uploadFile(file)
      
      if (uploaded) {
        // 根据文件类型更新预览数据
        if (fileType === 'excel') {
          // 获取Excel文件的工作表列表
          const response = await request.post('/data-resources/preview_data/', {
            type: 'Excel',
            path: dataSourceForm.path
          })
          
          if (response.data.success) {
            availableSheets.value = response.data.sheets
            dataSourceForm.sheet = availableSheets.value[0]
            previewData.value = response.data.data
            previewColumns.value = response.data.columns
          }
        } else {
          await fetchPreviewData()
        }
      }
    }
  }
  
  // 触发文件选择对话框
  fileInput.click()
}

// 修改获取预览数据函数中SQL Server相关部分
async function fetchPreviewData() {
  const loading = ElLoading.service({
    lock: true,
    text: '加载预览数据...',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  
  try {
    const requestData = {
      type: dataSourceForm.type,
      path: dataSourceForm.path
    }
    
    if (dataSourceForm.type === 'Excel') {
      requestData.sheet = dataSourceForm.sheet
    } else if (dataSourceForm.type === 'SQLServer') {
      requestData.server = dataSourceForm.server
      requestData.port = dataSourceForm.port
      requestData.database = dataSourceForm.database
      requestData.authType = dataSourceForm.authType
      requestData.username = dataSourceForm.username
      requestData.password = dataSourceForm.password
      requestData.timeout = dataSourceForm.timeout
      requestData.encrypt = dataSourceForm.encrypt
      requestData.trustServerCertificate = dataSourceForm.trustServerCertificate
      requestData.table = dataSourceForm.table
    } else if (dataSourceForm.type === 'XML') {
      requestData.rootPath = dataSourceForm.rootPath
    } else if (dataSourceForm.type === 'JSON') {
      requestData.dataPath = dataSourceForm.dataPath
    } else if (dataSourceForm.type === 'CSV') {
      requestData.delimiter = dataSourceForm.delimiter
      requestData.hasHeader = dataSourceForm.hasHeader
    }
    
    const response = await request.post('/data-resources/preview_data/', requestData)
    
    if (response.data.success) {
      previewData.value = response.data.data
      previewColumns.value = response.data.columns
    } else {
      ElMessage.error(response.data.message || '获取预览数据失败')
    }
  } catch (error) {
    console.error('获取预览数据失败:', error)
    ElMessage.error('获取预览数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.close()
  }
}
</script>

<style scoped>
.data-resource-config {
  padding: 20px;
}

.tab-card {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.data-source-type-group,
.environment-type-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.preview-data {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.connect-btn {
  margin-top: 10px;
}

.dialog-footer {
  display: flex;
  gap: 10px;
}

.file-content-section {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.file-header h4 {
  margin: 0;
  color: #606266;
}
</style>