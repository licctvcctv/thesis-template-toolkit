<template>
  <div class="doctor-followup-record">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>随访记录</span>
          <el-button type="primary" @click="handleAdd">填写随访记录</el-button>
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
          <el-form-item label="随访日期">
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
        <el-table-column prop="patientName" label="患者姓名" width="120" />
        <el-table-column prop="followupDate" label="随访日期" width="120" />
        <el-table-column prop="followupType" label="随访类型" width="120" />
        <el-table-column prop="symptoms" label="症状描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="bloodPressure" label="血压" width="100" />
        <el-table-column prop="bloodSugar" label="血糖" width="100" />
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column label="操作" fixed="right" width="300">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="success" size="small" @click="handleExport(scope.row)">导出报告</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" class="followup-record-dialog">
      <div class="dialog-body">
        <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="随访任务" prop="taskId" v-if="!formData.id">
          <el-select v-model="formData.taskId" placeholder="请选择随访任务" filterable style="width: 100%" @change="handleTaskChange">
            <el-option
              v-for="item in taskOptions"
              :key="item.id"
              :label="`${item.taskNo} - ${item.patientName} (${item.statusName})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者">
              <el-input v-model="formData.patientName" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="随访日期" prop="followupDate">
              <el-date-picker
                v-model="formData.followupDate"
                type="date"
                placeholder="请选择随访日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="随访类型" prop="followupType">
              <el-input v-model="formData.followupType" placeholder="请输入随访类型" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务编号">
              <el-input v-model="formData.taskNo" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="症状描述" prop="symptoms">
          <el-input v-model="formData.symptoms" type="textarea" :rows="3" placeholder="请输入症状描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="血压">
              <el-input v-model="formData.bloodPressure" placeholder="如：120/80" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="血糖">
              <el-input v-model="formData.bloodSugar" placeholder="如：5.5" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="体重(kg)">
              <el-input-number v-model="formData.weight" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="用药情况">
          <div class="medicine-list">
            <div v-for="(medicine, index) in formData.medicines" :key="index" class="medicine-item">
              <el-row :gutter="10" align="middle">
                <el-col :span="7">
                  <el-select v-model="medicine.medicineId" placeholder="选择药品" filterable style="width: 100%">
                    <el-option
                      v-for="item in medicineOptions"
                      :key="item.id"
                      :label="`${item.medicineName} (${item.medicineCode})`"
                      :value="item.id"
                    />
                  </el-select>
                </el-col>
                <el-col :span="5">
                  <el-input-number
                    v-model="medicine.quantity"
                    :min="1"
                    :step="1"
                    placeholder="数量"
                    style="width: 100%"
                    controls-position="right"
                  />
                </el-col>
                <el-col :span="9">
                  <el-input v-model="medicine.dosage" placeholder="用法用量" />
                </el-col>
                <el-col :span="3">
                  <el-button type="danger" size="small" @click="removeMedicine(index)">删除</el-button>
                </el-col>
              </el-row>
            </div>
            <div class="add-medicine-btn">
              <el-button type="primary" size="small" @click="addMedicine">添加药品</el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="用药依从性">
          <el-input v-model="formData.medicationCompliance" type="textarea" :rows="2" placeholder="请输入用药依从性" />
        </el-form-item>
        <el-form-item label="不良反应">
          <el-input v-model="formData.adverseReactions" type="textarea" :rows="2" placeholder="请输入不良反应" />
        </el-form-item>
        <el-form-item label="生活方式指导">
          <el-input v-model="formData.lifestyleGuidance" type="textarea" :rows="3" placeholder="请输入生活方式指导" />
        </el-form-item>
        <el-form-item label="随访结果" prop="followupResult">
          <el-input v-model="formData.followupResult" type="textarea" :rows="3" placeholder="请输入随访结果" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="下次随访日期">
              <el-date-picker
                v-model="formData.nextFollowupDate"
                type="date"
                placeholder="请选择下次随访日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="formData.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFollowupRecordPage, createFollowupRecord, updateFollowupRecord, deleteFollowupRecord, exportFollowupRecord, getFollowupRecordById } from '@/api/followupRecord'
