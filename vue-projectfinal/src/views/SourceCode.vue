<template>
  <div class="source-code-manager">
    <el-page-header title="返回" @back="goBack">
      <template #content>
        <h2>源代码管理</h2>
      </template>
      <template #extra>
        <el-button type="primary" @click="showUploadDialog">
          <el-icon><Upload /></el-icon> 上传源代码
        </el-button>
      </template>
    </el-page-header>

    <!-- 项目列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>源代码项目列表</span>
          <el-tag type="info">总计: {{ projects.length }}</el-tag>
        </div>
      </template>

      <el-table :data="filteredProjects" style="width: 100%">
        <el-table-column prop="name" label="项目名称"></el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件数量">
          <template #default="{ row }">
            {{ row.files ? row.files.length : 0 }}
          </template>
        </el-table-column>
        <el-table-column label="测试用例" width="300">
          <template #default="{ row }">
            <div>
              <div v-if="row.testCases && row.testCases.length > 0">
                <el-select
                  v-model="selectedTestCase[row.id]"
                  placeholder="选择测试用例"
                  @change="(value) => runAnalysis(row, value)"
                >
                  <el-option
                    v-for="testCase in row.testCases"
                    :key="testCase.id"
                    :label="testCase.file_name"
                    :value="testCase.id"
                  />
                </el-select>
              </div>
              <div v-else>
                <p>没有测试用例</p>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="runAnalysis(row)"
              :loading="row.status === 'running'"
              :disabled="true"
            >
              {{ row.status === "running" ? "运行中" : "运行" }}
            </el-button>
            <el-button
              size="small"
              type="success"
              @click="viewResult(row)"
              :disabled="
                !['completed', 'failed', 'timeout'].includes(row.status)
              "
            >
              结果
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteProject(row)"
              :disabled="row.status === 'running'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30]"
        layout="total, sizes, prev, pager, next"
        :total="projects.length"
      />
    </el-card>

    <!-- 简化的上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传源代码" width="50%">
      <el-upload
        class="upload-demo"
        drag
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        :before-upload="beforeUpload"
        accept=".zip"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖放ZIP文件到此处或<em>点击上传</em></div>
      </el-upload>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpload">上传</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 运行结果对话框 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="运行结果"
      width="70%"
      :close-on-click-modal="false"
    >
      <div v-if="currentResult" class="result-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="运行状态">
            <el-tag :type="getStatusType(currentResult.status)">
              {{ getStatusText(currentResult.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="返回码">
            {{ currentResult.return_code }}
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs class="result-tabs">
          <el-tab-pane label="输出">
            <pre class="output-content">
      <template v-if="currentResult.error">
{{ currentResult.error }}
      </template>
      <template v-if="currentResult.output.stdout">
{{ currentResult.output.stdout }}
      </template>
      <template v-else-if="currentResult.output.stdout === null && currentResult.compilation">
{{ currentResult.compilation.stdout }}
      </template>
    </pre>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resultDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { UploadFilled } from "@element-plus/icons-vue";
import { ElMessage, ElLoading, ElMessageBox } from "element-plus";
import request from "../utils/axios";

const router = useRouter();
const store = useStore();

// 简化的状态管理
const filterForm = ref({
  keyword: "",
  status: "",
});

const currentPage = ref(1);
const pageSize = ref(10);
const uploadDialogVisible = ref(false);
const fileList = ref([]);
const projects = ref([]);
const resultDialogVisible = ref(false);
const currentResult = ref(null);
const selectedTestCase = ref({}); // 用于存储每个项目选择的测试用例

// 添加轮询定时器
const pollingTimer = ref(null);
const analyzingProjects = ref(new Set());

// 过滤后的项目列表
const filteredProjects = computed(() => {
  return projects.value
    .filter((project) => {
      const matchesKeyword = project.name
        .toLowerCase()
        .includes(filterForm.value.keyword.toLowerCase());
      const matchesStatus = filterForm.value.status
        ? project.status === filterForm.value.status
        : true;
      return matchesKeyword && matchesStatus;
    })
    .slice(
      (currentPage.value - 1) * pageSize.value,
      currentPage.value * pageSize.value
    );
});

// 初始化加载数据
onMounted(() => {
  fetchProjects();
  startPolling();
});

onUnmounted(() => {
  stopPolling();
});

// 修改轮询逻辑
function startPolling() {
  pollingTimer.value = setInterval(() => {
    if (analyzingProjects.value.size > 0) {
      fetchProjects();
    }
  }, 2000); // 每2秒轮询一次
}

// 停止轮询
function stopPolling() {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value);
    pollingTimer.value = null;
  }
}

// 修改获取项目列表函数
async function fetchProjects() {
  try {
    const response = await request.get("/source-code/list/");
    projects.value = response.data.projects.map((project) => {
      return {
        ...project,
      };
    });

    analyzingProjects.value = new Set(
      projects.value
        .filter((p) => p.status === "analyzing" || p.status === "running")
        .map((p) => p.id)
    );

    if (analyzingProjects.value.size === 0) {
      stopPolling();
    }
  } catch (error) {
    ElMessage.error(
      "获取项目列表失败: " + (error.response?.data?.message || error.message)
    );
  }
}

// 核心功能函数
function goBack() {
  router.go(-1);
}

function showUploadDialog() {
  uploadDialogVisible.value = true;
}

function beforeUpload(file) {
  const isZip = file.type === "application/zip" || file.name.endsWith(".zip");
  if (!isZip) {
    ElMessage.error("只能上传ZIP格式的文件!");
  }
  return isZip;
}

function handleFileChange(file, files) {
  fileList.value = files.filter(
    (f) => f.type === "application/zip" || f.name.endsWith(".zip")
  );
}

function submitUpload() {
  if (fileList.value.length === 0) {
    ElMessage.error("请选择要上传的ZIP文件");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileList.value[0].raw);

  const loading = ElLoading.service({
    lock: true,
    text: "文件上传中...",
    background: "rgba(0, 0, 0, 0.7)",
  });

  request
    .post("source-code/upload-zip/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      ElMessage.success("上传成功");
      uploadDialogVisible.value = false;
      fileList.value = [];
      fetchProjects();
    })
    .catch((error) => {
      ElMessage.error(
        "上传失败: " + (error.response?.data?.message || error.message)
      );
    })
    .finally(() => {
      loading.close();
    });
}

