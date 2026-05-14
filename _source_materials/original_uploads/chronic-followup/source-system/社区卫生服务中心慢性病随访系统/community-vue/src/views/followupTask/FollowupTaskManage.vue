<template>
  <div class="followup-task-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>随访任务分配</span>
          <el-button type="primary" @click="handleAdd">创建任务</el-button>
        </div>
      </template>

      <div class="statistics-bar">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总任务数" :value="statistics.totalTasks" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="待办任务" :value="statistics.pendingTasks">
              <template #suffix>
                <el-tag type="warning" size="small">待处理</el-tag>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="进行中" :value="statistics.inProgressTasks">
              <template #suffix>
                <el-tag type="info" size="small">进行中</el-tag>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="已完成" :value="statistics.completedTasks">
              <template #suffix>
                <el-tag type="success" size="small">已完成</el-tag>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
        <div style="margin-top: 10px;">
          <el-text>完成率：{{ statistics.completionRate?.toFixed(2) }}%</el-text>
        </div>
      </div>

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
          <el-form-item label="医生">
            <el-select v-model="searchForm.doctorId" placeholder="请选择医生" clearable filterable style="width: 200px">
              <el-option
                v-for="item in doctorOptions"
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
              <el-option label="已取消" value="cancelled" />
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

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="taskNo" label="任务编号" width="150" />
        <el-table-column prop="patientName" label="患者姓名" width="120" />
        <el-table-column prop="doctorName" label="负责医生" width="120" />
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
        <el-table-column label="操作" fixed="right" width="300">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="warning" size="small" @click="handleUpdateStatus(scope.row)">状态管理</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="患者" prop="patientId">
          <el-select v-model="formData.patientId" placeholder="请选择患者" filterable style="width: 100%">
            <el-option
              v-for="item in patientOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责医生" prop="doctorId">
          <el-select v-model="formData.doctorId" placeholder="请选择医生" filterable style="width: 100%">
            <el-option
              v-for="item in doctorOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务类型" prop="taskType">
          <el-input v-model="formData.taskType" placeholder="请输入任务类型" />
        </el-form-item>
        <el-form-item label="任务内容" prop="taskContent">
          <el-input v-model="formData.taskContent" type="textarea" :rows="4" placeholder="请输入任务内容" />
        </el-form-item>
        <el-form-item label="计划日期" prop="planDate">
          <el-date-picker
            v-model="formData.planDate"
            type="date"
            placeholder="请选择计划日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="正常" value="normal" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="statusDialogVisible" title="状态管理" width="400px">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusTagType(currentTask?.status)">
            {{ currentTask?.statusName }}
          </el-tag>
        </el-form-item>
        <el-form-item label="更新状态" prop="status">
          <el-select v-model="statusForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="待办" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStatusSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFollowupTaskPage, createFollowupTask, updateFollowupTask, deleteFollowupTask, updateFollowupTaskStatus, getFollowupTaskStatistics } from '@/api/followupTask'
import { getPatientList } from '@/api/patient'
import { getDoctorList } from '@/api/doctor'

const tableData = ref([])
const patientOptions = ref([])
const doctorOptions = ref([])
const statistics = ref({
  totalTasks: 0,
  pendingTasks: 0,
  inProgressTasks: 0,
  completedTasks: 0,
  completionRate: 0
})

const searchForm = reactive({
  patientId: null,
  doctorId: null,
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

const dialogVisible = ref(false)
const dialogTitle = ref('创建任务')
const formRef = ref(null)
const formData = reactive({
  id: null,
  patientId: null,
  doctorId: null,
  taskType: '',
  taskContent: '',
  planDate: '',
  priority: 'normal',
  remarks: ''
})

const statusDialogVisible = ref(false)
const currentTask = ref(null)
const statusForm = reactive({
  status: ''
})

const rules = {
  patientId: [{ required: true, message: '请选择患者', trigger: 'change' }],
  doctorId: [{ required: true, message: '请选择医生', trigger: 'change' }],
  taskContent: [{ required: true, message: '请输入任务内容', trigger: 'blur' }],
  planDate: [{ required: true, message: '请选择计划日期', trigger: 'change' }]
}

onMounted(() => {
  loadData()
  loadStatistics()
  loadPatientOptions()
  loadDoctorOptions()
})

const loadData = async () => {
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      patientId: searchForm.patientId,
      doctorId: searchForm.doctorId,
      status: searchForm.status,
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

const loadStatistics = async () => {
  try {
    const res = await getFollowupTaskStatistics()
    statistics.value = res.data
  } catch (error) {
    ElMessage.error('加载统计信息失败')
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

const loadDoctorOptions = async () => {
  try {
    const res = await getDoctorList({ current: 1, size: 1000 })
    doctorOptions.value = res.data.records.map(item => ({
      id: item.id,
      name: item.name
    })) || []
  } catch (error) {
    ElMessage.error('加载医生列表失败')
  }
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
  searchForm.doctorId = null
  searchForm.status = ''
  searchForm.startDate = null
  searchForm.endDate = null
  dateRange.value = null
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  dialogTitle.value = '创建任务'
  Object.assign(formData, {
    id: null,
    patientId: null,
    doctorId: null,
    taskType: '',
    taskContent: '',
    planDate: '',
    priority: 'normal',
    remarks: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑任务'
  Object.assign(formData, {
    id: row.id,
    patientId: row.patientId,
    doctorId: row.doctorId,
    taskType: row.taskType,
    taskContent: row.taskContent,
    planDate: row.planDate,
    priority: row.priority,
    remarks: row.remarks
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (formData.id) {
          await updateFollowupTask(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await createFollowupTask(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
        loadStatistics()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleUpdateStatus = (row) => {
  currentTask.value = row
  statusForm.status = row.status
  statusDialogVisible.value = true
}

const handleStatusSubmit = async () => {
  try {
    await updateFollowupTaskStatus(currentTask.value.id, statusForm.status)
    ElMessage.success('状态更新成功')
    statusDialogVisible.value = false
    loadData()
    loadStatistics()
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
      type: 'warning'
    })
    await deleteFollowupTask(row.id)
    ElMessage.success('删除成功')
    loadData()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
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
.followup-task-manage {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics-bar {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
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