import { getFollowupTaskPage, getFollowupTaskById } from '@/api/followupTask'
import { getDoctorByUserId } from '@/api/doctor'
import { getMedicineList } from '@/api/medicine'

const route = useRoute()
const tableData = ref([])
const taskOptions = ref([])
const medicineOptions = ref([])
const currentDoctorId = ref(null)

const searchForm = reactive({
  patientId: null,
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
const dialogTitle = ref('填写随访记录')
const formRef = ref(null)
const formData = reactive({
  id: null,
  taskId: null,
  patientId: null,
  patientName: '',
  followupDate: '',
  followupType: '',
  symptoms: '',
  bloodPressure: '',
  bloodSugar: '',
  weight: null,
  medicationCompliance: '',
  adverseReactions: '',
  lifestyleGuidance: '',
  nextFollowupDate: '',
  followupResult: '',
  remarks: '',
  taskNo: '',
  medicines: []
})

const rules = {
  taskId: [{ required: true, message: '请选择随访任务', trigger: 'change' }],
  followupDate: [{ required: true, message: '请选择随访日期', trigger: 'change' }],
  followupResult: [{ required: true, message: '请输入随访结果', trigger: 'blur' }]
}

onMounted(async () => {
  const doctorLoaded = await loadDoctorId()
  if (doctorLoaded) {
    await loadTaskOptions()
    loadData()
  }
  loadMedicineOptions()
  
  if (route.query.taskId) {
    try {
      const res = await getFollowupTaskById(route.query.taskId)
      if (res.data) {
        formData.taskId = res.data.id
        formData.patientId = res.data.patientId
        formData.patientName = res.data.patientName
        formData.taskNo = res.data.taskNo
        handleAdd()
      }
    } catch (error) {
      ElMessage.error('加载任务信息失败')
    }
  }
})

const loadDoctorId = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      console.error('用户ID不存在')
      ElMessage.error('用户信息未找到，请重新登录')
      return false
    }
    console.log('获取医生信息，userId:', userId)
    const res = await getDoctorByUserId(userId)
    console.log('医生信息返回:', res)
    if (res.data && res.data.id) {
      currentDoctorId.value = res.data.id
      formData.doctorId = res.data.id
      console.log('医生ID已加载:', currentDoctorId.value)
      return true
    } else {
      console.error('医生信息数据格式错误:', res.data)
      ElMessage.error('医生信息获取失败')
      return false
    }
  } catch (error) {
    console.error('获取医生信息失败:', error)
    ElMessage.error('获取医生信息失败: ' + (error.message || '未知错误'))
    return false
  }
}

