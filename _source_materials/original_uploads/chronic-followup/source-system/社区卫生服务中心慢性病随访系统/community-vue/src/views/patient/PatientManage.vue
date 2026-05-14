<template>
  <div class="patient-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>患者管理</span>
          <div>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button type="warning" @click="handleImport">导入</el-button>
            <el-button type="primary" @click="handleAdd">添加患者</el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="信息管理" name="info">
          <div class="search-bar">
            <el-form :inline="true" :model="searchForm">
              <el-form-item label="姓名">
                <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
              </el-form-item>
              <el-form-item label="患者编号">
                <el-input v-model="searchForm.patientNo" placeholder="请输入患者编号" clearable />
              </el-form-item>
              <el-form-item label="疾病历史">
                <el-input v-model="searchForm.diseaseType" placeholder="请输入疾病历史" clearable />
              </el-form-item>
              <el-form-item label="风险等级">
                <el-select v-model="searchForm.riskLevel" placeholder="请选择风险等级" clearable style="width: 150px">
                  <el-option
                    v-for="item in riskLevelOptions"
                    :key="item.levelCode"
                    :label="item.levelName"
                    :value="item.levelCode"
                  />
                </el-select>
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
            <el-table-column prop="diseaseType" label="疾病历史" />
            <el-table-column prop="riskLevelName" label="风险等级" width="100">
              <template #default="scope">
                <el-tag :type="getRiskLevelTagType(scope.row.riskLevel)">
                  {{ scope.row.riskLevelName }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="doctorName" label="负责医生" />
            <el-table-column label="操作" fixed="right" width="380">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
                <el-button type="info" size="small" @click="handleRiskAssessment(scope.row)">风险评估</el-button>
                <el-button type="success" size="small" @click="handleAssignDoctor(scope.row)">分配医生</el-button>
                <el-button type="warning" size="small" @click="handleViewTrend(scope.row)">趋势图</el-button>
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
        </el-tab-pane>

        <el-tab-pane label="风险等级评估" name="risk">
          <div class="search-bar">
            <el-form :inline="true" :model="riskSearchForm">
              <el-form-item label="患者">
                <el-select v-model="riskSearchForm.patientId" placeholder="请选择患者" clearable filterable style="width: 200px">
                  <el-option
                    v-for="item in patientOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="风险等级">
                <el-select v-model="riskSearchForm.riskLevel" placeholder="请选择风险等级" clearable style="width: 150px">
                  <el-option
                    v-for="item in riskLevelOptions"
                    :key="item.levelCode"
                    :label="item.levelName"
                    :value="item.levelCode"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleRiskSearch">查询</el-button>
                <el-button @click="handleRiskReset">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="riskTableData" border style="width: 100%">
            <el-table-column prop="patientName" label="患者姓名" width="120" />
            <el-table-column prop="riskLevelName" label="风险等级" width="120">
              <template #default="scope">
                <el-tag :type="getRiskLevelTagType(scope.row.riskLevel)">
                  {{ scope.row.riskLevelName }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assessmentDate" label="评估日期" width="120" />
            <el-table-column prop="assessorName" label="评估人" width="120" />
            <el-table-column prop="assessmentResult" label="评估结果" />
            <el-table-column prop="remarks" label="备注" width="150" />
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="riskPagination.current"
              v-model:page-size="riskPagination.size"
              :total="riskPagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleRiskSizeChange"
              @current-change="handleRiskCurrentChange"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="数据录入" name="vitalSigns">
          <div class="search-bar">
            <el-form :inline="true" :model="vitalSignsSearchForm">
              <el-form-item label="患者">
                <el-select v-model="vitalSignsSearchForm.patientId" placeholder="请选择患者" clearable filterable style="width: 200px">
                  <el-option
                    v-for="item in patientOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="录入时间">
                <el-date-picker
                  v-model="vitalSignsDateRange"
                  type="datetimerange"
                  range-separator="至"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  value-format="YYYY-MM-DD HH:mm:ss"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleVitalSignsSearch">查询</el-button>
                <el-button @click="handleVitalSignsReset">重置</el-button>
                <el-button type="success" @click="handleVitalSignsAdd">录入数据</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="vitalSignsTableData" border style="width: 100%">
            <el-table-column prop="patientName" label="患者姓名" width="120" />
            <el-table-column prop="recordDate" label="录入时间" width="180">
              <template #default="scope">
                {{ scope.row.recordDate ? dayjs(scope.row.recordDate).format('YYYY-MM-DD HH:mm:ss') : '' }}
              </template>
            </el-table-column>
            <el-table-column prop="bloodPressure" label="血压" width="120" />
            <el-table-column prop="bloodSugar" label="血糖" width="100" />
            <el-table-column prop="bloodSugarTypeName" label="血糖类型" width="100" />
            <el-table-column prop="remarks" label="备注" />
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleVitalSignsEdit(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" @click="handleVitalSignsDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="vitalSignsPagination.page"
              v-model:page-size="vitalSignsPagination.size"
              :total="vitalSignsPagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleVitalSignsSizeChange"
              @current-change="handleVitalSignsCurrentChange"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="医生分配记录" name="assignment">
          <div class="search-bar">
            <el-form :inline="true" :model="assignmentSearchForm">
              <el-form-item label="患者">
                <el-select v-model="assignmentSearchForm.patientId" placeholder="请选择患者" clearable filterable style="width: 200px">
                  <el-option
                    v-for="item in patientOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="医生">
                <el-select v-model="assignmentSearchForm.doctorId" placeholder="请选择医生" clearable filterable style="width: 200px">
                  <el-option
                    v-for="item in doctorOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleAssignmentSearch">查询</el-button>
                <el-button @click="handleAssignmentReset">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="assignmentTableData" border style="width: 100%">
            <el-table-column prop="patientName" label="患者姓名" width="120" />
            <el-table-column prop="doctorName" label="医生姓名" width="120" />
            <el-table-column prop="assignDate" label="分配日期" width="120" />
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

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="assignmentPagination.current"
              v-model:page-size="assignmentPagination.size"
              :total="assignmentPagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleAssignmentSizeChange"
              @current-change="handleAssignmentCurrentChange"
            />
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- 患者信息对话框 -->
      <el-dialog
        v-model="patientDialogVisible"
        :title="patientDialogTitle"
        width="700px"
        @close="handlePatientDialogClose"
      >
        <el-form
          ref="patientFormRef"
          :model="patientFormData"
          :rules="patientFormRules"
          label-width="100px"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="患者编号" prop="patientNo">
                <el-input v-model="patientFormData.patientNo" placeholder="留空自动生成" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="patientFormData.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="性别" prop="gender">
                <el-radio-group v-model="patientFormData.gender">
                  <el-radio :label="1">男</el-radio>
                  <el-radio :label="2">女</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="出生日期" prop="birthday">
                <el-date-picker
                  v-model="patientFormData.birthday"
                  type="date"
                  placeholder="请选择出生日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="身份证号" prop="idCard">
                <el-input v-model="patientFormData.idCard" placeholder="请输入身份证号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="patientFormData.phone" placeholder="请输入手机号" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="地址" prop="address">
            <el-input v-model="patientFormData.address" placeholder="请输入地址" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="疾病历史" prop="diseaseType">
                <el-input v-model="patientFormData.diseaseType" type="textarea" :rows="3" placeholder="请输入疾病历史" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="确诊日期" prop="diagnosisDate">
                <el-date-picker
                  v-model="patientFormData.diagnosisDate"
                  type="date"
                  placeholder="请选择确诊日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="风险等级" prop="riskLevel">
                <el-select v-model="patientFormData.riskLevel" placeholder="请选择风险等级" style="width: 100%">
                  <el-option
                    v-for="item in riskLevelOptions"
                    :key="item.levelCode"
                    :label="item.levelName"
                    :value="item.levelCode"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="负责医生" prop="currentDoctorId">
                <el-select v-model="patientFormData.currentDoctorId" placeholder="请选择医生" filterable style="width: 100%">
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
        </el-form>
        <template #footer>
          <el-button @click="patientDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePatientSubmit" :loading="patientSubmitLoading">确定</el-button>
        </template>
      </el-dialog>

      <!-- 风险评估对话框 -->
      <el-dialog
        v-model="riskDialogVisible"
        title="风险等级评估"
        width="600px"
        @close="handleRiskDialogClose"
      >
        <el-form
          ref="riskFormRef"
          :model="riskFormData"
          :rules="riskFormRules"
          label-width="100px"
        >
          <el-form-item label="患者">
            <el-input v-model="riskFormData.patientName" disabled />
          </el-form-item>
          <el-form-item label="风险等级" prop="riskLevel">
            <el-select v-model="riskFormData.riskLevel" placeholder="请选择风险等级" style="width: 100%">
              <el-option
                v-for="item in riskLevelOptions"
                :key="item.levelCode"
                :label="item.levelName"
                :value="item.levelCode"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="评估日期" prop="assessmentDate">
            <el-date-picker
              v-model="riskFormData.assessmentDate"
              type="date"
              placeholder="请选择评估日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="评估结果" prop="assessmentResult">
            <el-input
              v-model="riskFormData.assessmentResult"
              type="textarea"
              :rows="4"
              placeholder="请输入评估结果"
            />
          </el-form-item>
          <el-form-item label="备注" prop="remarks">
            <el-input
              v-model="riskFormData.remarks"
              type="textarea"
              :rows="2"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="riskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleRiskSubmit" :loading="riskSubmitLoading">确定</el-button>
        </template>
      </el-dialog>

      <!-- 分配医生对话框 -->
      <el-dialog
        v-model="assignmentDialogVisible"
        title="分配医生"
        width="500px"
        @close="handleAssignmentDialogClose"
      >
        <el-form
          ref="assignmentFormRef"
          :model="assignmentFormData"
          :rules="assignmentFormRules"
          label-width="100px"
        >
          <el-form-item label="患者">
            <el-input v-model="assignmentFormData.patientName" disabled />
          </el-form-item>
          <el-form-item label="医生" prop="doctorId">
            <el-select v-model="assignmentFormData.doctorId" placeholder="请选择医生" filterable style="width: 100%">
              <el-option
                v-for="item in doctorOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="备注" prop="remarks">
            <el-input
              v-model="assignmentFormData.remarks"
              type="textarea"
              :rows="3"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="assignmentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAssignmentSubmit" :loading="assignmentSubmitLoading">确定</el-button>
        </template>
      </el-dialog>

      <!-- 导入对话框 -->
      <el-dialog
        v-model="importDialogVisible"
        title="导入患者信息"
        width="500px"
      >
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
        >
          <template #trigger>
            <el-button type="primary">选择文件</el-button>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              只能上传Excel文件，支持.xlsx和.xls格式
            </div>
          </template>
        </el-upload>
        <template #footer>
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">导入</el-button>
        </template>
      </el-dialog>

      <!-- 数据录入对话框 -->
      <el-dialog
        v-model="vitalSignsDialogVisible"
        :title="vitalSignsDialogTitle"
        width="600px"
        @close="handleVitalSignsDialogClose"
      >
        <el-form
          ref="vitalSignsFormRef"
          :model="vitalSignsFormData"
          :rules="vitalSignsFormRules"
          label-width="100px"
        >
          <el-form-item label="患者" prop="patientId">
            <el-select v-model="vitalSignsFormData.patientId" placeholder="请选择患者" filterable style="width: 100%">
              <el-option
                v-for="item in patientOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="录入时间" prop="recordDate">
            <el-date-picker
              v-model="vitalSignsFormData.recordDate"
              type="datetime"
              placeholder="请选择录入时间"
              style="width: 100%"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="收缩压">
                <el-input-number v-model="vitalSignsFormData.bloodPressureSystolic" :min="0" :max="300" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="舒张压">
                <el-input-number v-model="vitalSignsFormData.bloodPressureDiastolic" :min="0" :max="200" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="血糖值">
                <el-input-number v-model="vitalSignsFormData.bloodSugar" :precision="2" :step="0.1" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="血糖类型">
                <el-select v-model="vitalSignsFormData.bloodSugarType" placeholder="请选择" style="width: 100%">
                  <el-option label="空腹" value="fasting" />
                  <el-option label="餐后" value="postprandial" />
                  <el-option label="随机" value="random" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注">
            <el-input v-model="vitalSignsFormData.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="vitalSignsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleVitalSignsSubmit" :loading="vitalSignsSubmitLoading">确定</el-button>
        </template>
      </el-dialog>

      <!-- 趋势图对话框 -->
      <el-dialog
        v-model="trendDialogVisible"
        title="血压血糖趋势图"
        width="900px"
      >
        <div v-if="selectedPatientId">
          <div style="margin-bottom: 20px;">
            <el-date-picker
              v-model="trendDateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="loadTrendData"
            />
          </div>
          <div ref="trendChartRef" style="width: 100%; height: 400px;"></div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import {
  getPatientList,
  addPatient,
  updatePatient,
  deletePatient,
  exportPatient,
  importPatient
} from '@/api/patient'
import {
  getRiskAssessmentList,
  addRiskAssessment,
  getRiskLevelConfigs
} from '@/api/riskAssessment'
import {
  getDoctorAssignmentList,
  assignDoctor
} from '@/api/doctorAssignment'
import { getEnabledDepartmentList } from '@/api/department'
import { getDoctorList } from '@/api/doctor'
import {
  getPatientVitalSignsPage,
  getPatientVitalSignsById,
  createPatientVitalSigns,
  updatePatientVitalSigns,
  deletePatientVitalSigns,
  getPatientVitalSignsByPatientId
} from '@/api/patientVitalSigns'
import * as echarts from 'echarts'

const activeTab = ref('info')
const tableData = ref([])
const riskTableData = ref([])
const assignmentTableData = ref([])
const vitalSignsTableData = ref([])
const patientDialogVisible = ref(false)
const riskDialogVisible = ref(false)
const assignmentDialogVisible = ref(false)
const importDialogVisible = ref(false)
const vitalSignsDialogVisible = ref(false)
const patientDialogTitle = ref('添加患者')
const patientSubmitLoading = ref(false)
const riskSubmitLoading = ref(false)
const assignmentSubmitLoading = ref(false)
const importLoading = ref(false)
const patientFormRef = ref(null)
const riskFormRef = ref(null)
const assignmentFormRef = ref(null)
const uploadRef = ref(null)
const isEdit = ref(false)
const riskLevelOptions = ref([])
const doctorOptions = ref([])
const patientOptions = ref([])
const currentPatientId = ref(null)
const importFile = ref(null)

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const riskPagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const assignmentPagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const vitalSignsPagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const searchForm = reactive({
  name: '',
  patientNo: '',
  diseaseType: '',
  riskLevel: ''
})

const riskSearchForm = reactive({
  patientId: null,
  riskLevel: ''
})

const assignmentSearchForm = reactive({
  patientId: null,
  doctorId: null
})

const vitalSignsSearchForm = reactive({
  patientId: null,
  startDate: null,
  endDate: null
})

const vitalSignsDateRange = ref(null)
const vitalSignsDialogTitle = ref('录入数据')
const vitalSignsSubmitLoading = ref(false)
const vitalSignsFormRef = ref(null)
const vitalSignsFormData = reactive({
  id: null,
  patientId: null,
  recordDate: '',
  bloodPressureSystolic: null,
  bloodPressureDiastolic: null,
  bloodSugar: null,
  bloodSugarType: '',
  remarks: ''
})

const vitalSignsFormRules = {
  patientId: [{ required: true, message: '请选择患者', trigger: 'change' }],
  recordDate: [{ required: true, message: '请选择录入时间', trigger: 'change' }]
}

const trendDialogVisible = ref(false)
const trendChartRef = ref(null)
const trendChart = ref(null)
const selectedPatientId = ref(null)
const trendDateRange = ref(null)

const patientFormData = reactive({
  id: null,
  patientNo: '',
  name: '',
  gender: null,
  birthday: null,
  idCard: '',
  phone: '',
  address: '',
  diseaseType: '',
  diagnosisDate: null,
  currentDoctorId: null,
  riskLevel: 'low'
})

const riskFormData = reactive({
  patientId: null,
  patientName: '',
  riskLevel: '',
  assessmentDate: null,
  assessmentResult: '',
  remarks: ''
})

const assignmentFormData = reactive({
  patientId: null,
  patientName: '',
  doctorId: null,
  remarks: ''
})

const patientFormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

const riskFormRules = {
  riskLevel: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ],
  assessmentDate: [
    { required: true, message: '请选择评估日期', trigger: 'change' }
  ],
  assessmentResult: [
    { required: true, message: '请输入评估结果', trigger: 'blur' }
  ]
}

const assignmentFormRules = {
  doctorId: [
    { required: true, message: '请选择医生', trigger: 'change' }
  ]
}

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

const loadData = async () => {
  try {
    const params = {
      ...searchForm,
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

const loadRiskData = async () => {
  try {
    const params = {
      ...riskSearchForm,
      current: riskPagination.current,
      size: riskPagination.size
    }
    const res = await getRiskAssessmentList(params)
    riskTableData.value = res.data.records
    riskPagination.total = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '加载数据失败')
  }
}

const loadAssignmentData = async () => {
  try {
    const params = {
      ...assignmentSearchForm,
      current: assignmentPagination.current,
      size: assignmentPagination.size
    }
    const res = await getDoctorAssignmentList(params)
    assignmentTableData.value = res.data.records
    assignmentPagination.total = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '加载数据失败')
  }
}

const handleTabChange = (tab) => {
  if (tab === 'risk') {
    loadRiskData()
  } else if (tab === 'assignment') {
    loadAssignmentData()
  } else if (tab === 'vitalSigns') {
    loadVitalSignsData()
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
    diseaseType: '',
    riskLevel: ''
  })
  pagination.current = 1
  loadData()
}

const handleRiskSearch = () => {
  riskPagination.current = 1
  loadRiskData()
}

const handleRiskReset = () => {
  Object.assign(riskSearchForm, {
    patientId: null,
    riskLevel: ''
  })
  riskPagination.current = 1
  loadRiskData()
}

const handleAssignmentSearch = () => {
  assignmentPagination.current = 1
  loadAssignmentData()
}

const handleAssignmentReset = () => {
  Object.assign(assignmentSearchForm, {
    patientId: null,
    doctorId: null
  })
  assignmentPagination.current = 1
  loadAssignmentData()
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

const handleRiskSizeChange = (size) => {
  riskPagination.size = size
  riskPagination.current = 1
  loadRiskData()
}

const handleRiskCurrentChange = (current) => {
  riskPagination.current = current
  loadRiskData()
}

const handleAssignmentSizeChange = (size) => {
  assignmentPagination.size = size
  assignmentPagination.current = 1
  loadAssignmentData()
}

const handleAssignmentCurrentChange = (current) => {
  assignmentPagination.current = current
  loadAssignmentData()
}

const handleAdd = () => {
  isEdit.value = false
  patientDialogTitle.value = '添加患者'
  resetPatientForm()
  patientDialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  patientDialogTitle.value = '编辑患者'
  Object.assign(patientFormData, {
    id: row.id,
    patientNo: row.patientNo,
    name: row.name,
    gender: row.gender,
    birthday: row.birthday,
    idCard: row.idCard || '',
    phone: row.phone || '',
    address: row.address || '',
    diseaseType: row.diseaseType || '',
    diagnosisDate: row.diagnosisDate,
    currentDoctorId: row.currentDoctorId,
    riskLevel: row.riskLevel || 'low'
  })
  patientDialogVisible.value = true
}

const handlePatientSubmit = async () => {
  if (!patientFormRef.value) return
  
  await patientFormRef.value.validate(async (valid) => {
    if (valid) {
      patientSubmitLoading.value = true
      try {
        if (isEdit.value) {
          await updatePatient(patientFormData)
          ElMessage.success('更新成功')
        } else {
          await addPatient(patientFormData)
          ElMessage.success('添加成功')
        }
        patientDialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        patientSubmitLoading.value = false
      }
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该患者吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deletePatient(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
}

const handleRiskAssessment = (row) => {
  currentPatientId.value = row.id
  riskFormData.patientId = row.id
  riskFormData.patientName = row.name
  riskFormData.riskLevel = row.riskLevel || 'low'
  riskFormData.assessmentDate = new Date().toISOString().split('T')[0]
  riskDialogVisible.value = true
}

const handleRiskSubmit = async () => {
  if (!riskFormRef.value) return
  
  await riskFormRef.value.validate(async (valid) => {
    if (valid) {
      riskSubmitLoading.value = true
      try {
        const userId = localStorage.getItem('token')
        await addRiskAssessment({
          ...riskFormData,
          assessorId: userId ? parseInt(userId) : null
        })
        ElMessage.success('评估成功')
        riskDialogVisible.value = false
        loadData()
        if (activeTab.value === 'risk') {
          loadRiskData()
        }
      } catch (error) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        riskSubmitLoading.value = false
      }
    }
  })
}

const handleAssignDoctor = (row) => {
  assignmentFormData.patientId = row.id
  assignmentFormData.patientName = row.name
  assignmentFormData.doctorId = row.currentDoctorId
  assignmentDialogVisible.value = true
}

const handleAssignmentSubmit = async () => {
  if (!assignmentFormRef.value) return
  
  await assignmentFormRef.value.validate(async (valid) => {
    if (valid) {
      assignmentSubmitLoading.value = true
      try {
        const userId = localStorage.getItem('token')
        await assignDoctor({
          patientId: assignmentFormData.patientId,
          doctorId: assignmentFormData.doctorId,
          assignerId: userId ? parseInt(userId) : null,
          remarks: assignmentFormData.remarks
        })
        ElMessage.success('分配成功')
        assignmentDialogVisible.value = false
        loadData()
        if (activeTab.value === 'assignment') {
          loadAssignmentData()
        }
      } catch (error) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        assignmentSubmitLoading.value = false
      }
    }
  })
}

const handleExport = async () => {
  try {
    await exportPatient(searchForm)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error(error.message || '导出失败')
  }
}

const handleImport = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  importLoading.value = true
  try {
    const res = await importPatient(importFile.value)
    ElMessage.success(res.message || '导入成功')
    importDialogVisible.value = false
    importFile.value = null
    uploadRef.value?.clearFiles()
    loadData()
  } catch (error) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const handlePatientDialogClose = () => {
  resetPatientForm()
}

const handleRiskDialogClose = () => {
  resetRiskForm()
}

const handleAssignmentDialogClose = () => {
  resetAssignmentForm()
}

const resetPatientForm = () => {
  Object.assign(patientFormData, {
    id: null,
    patientNo: '',
    name: '',
    gender: null,
    birthday: null,
    idCard: '',
    phone: '',
    address: '',
    diseaseType: '',
    diagnosisDate: null,
    currentDoctorId: null,
    riskLevel: 'low'
  })
  patientFormRef.value?.clearValidate()
}

const resetRiskForm = () => {
  Object.assign(riskFormData, {
    patientId: null,
    patientName: '',
    riskLevel: '',
    assessmentDate: null,
    assessmentResult: '',
    remarks: ''
  })
  riskFormRef.value?.clearValidate()
}

const resetAssignmentForm = () => {
  Object.assign(assignmentFormData, {
    patientId: null,
    patientName: '',
    doctorId: null,
    remarks: ''
  })
  assignmentFormRef.value?.clearValidate()
}

// 数据录入相关方法
const loadVitalSignsData = async () => {
  try {
    const params = {
      page: vitalSignsPagination.page,
      size: vitalSignsPagination.size,
      patientId: vitalSignsSearchForm.patientId,
      startDate: vitalSignsSearchForm.startDate,
      endDate: vitalSignsSearchForm.endDate
    }
    const res = await getPatientVitalSignsPage(params)
    vitalSignsTableData.value = res.data.records || []
    vitalSignsPagination.total = res.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleVitalSignsSearch = () => {
  if (vitalSignsDateRange.value && vitalSignsDateRange.value.length === 2) {
    vitalSignsSearchForm.startDate = vitalSignsDateRange.value[0]
    vitalSignsSearchForm.endDate = vitalSignsDateRange.value[1]
  } else {
    vitalSignsSearchForm.startDate = null
    vitalSignsSearchForm.endDate = null
  }
  vitalSignsPagination.page = 1
  loadVitalSignsData()
}

const handleVitalSignsReset = () => {
  vitalSignsSearchForm.patientId = null
  vitalSignsSearchForm.startDate = null
  vitalSignsSearchForm.endDate = null
  vitalSignsDateRange.value = null
  vitalSignsPagination.page = 1
  loadVitalSignsData()
}

const handleVitalSignsAdd = () => {
  vitalSignsDialogTitle.value = '录入数据'
  Object.assign(vitalSignsFormData, {
    id: null,
    patientId: null,
    recordDate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
    bloodPressureSystolic: null,
    bloodPressureDiastolic: null,
    bloodSugar: null,
    bloodSugarType: '',
    remarks: ''
  })
  vitalSignsDialogVisible.value = true
}

const handleVitalSignsEdit = async (row) => {
  try {
    const res = await getPatientVitalSignsById(row.id)
    if (!res.data) {
      ElMessage.error('数据不存在')
      return
    }
    vitalSignsDialogTitle.value = '编辑数据'
    Object.assign(vitalSignsFormData, {
      id: res.data.id,
      patientId: res.data.patientId,
      recordDate: res.data.recordDate ? dayjs(res.data.recordDate).format('YYYY-MM-DD HH:mm:ss') : dayjs().format('YYYY-MM-DD HH:mm:ss'),
      bloodPressureSystolic: res.data.bloodPressureSystolic,
      bloodPressureDiastolic: res.data.bloodPressureDiastolic,
      bloodSugar: res.data.bloodSugar,
      bloodSugarType: res.data.bloodSugarType || '',
      remarks: res.data.remarks || ''
    })
    vitalSignsDialogVisible.value = true
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  }
}

const handleVitalSignsSubmit = async () => {
  if (!vitalSignsFormRef.value) return
  await vitalSignsFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (vitalSignsFormData.id) {
          await updatePatientVitalSigns(vitalSignsFormData.id, vitalSignsFormData)
          ElMessage.success('更新成功')
        } else {
          await createPatientVitalSigns(vitalSignsFormData)
          ElMessage.success('录入成功')
        }
        vitalSignsDialogVisible.value = false
        loadVitalSignsData()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleVitalSignsDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据吗？', '提示', {
      type: 'warning'
    })
    await deletePatientVitalSigns(row.id)
    ElMessage.success('删除成功')
    loadVitalSignsData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleVitalSignsDialogClose = () => {
  vitalSignsFormRef.value?.clearValidate()
}

const handleVitalSignsSizeChange = () => {
  loadVitalSignsData()
}

const handleVitalSignsCurrentChange = () => {
  loadVitalSignsData()
}

// 趋势图相关方法
const handleViewTrend = (row) => {
  selectedPatientId.value = row.id
  trendDateRange.value = null
  trendDialogVisible.value = true
  setTimeout(() => {
    initTrendChart()
    loadTrendData()
  }, 100)
}

const handleViewTrendByRecord = (row) => {
  selectedPatientId.value = row.patientId
  trendDateRange.value = null
  trendDialogVisible.value = true
  setTimeout(() => {
    initTrendChart()
    loadTrendData()
  }, 100)
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart.value) {
    trendChart.value.dispose()
  }
  trendChart.value = echarts.init(trendChartRef.value)
}

const loadTrendData = async () => {
  if (!selectedPatientId.value || !trendChart.value) return
  try {
    const params = {}
    if (trendDateRange.value && trendDateRange.value.length === 2) {
      params.startDate = trendDateRange.value[0]
      params.endDate = trendDateRange.value[1]
    }
    const res = await getPatientVitalSignsByPatientId(selectedPatientId.value, params)
    const data = res.data || []
    
    const dates = data.map(item => item.recordDate ? dayjs(item.recordDate).format('YYYY-MM-DD HH:mm') : '')
    const systolicData = data.map(item => item.bloodPressureSystolic).filter(v => v != null)
    const diastolicData = data.map(item => item.bloodPressureDiastolic).filter(v => v != null)
    const bloodSugarData = data.map(item => item.bloodSugar ? Number(item.bloodSugar) : null).filter(v => v != null)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['收缩压', '舒张压', '血糖']
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false
      },
      yAxis: [
        {
          type: 'value',
          name: '血压(mmHg)',
          position: 'left',
          axisLabel: {
            formatter: '{value}'
          }
        },
        {
          type: 'value',
          name: '血糖(mmol/L)',
          position: 'right',
          axisLabel: {
            formatter: '{value}'
          }
        }
      ],
      series: [
        {
          name: '收缩压',
          type: 'line',
          data: data.map(item => item.bloodPressureSystolic),
          smooth: true,
          itemStyle: { color: '#f56c6c' }
        },
        {
          name: '舒张压',
          type: 'line',
          data: data.map(item => item.bloodPressureDiastolic),
          smooth: true,
          itemStyle: { color: '#409eff' }
        },
        {
          name: '血糖',
          type: 'line',
          yAxisIndex: 1,
          data: data.map(item => item.bloodSugar ? Number(item.bloodSugar) : null),
          smooth: true,
          itemStyle: { color: '#67c23a' }
        }
      ]
    }
    
    trendChart.value.setOption(option)
  } catch (error) {
    ElMessage.error('加载趋势数据失败')
  }
}

onMounted(() => {
  loadRiskLevelOptions()
  loadDoctorOptions()
  loadPatientOptions()
  loadData()
})
</script>

<style scoped>
.patient-manage {
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
