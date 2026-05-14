<template>
  <div class="medical-record-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>诊疗记录录入</span>
          <el-button type="primary" @click="handleAdd">添加诊疗记录</el-button>
        </div>
      </template>

      <el-row :gutter="20" class="statistics-row">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="statistic-title">总记录数</div>
              <div class="statistic-value">{{ statistics.totalRecords || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="statistic-title">今日记录</div>
              <div class="statistic-value">{{ statistics.todayRecords || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="statistic-title">本月记录</div>
              <div class="statistic-value">{{ statistics.thisMonthRecords || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="statistic-title">当前筛选记录</div>
              <div class="statistic-value">{{ pagination.total || 0 }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

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
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="searchForm.startDate"
              type="date"
              placeholder="请选择开始日期"
              value-format="YYYY-MM-DD"
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker
              v-model="searchForm.endDate"
              type="date"
              placeholder="请选择结束日期"
              value-format="YYYY-MM-DD"
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="recordDate" label="诊疗日期" width="120" />
        <el-table-column prop="patientName" label="患者姓名" width="120" />
        <el-table-column prop="doctorName" label="医生姓名" width="120" />
        <el-table-column prop="chiefComplaint" label="主诉" width="200" show-overflow-tooltip />
        <el-table-column prop="diagnosis" label="诊断" show-overflow-tooltip />
        <el-table-column label="用药情况">
          <template #default="scope">
            <div v-if="scope.row.medicines && scope.row.medicines.length > 0">
              <el-tag v-for="(med, index) in scope.row.medicines" :key="index" size="small" style="margin-right: 5px">
                {{ med.medicineName }} × {{ med.quantity }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
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

      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="800px"
        @close="handleDialogClose"
      >
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="100px"
        >
          <el-row :gutter="20">
            <el-col :span="12">
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
            </el-col>
            <el-col :span="12">
              <el-form-item label="医生" prop="doctorId">
                <el-select v-model="formData.doctorId" placeholder="请选择医生" filterable style="width: 100%">
                  <el-option
                    v-for="item in doctorOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="诊疗日期" prop="recordDate">
            <el-date-picker
              v-model="formData.recordDate"
              type="date"
              placeholder="请选择诊疗日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="主诉" prop="chiefComplaint">
            <el-input
              v-model="formData.chiefComplaint"
              type="textarea"
              :rows="2"
              placeholder="请输入主诉"
            />
          </el-form-item>
          <el-form-item label="现病史" prop="presentIllness">
            <el-input
              v-model="formData.presentIllness"
              type="textarea"
              :rows="3"
              placeholder="请输入现病史"
            />
          </el-form-item>
          <el-form-item label="体格检查" prop="physicalExamination">
            <el-input
              v-model="formData.physicalExamination"
              type="textarea"
              :rows="3"
              placeholder="请输入体格检查结果"
            />
          </el-form-item>
          <el-form-item label="诊断" prop="diagnosis">
            <el-input
              v-model="formData.diagnosis"
              type="textarea"
              :rows="2"
              placeholder="请输入诊断"
            />
          </el-form-item>
          <el-form-item label="治疗方案" prop="treatmentPlan">
            <el-input
              v-model="formData.treatmentPlan"
              type="textarea"
              :rows="3"
              placeholder="请输入治疗方案"
            />
          </el-form-item>
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
          <el-form-item label="备注" prop="remarks">
            <el-input
              v-model="formData.remarks"
              type="textarea"
              :rows="2"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMedicalRecordList,
  getMedicalRecordById,
  addMedicalRecord,
  updateMedicalRecord,
  deleteMedicalRecord,
  getMedicalRecordStatistics
} from '@/api/medicalRecord'
import { getPatientList } from '@/api/patient'
import { getDoctorList } from '@/api/doctor'
import { getMedicineList } from '@/api/medicine'

const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加诊疗记录')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const patientOptions = ref([])
const doctorOptions = ref([])
const medicineOptions = ref([])

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const statistics = reactive({
  totalRecords: 0,
  todayRecords: 0,
  thisMonthRecords: 0,
  byPatientCount: 0,
  byDoctorCount: 0
})

const searchForm = reactive({
  patientId: null,
  doctorId: null,
  startDate: null,
  endDate: null
})

const formData = reactive({
  id: null,
  patientId: null,
  doctorId: null,
  recordDate: null,
  chiefComplaint: '',
  presentIllness: '',
  physicalExamination: '',
  diagnosis: '',
  treatmentPlan: '',
  medication: '',
  remarks: '',
  medicines: []
})

const formRules = {
  patientId: [
    { required: true, message: '请选择患者', trigger: 'change' }
  ],
  doctorId: [
    { required: true, message: '请选择医生', trigger: 'change' }
  ],
  recordDate: [
    { required: true, message: '请选择诊疗日期', trigger: 'change' }
  ]
}

const loadPatientOptions = async () => {
  try {
    const res = await getPatientList({ current: 1, size: 1000 })
    patientOptions.value = res.data.records.map(item => ({
      id: item.id,
      name: item.name
    }))
  } catch (error) {
    console.error('加载患者列表失败', error)
  }
}

const loadDoctorOptions = async () => {
  try {
    const res = await getDoctorList({ current: 1, size: 1000 })
    doctorOptions.value = res.data.records.map(item => ({
      id: item.id,
      name: item.name
    }))
  } catch (error) {
    console.error('加载医生列表失败', error)
  }
}

const loadMedicineOptions = async () => {
  try {
    const res = await getMedicineList({ current: 1, size: 1000 })
    medicineOptions.value = res.data.records.map(item => ({
      id: item.id,
      medicineName: item.medicineName,
      medicineCode: item.medicineCode
    }))
  } catch (error) {
    console.error('加载药品列表失败', error)
  }
}

const loadStatistics = async () => {
  try {
    const res = await getMedicalRecordStatistics({
      patientId: searchForm.patientId,
      doctorId: searchForm.doctorId
    })
    Object.assign(statistics, res.data)
  } catch (error) {
    console.error('加载统计信息失败', error)
  }
}

const loadData = async () => {
  try {
    const params = {
      ...searchForm,
      current: pagination.current,
      size: pagination.size
    }
    const res = await getMedicalRecordList(params)
    tableData.value = res.data.records
    pagination.total = res.data.total
    loadStatistics()
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
    patientId: null,
    doctorId: null,
    startDate: null,
    endDate: null
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

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '添加诊疗记录'
  resetForm()
  formData.recordDate = new Date().toISOString().split('T')[0]
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑诊疗记录'
  try {
    const res = await getMedicalRecordById(row.id)
    const data = res.data
    Object.assign(formData, {
      id: data.id,
      patientId: data.patientId,
      doctorId: data.doctorId,
      recordDate: data.recordDate,
      chiefComplaint: data.chiefComplaint || '',
      presentIllness: data.presentIllness || '',
      physicalExamination: data.physicalExamination || '',
      diagnosis: data.diagnosis || '',
      treatmentPlan: data.treatmentPlan || '',
      medication: data.medication || '',
      remarks: data.remarks || '',
      medicines: (data.medicines || []).map(m => ({
        id: m.id,
        medicineId: m.medicineId,
        quantity: m.quantity,
        dosage: m.dosage || ''
      }))
    })
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const submitData = {
          ...formData,
          medicines: formData.medicines.filter(m => m.medicineId && m.quantity)
        }
        
        if (isEdit.value) {
          await updateMedicalRecord(submitData)
          ElMessage.success('更新成功')
        } else {
          await addMedicalRecord(submitData)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该诊疗记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteMedicalRecord(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
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

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    patientId: null,
    doctorId: null,
    recordDate: null,
    chiefComplaint: '',
    presentIllness: '',
    physicalExamination: '',
    diagnosis: '',
    treatmentPlan: '',
    medication: '',
    remarks: '',
    medicines: []
  })
  formRef.value?.clearValidate()
}

onMounted(() => {
  loadPatientOptions()
  loadDoctorOptions()
  loadMedicineOptions()
  loadData()
})
</script>

<style scoped>
.medical-record-manage {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics-row {
  margin-bottom: 20px;
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
  margin-bottom: 12px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.add-medicine-btn {
  margin-top: 10px;
}

.statistic-item {
  text-align: center;
}

.statistic-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.statistic-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}
</style>