const loadData = async () => {
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      doctorId: currentDoctorId.value,
      patientId: searchForm.patientId,
      taskId: null,
      startDate: searchForm.startDate,
      endDate: searchForm.endDate
    }
    const res = await getFollowupRecordPage(params)
    tableData.value = res.data.records || []
    pagination.total = res.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const loadTaskOptions = async () => {
  try {
    if (!currentDoctorId.value) {
      console.warn('医生ID未加载，无法加载任务列表')
      ElMessage.warning('医生信息未加载，请刷新页面重试')
      return
    }
    console.log('开始加载任务列表，医生ID:', currentDoctorId.value)
    const res = await getFollowupTaskPage({
      doctorId: currentDoctorId.value,
      page: 1,
      size: 1000
    })
    console.log('任务列表API返回:', res)
    // 只显示待办和进行中的任务
    taskOptions.value = (res.data.records || []).filter(task => 
      task.status === 'pending' || task.status === 'in_progress'
    )
    console.log('过滤后的任务列表:', taskOptions.value)
    if (taskOptions.value.length === 0) {
      console.warn('没有可用的随访任务')
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败: ' + (error.message || '未知错误'))
  }
}

const loadMedicineOptions = async () => {
  try {
    const res = await getMedicineList({ current: 1, size: 1000 })
    medicineOptions.value = res.data.records || []
  } catch (error) {
    ElMessage.error('加载药品列表失败')
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
  searchForm.startDate = null
  searchForm.endDate = null
  dateRange.value = null
  pagination.page = 1
  loadData()
}

const handleTaskChange = async (taskId) => {
  if (!taskId) {
    formData.patientId = null
    formData.patientName = ''
    formData.taskNo = ''
    return
  }
  try {
    const res = await getFollowupTaskById(taskId)
    if (res.data) {
      formData.patientId = res.data.patientId
      formData.patientName = res.data.patientName
      formData.taskNo = res.data.taskNo
    }
  } catch (error) {
    ElMessage.error('加载任务信息失败')
  }
}

const addMedicine = () => {
  formData.medicines.push({
    medicineId: null,
    quantity: 1,
    dosage: ''
  })
}

const removeMedicine = (index) => {
  formData.medicines.splice(index, 1)
}

const handleAdd = async () => {
  dialogTitle.value = '填写随访记录'
  // 重新加载任务列表，确保数据是最新的
  await loadTaskOptions()
  Object.assign(formData, {
    id: null,
    taskId: formData.taskId || null,
    patientId: formData.patientId || null,
    patientName: formData.patientName || '',
    doctorId: currentDoctorId.value,
    followupDate: new Date().toISOString().split('T')[0],
    followupType: '',
    symptoms: '',
    bloodPressure: '',
    bloodSugar: '',
    weight: null,
    medicationCompliance: '',
    adverseReactions: '',
    lifestyleGuidance: '',
    nextFollowupDate: '',
    followupResult: '',
    remarks: '',
    taskNo: formData.taskNo || '',
    medicines: []
  })
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  try {
    const res = await getFollowupRecordById(row.id)
    dialogTitle.value = '编辑随访记录'
    Object.assign(formData, {
      id: res.data.id,
      taskId: res.data.taskId,
      patientId: res.data.patientId,
      patientName: res.data.patientName,
      doctorId: currentDoctorId.value,
      followupDate: res.data.followupDate,
      followupType: res.data.followupType,
      symptoms: res.data.symptoms,
      bloodPressure: res.data.bloodPressure,
      bloodSugar: res.data.bloodSugar,
      weight: res.data.weight,
      medicationCompliance: res.data.medicationCompliance,
      adverseReactions: res.data.adverseReactions,
      lifestyleGuidance: res.data.lifestyleGuidance,
      nextFollowupDate: res.data.nextFollowupDate,
      followupResult: res.data.followupResult,
      remarks: res.data.remarks,
      taskNo: res.data.taskNo || '',
      medicines: (res.data.medicines || []).map(m => ({
        medicineId: m.medicineId,
        quantity: m.quantity,
        dosage: m.dosage
      }))
    })
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载记录详情失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (formData.id) {
          await updateFollowupRecord(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await createFollowupRecord(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗？', '提示', {
      type: 'warning'
    })
    await deleteFollowupRecord(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleExport = async (row) => {
  try {
    const res = await exportFollowupRecord(row.id)
    const html = res.data
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `随访记录_${row.patientName}_${row.followupDate}.html`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleSizeChange = () => {
  loadData()
}

const handleCurrentChange = () => {
  loadData()
}
</script>

<style scoped>
.doctor-followup-record {
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

.medicine-list {
  width: 100%;
}

.medicine-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.add-medicine-btn {
  margin-top: 10px;
  text-align: right;
}

/* 弹窗样式 */
.followup-record-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.dialog-body {
  max-height: calc(70vh - 120px);
  overflow-y: auto;
  padding-right: 10px;
}

/* 自定义滚动条样式 */
.dialog-body::-webkit-scrollbar {
  width: 6px;
}

.dialog-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.dialog-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.dialog-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