function runAnalysis(project, testCaseId) {
  if (!testCaseId) {
    ElMessage.error("请先选择测试用例");
    return;
  }

  const loading = ElLoading.service({
    lock: true,
    text: "正在启动项目运行...",
    background: "rgba(0, 0, 0, 0.7)",
  });

  request
    .post(`/source-code/${project.id}/run/`, {
      testCaseId: testCaseId,
      projectId: project.id,
    })
    .then((response) => {
      ElMessage.success("项目运行已启动");
      analyzingProjects.value.add(project.id);
      if (!pollingTimer.value) {
        startPolling();
      }
      fetchProjects();
    })
    .catch((error) => {
      ElMessage.error(
        "启动运行失败: " + (error.response?.data?.message || error.message)
      );
    })
    .finally(() => {
      loading.close();
    });
}

// 修改查看结果函数
async function viewResult(project) {
  try {
    const response = await request.get(`/source-code/${project.id}/result/`);
    currentResult.value = {
      ...response.data,
      status: project.status, // 添加状态信息
    };
    resultDialogVisible.value = true;
  } catch (error) {
    ElMessage.error(
      "获取运行结果失败: " + (error.response?.data?.message || error.message)
    );
  }
}

function deleteProject(project) {
  ElMessageBox.confirm(
    `确定要删除项目 "${project.name}" 吗？此操作不可恢复。`,
    "警告",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(() => {
      request
        .post(`/source-code/delete/${project.id}/`)
        .then(() => {
          ElMessage.success("项目已删除");
          fetchProjects();
        })
        .catch((error) => {
          ElMessage.error(
            "删除失败: " + (error.response?.data?.message || error.message)
          );
        });
    })
    .catch(() => {
      // 用户取消删除操作
    });
}

function searchProjects() {
  currentPage.value = 1;
}

// 更新状态显示
function getStatusType(status) {
  switch (status) {
    case "analyzed":
      return "success";
    case "analyzing":
      return "warning";
    case "analysis_failed":
      return "danger";
    case "running":
      return "warning";
    case "completed":
      return "success";
    case "failed":
      return "danger";
    case "timeout":
      return "danger";
    default:
      return "info";
  }
}

function getStatusText(status) {
  switch (status) {
    case "analyzed":
      return "已分析";
    case "analyzing":
      return "分析中";
    case "analysis_failed":
      return "分析失败";
    case "running":
      return "运行中";
    case "completed":
      return "已完成";
    case "failed":
      return "运行失败";
    case "timeout":
      return "运行超时";
    default:
      return "未分析";
  }
}

function handleTestCaseChange(projectId) {}
</script>

<style scoped>
.source-code-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}

.result-content {
  max-height: 600px;
  overflow-y: auto;
}

.result-tabs {
  margin-top: 20px;
}

.output-content {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin: 0;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  max-height: 400px;
  overflow-y: auto;
}

.output-content.error {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
