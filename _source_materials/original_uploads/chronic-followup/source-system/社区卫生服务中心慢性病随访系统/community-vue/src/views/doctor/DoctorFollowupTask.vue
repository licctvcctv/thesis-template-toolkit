<template>
  <div class="doctor-followup-task">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>随访任务查看</span>
        </div>
      </template>

      <div class="search-bar">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="患者">
            <el-select v-model="searchForm.patientId" placeholder="请选择患者" clearable filterable style="width: 200px">
              <el-option
                v-for="item in patientOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 150px">
              <el-option label="待办" value="pending" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="计划日期">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待办任务" name="pending">
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="taskNo" label="任务编号" width="150" />
            <el-table-column prop="patientName" label="患者姓名" width="120" />
            <el-table-column prop="taskType" label="任务类型" width="120" />
            <el-table-column prop="taskContent" label="任务内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="planDate" label="计划日期" width="120" />
            <el-table-column prop="priorityName" label="优先级" width="100">
              <template #default="scope">
                <el-tag :type="getPriorityTagType(scope.row.priority)" size="small">
                  {{ scope.row.priorityName }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="200">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">查看详情</el-button>
                <el-button type="success" size="small" @click="handleStartTask(scope.row)">开始任务</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="全部任务" name="all">
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="taskNo" label="任务编号" width="150" />
            <el-table-column prop="patientName" label="患者姓名" width="120" />
            <el-table-column prop="taskType" label="任务类型" width="120" />
            <el-table-column prop="taskContent" label="任务内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="planDate" label="计划日期" width="120" />
            <el-table-column prop="actualDate" label="实际日期" width="120" />
            <el-table-column prop="statusName" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)">
                  {{ scope.row.statusName }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priorityName" label="优先级" width="100">
              <template #default="scope">
                <el-tag :type="getPriorityTagType(scope.row.priority)" size="small">
                  {{ scope.row.priorityName }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailDialogVisible" title="任务详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务编号">{{ currentTask?.taskNo }}</el-descriptions-item>
        <el-descriptions-item label="患者姓名">{{ currentTask?.patientName }}</el-descriptions-item>
        <el-descriptions-item label="任务类型">{{ currentTask?.taskType }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityTagType(currentTask?.priority)" size="small">
            {{ currentTask?.priorityName }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="计划日期">{{ currentTask?.planDate }}</el-descriptions-item>
        <el-descriptions-item label="实际日期">{{ currentTask?.actualDate || '未完成' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(currentTask?.status)">
            {{ currentTask?.statusName }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建人">{{ currentTask?.creatorName }}</el-descriptions-item>
        <el-descriptions-item label="任务内容" :span="2">
          <div style="white-space: pre-wrap;">{{ currentTask?.taskContent }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentTask?.remarks || '无' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button v-if="currentTask?.status === 'pending'" type="primary" @click="handleStartTask(currentTask)">开始任务</el-button>
        <el-button v-if="currentTask?.status === 'in_progress'" type="success" @click="handleCreateRecord">填写随访记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFollowupTaskPage, updateFollowupTaskStatus, getFollowupTaskById } from '@/api/followupTask'
import { getPatientList } from '@/api/patient'
import { getDoctorByUserId } from '@/api/doctor'

const router = useRouter()
const tableData = ref([])
const patientOptions = ref([])
const currentDoctorId = ref(null)

const activeTab = ref('pending')

const searchForm = reactive({
  patientId: null,
  status: '',
  startDate: null,
  endDate: null
})

const dateRange = ref(null)

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const detailDialogVisible = ref(false)
const currentTask = ref(null)

const computedStatus = computed(() => {
  return activeTab.value === 'pending' ? 'pending' : ''
})

onMounted(async () => {
  await loadDoctorId()
  loadData()
  loadPatientOptions()
})

const loadDoctorId = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (userId) {
      const res = await getDoctorByUserId(userId)
      if (res.data) {
        currentDoctorId.value = res.data.id
      }
    }
  } catch (error) {
    ElMessage.error('获取医生信息失败')
  }
}

const loadData = async () => {
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      doctorId: currentDoctorId.value,
      patientId: searchForm.patientId,
      status: activeTab.value === 'pending' ? 'pending' : searchForm.status,
      startDate: searchForm.startDate,
      endDate: searchForm.endDate
    }
    const res = await getFollowupTaskPage(params)
    tableData.value = res.data.records || []
    pagination.total = res.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const loadPatientOptions = async () => {
  try {
    const res = await getPatientList({ current: 1, size: 1000 })
    patientOptions.value = res.data.records || []
  } catch (error) {
    ElMessage.error('加载患者列表失败')
  }
}

const handleTabChange = () => {
  pagination.page = 1
  loadData()
}

const handleSearch = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    searchForm.startDate = dateRange.value[0]
    searchForm.endDate = dateRange.value[1]
  } else {
    searchForm.startDate = null
    searchForm.endDate = null
  }
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.patientId = null
  searchForm.status = ''
  searchForm.startDate = null
  searchForm.endDate = null
  dateRange.value = null
  pagination.page = 1
  loadData()
}

const handleViewDetail = async (row) => {
  try {
    const res = await getFollowupTaskById(row.id)
    currentTask.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载任务详情失败')
  }
}

const handleStartTask = async (task) => {
  try {
    await updateFollowupTaskStatus(task.id, 'in_progress')
    ElMessage.success('任务已开始')
    detailDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleCreateRecord = () => {
  router.push({
    path: '/doctor-followup-record',
    query: { taskId: currentTask.value.id, patientId: currentTask.value.patientId, taskNo: currentTask.value.taskNo }
  })
}

const handleSizeChange = () => {
  loadData()
}

const handleCurrentChange = () => {
  loadData()
}

const getStatusTagType = (status) => {
  const map = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || ''
}

const getPriorityTagType = (priority) => {
  const map = {
    low: 'info',
    normal: '',
    high: 'danger'
  }
  return map[priority] || ''
}
</script>

<style scoped>
.doctor-followup-task {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
