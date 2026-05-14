<template>
  <div class="doctor-patient-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>患者管理</span>
        </div>
      </template>

      <div class="search-bar">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="姓名">
            <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
          </el-form-item>
          <el-form-item label="患者编号">
            <el-input v-model="searchForm.patientNo" placeholder="请输入患者编号" clearable />
          </el-form-item>
          <el-form-item label="疾病类型">
            <el-input v-model="searchForm.diseaseType" placeholder="请输入疾病类型" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="patientNo" label="患者编号" width="150" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="scope">
            {{ scope.row.gender === 1 ? '男' : scope.row.gender === 2 ? '女' : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="birthday" label="出生日期" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="diseaseType" label="疾病类型" width="120" />
        <el-table-column prop="riskLevelName" label="风险等级" width="100">
          <template #default="scope">
            <el-tag :type="getRiskLevelTagType(scope.row.riskLevel)">
              {{ scope.row.riskLevelName }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">详细信息</el-button>
            <el-button type="info" size="small" @click="handleViewHistory(scope.row)">历史记录</el-button>
            <el-button type="success" size="small" @click="handleViewRecords(scope.row)">诊疗记录</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 患者详细信息对话框 -->
      <el-dialog
        v-model="detailDialogVisible"
        title="患者详细信息"
        width="700px"
      >
        <el-descriptions :column="2" border v-if="currentPatient">
          <el-descriptions-item label="患者编号">{{ currentPatient.patientNo }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ currentPatient.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">
            {{ currentPatient.gender === 1 ? '男' : currentPatient.gender === 2 ? '女' : '' }}
          </el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ currentPatient.birthday }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ currentPatient.idCard || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentPatient.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">{{ currentPatient.address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="疾病类型">{{ currentPatient.diseaseType || '-' }}</el-descriptions-item>
          <el-descriptions-item label="确诊日期">{{ currentPatient.diagnosisDate || '-' }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskLevelTagType(currentPatient.riskLevel)">
              {{ currentPatient.riskLevelName }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负责医生">{{ currentPatient.doctorName || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>

      <!-- 历史记录对话框 -->
      <el-dialog
        v-model="historyDialogVisible"
        title="患者历史记录"
        width="900px"
      >
        <el-tabs v-model="historyActiveTab">
          <el-tab-pane label="风险评估记录" name="risk">
            <el-table :data="riskHistoryData" border style="width: 100%">
              <el-table-column prop="assessmentDate" label="评估日期" width="120" />
              <el-table-column prop="riskLevelName" label="风险等级" width="120">
                <template #default="scope">
                  <el-tag :type="getRiskLevelTagType(scope.row.riskLevel)">
                    {{ scope.row.riskLevelName }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assessorName" label="评估人" width="120" />
              <el-table-column prop="assessmentResult" label="评估结果" />
              <el-table-column prop="remarks" label="备注" width="150" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="医生分配记录" name="assignment">
            <el-table :data="assignmentHistoryData" border style="width: 100%">
              <el-table-column prop="assignDate" label="分配日期" width="120" />
              <el-table-column prop="doctorName" label="医生姓名" width="120" />
              <el-table-column prop="assignerName" label="分配人" width="120" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
                    {{ scope.row.status === 1 ? '当前分配' : '历史分配' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="remarks" label="备注" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-dialog>

      <!-- 诊疗记录对话框 -->
      <el-dialog
        v-model="recordsDialogVisible"
        title="患者诊疗记录"
        width="1000px"
      >
        <el-table :data="medicalRecordsData" border style="width: 100%">
          <el-table-column prop="recordDate" label="诊疗日期" width="120" />
          <el-table-column prop="doctorName" label="医生" width="120" />
          <el-table-column prop="chiefComplaint" label="主诉" width="200" show-overflow-tooltip />
          <el-table-column prop="diagnosis" label="诊断" width="200" show-overflow-tooltip />
          <el-table-column label="用药情况" width="200">
            <template #default="scope">
              <div v-if="scope.row.medicines && scope.row.medicines.length > 0">
                <el-tag v-for="(med, index) in scope.row.medicines" :key="index" size="small" style="margin-right: 5px">
                  {{ med.medicineName }} × {{ med.quantity }}
                </el-tag>
              </div>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="remarks" label="备注" />
        </el-table>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPatientList, getPatientById } from '@/api/patient'
import { getRiskAssessmentList, getRiskLevelConfigs } from '@/api/riskAssessment'
import { getDoctorAssignmentList } from '@/api/doctorAssignment'
import { getMedicalRecordList } from '@/api/medicalRecord'
import { getDoctorByUserId } from '@/api/doctor'

const tableData = ref([])
const detailDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const recordsDialogVisible = ref(false)
const historyActiveTab = ref('risk')
const currentPatient = ref(null)
const riskHistoryData = ref([])
const assignmentHistoryData = ref([])
const medicalRecordsData = ref([])
const riskLevelOptions = ref([])
const currentDoctorId = ref(null)

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const searchForm = reactive({
  name: '',
  patientNo: '',
  diseaseType: ''
})

const getRiskLevelTagType = (level) => {
  const map = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger'
  }
  return map[level] || ''
}

const loadRiskLevelOptions = async () => {
  try {
    const res = await getRiskLevelConfigs()
    riskLevelOptions.value = res.data
  } catch (error) {
    console.error('加载风险等级配置失败', error)
  }
}

const loadDoctorId = async () => {
  try {
    const userId = localStorage.getItem('token')
    if (!userId) {
      ElMessage.error('未登录')
      return null
    }
    
    const res = await getDoctorByUserId(parseInt(userId))
    if (res.data && res.data.id) {
      currentDoctorId.value = res.data.id
      return res.data.id
    }
    return null
  } catch (error) {
    console.error('获取医生信息失败', error)
    return null
  }
}

const loadData = async () => {
  try {
    if (!currentDoctorId.value) {
      const doctorId = await loadDoctorId()
      if (!doctorId) {
        ElMessage.error('无法获取医生信息')
        return
      }
    }
    
    const params = {
      ...searchForm,
      doctorId: currentDoctorId.value,
      current: pagination.current,
      size: pagination.size
    }
    const res = await getPatientList(params)
    tableData.value = res.data.records
    pagination.total = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '加载数据失败')
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    patientNo: '',
    diseaseType: ''
  })
  pagination.current = 1
  loadData()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.current = 1
  loadData()
}

const handleCurrentChange = (current) => {
  pagination.current = current
  loadData()
}

const handleViewDetail = async (row) => {
  try {
    const res = await getPatientById(row.id)
    currentPatient.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载患者信息失败')
  }
}

const handleViewHistory = async (row) => {
  historyActiveTab.value = 'risk'
  try {
    const riskRes = await getRiskAssessmentList({
      patientId: row.id,
      current: 1,
      size: 1000
    })
    riskHistoryData.value = riskRes.data.records || []
    
    const assignmentRes = await getDoctorAssignmentList({
      patientId: row.id,
      current: 1,
      size: 1000
    })
    assignmentHistoryData.value = assignmentRes.data.records || []
    
    historyDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  }
}

const handleViewRecords = async (row) => {
  try {
    const res = await getMedicalRecordList({
      patientId: row.id,
      current: 1,
      size: 1000
    })
    medicalRecordsData.value = res.data.records || []
    recordsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载诊疗记录失败')
  }
}

onMounted(() => {
  loadRiskLevelOptions()
  loadData()
})
</script>

<style scoped>
.doctor-patient-manage {
  height: 100%;
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
