<template>
  <div class="medicine-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>药品管理</span>
          <el-button type="primary" @click="handleAdd">添加药品</el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="药品名称">
            <el-input v-model="searchForm.medicineName" placeholder="请输入药品名称" clearable />
          </el-form-item>
          <el-form-item label="药品编码">
            <el-input v-model="searchForm.medicineCode" placeholder="请输入药品编码" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="medicineCode" label="药品编码" width="120" />
        <el-table-column prop="medicineName" label="药品名称" width="180" />
        <el-table-column prop="specification" label="规格" width="150" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="manufacturer" label="生产厂家" width="200" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="scope">
            ¥{{ scope.row.price ? scope.row.price.toFixed(2) : '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="description" label="药品描述" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
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
        width="600px"
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
              <el-form-item label="药品编码" prop="medicineCode">
                <el-input v-model="formData.medicineCode" placeholder="请输入药品编码" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="药品名称" prop="medicineName">
                <el-input v-model="formData.medicineName" placeholder="请输入药品名称" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="规格" prop="specification">
                <el-input v-model="formData.specification" placeholder="请输入规格" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="单位" prop="unit">
                <el-input v-model="formData.unit" placeholder="请输入单位" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="生产厂家" prop="manufacturer">
            <el-input v-model="formData.manufacturer" placeholder="请输入生产厂家" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="价格" prop="price">
                <el-input-number
                  v-model="formData.price"
                  :precision="2"
                  :min="0"
                  :step="0.01"
                  style="width: 100%"
                  placeholder="请输入价格"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="库存" prop="stock">
                <el-input-number
                  v-model="formData.stock"
                  :min="0"
                  :step="1"
                  style="width: 100%"
                  placeholder="请输入库存"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="药品描述" prop="description">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="3"
              placeholder="请输入药品描述"
            />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="formData.status">
              <el-radio :label="1">启用</el-radio>
              <el-radio :label="0">停用</el-radio>
            </el-radio-group>
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
  getMedicineList,
  addMedicine,
  updateMedicine,
  deleteMedicine
} from '@/api/medicine'

const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加药品')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const searchForm = reactive({
  medicineName: '',
  medicineCode: ''
})

const formData = reactive({
  id: null,
  medicineCode: '',
  medicineName: '',
  specification: '',
  unit: '',
  manufacturer: '',
  price: null,
  stock: 0,
  description: '',
  status: 1
})

const formRules = {
  medicineCode: [
    { required: true, message: '请输入药品编码', trigger: 'blur' }
  ],
  medicineName: [
    { required: true, message: '请输入药品名称', trigger: 'blur' }
  ]
}

const loadData = async () => {
  try {
    const params = {
      ...searchForm,
      current: pagination.current,
      size: pagination.size
    }
    const res = await getMedicineList(params)
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
  searchForm.medicineName = ''
  searchForm.medicineCode = ''
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
  dialogTitle.value = '添加药品'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑药品'
  Object.assign(formData, {
    id: row.id,
    medicineCode: row.medicineCode,
    medicineName: row.medicineName,
    specification: row.specification || '',
    unit: row.unit || '',
    manufacturer: row.manufacturer || '',
    price: row.price,
    stock: row.stock || 0,
    description: row.description || '',
    status: row.status
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateMedicine(formData)
          ElMessage.success('更新成功')
        } else {
          await addMedicine(formData)
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
  ElMessageBox.confirm('确定要删除该药品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteMedicine(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    medicineCode: '',
    medicineName: '',
    specification: '',
    unit: '',
    manufacturer: '',
    price: null,
    stock: 0,
    description: '',
    status: 1
  })
  formRef.value?.clearValidate()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.medicine-manage {
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
