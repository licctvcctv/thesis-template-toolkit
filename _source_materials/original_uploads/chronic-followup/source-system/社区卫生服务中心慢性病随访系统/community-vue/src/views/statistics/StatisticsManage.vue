<template>
  <div class="statistics-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据统计</span>
        </div>
      </template>

      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="患者总数" :value="statistics.totalPatients">
              <template #suffix>
                <span style="font-size: 14px;">人</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="随访任务总数" :value="statistics.totalFollowupTasks">
              <template #suffix>
                <span style="font-size: 14px;">个</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="已完成任务" :value="statistics.completedFollowupTasks">
              <template #suffix>
                <span style="font-size: 14px;">个</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="随访完成率" :value="statistics.followupCompletionRate">
              <template #suffix>
                <span style="font-size: 14px;">%</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="随访统计" name="followup">
          <el-card :body-style="{ padding: '20px' }">
            <template #header>
              <span>随访完成情况</span>
            </template>
            <div ref="followupChartRef" class="chart-container"></div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="医生工作量统计" name="doctor">
          <el-table :data="statistics.doctorWorkloads" border style="width: 100%">
            <el-table-column prop="doctorName" label="医生姓名" width="150" />
            <el-table-column prop="patientCount" label="负责患者数" width="120" />
            <el-table-column prop="followupTaskCount" label="随访任务数" width="120" />
            <el-table-column prop="followupRecordCount" label="随访记录数" width="120" />
            <el-table-column prop="medicalRecordCount" label="诊疗记录数" width="120" />
            <el-table-column label="总工作量" width="120">
              <template #default="scope">
                {{ scope.row.patientCount + scope.row.followupTaskCount + scope.row.followupRecordCount + scope.row.medicalRecordCount }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getStatistics } from '@/api/statistics'
import * as echarts from 'echarts'

const activeTab = ref('followup')
const statistics = reactive({
  totalPatients: 0,
  totalFollowupTasks: 0,
  completedFollowupTasks: 0,
  followupCompletionRate: 0,
  totalFollowupRecords: 0,
  doctorWorkloads: []
})

const followupChartRef = ref(null)
let followupChart = null

onMounted(() => {
  loadStatistics()
})

const loadStatistics = async () => {
  try {
    const res = await getStatistics()
    Object.assign(statistics, res.data)
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

const handleTabChange = (tab) => {
  nextTick(() => {
    if (tab === 'followup') {
      initFollowupChart()
    }
  })
}

const initCharts = () => {
  initFollowupChart()
}

const initFollowupChart = () => {
  if (!followupChartRef.value) return
  if (followupChart) {
    followupChart.dispose()
  }
  followupChart = echarts.init(followupChartRef.value)
  
  const pendingCount = statistics.totalFollowupTasks - statistics.completedFollowupTasks
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(function(item) {
          result += item.marker + item.seriesName + ': ' + item.value + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['总任务数', '已完成', '待办'],
      top: 10,
      left: 'center'
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '10%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['随访任务统计'],
      axisLabel: {
        fontSize: 14
      }
    },
    yAxis: {
      type: 'value',
      name: '数量',
      nameLocation: 'middle',
      nameGap: 50,
      axisLabel: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '总任务数',
        type: 'bar',
        data: [statistics.totalFollowupTasks],
        itemStyle: { color: '#909399' },
        barWidth: '40%'
      },
      {
        name: '已完成',
        type: 'bar',
        data: [statistics.completedFollowupTasks],
        itemStyle: { color: '#67c23a' },
        barWidth: '40%'
      },
      {
        name: '待办',
        type: 'bar',
        data: [pendingCount],
        itemStyle: { color: '#e6a23c' },
        barWidth: '40%'
      }
    ]
  }
  
  followupChart.setOption(option)
  
  // 监听窗口大小变化，自动调整图表大小
  const resizeHandler = () => {
    if (followupChart) {
      followupChart.resize()
    }
  }
  window.addEventListener('resize', resizeHandler)
  
  // 组件卸载时移除监听器
  return () => {
    window.removeEventListener('resize', resizeHandler)
  }
}
</script>

<style scoped>
.statistics-manage {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: calc(100vh - 400px);
  min-height: 500px;
}
</style>
