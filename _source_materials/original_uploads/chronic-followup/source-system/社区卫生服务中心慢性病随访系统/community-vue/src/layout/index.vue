<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-content">
        <div class="header-title">
          <h2>社区卫生服务中心慢性病随访系统</h2>
        </div>
        <div class="user-info">
          <el-icon class="user-icon"><User /></el-icon>
          <span class="user-name">{{ userInfo.name }}</span>
          <el-button type="text" class="logout-btn" @click="logout">退出登录</el-button>
        </div>
      </div>
    </el-header>
    <el-container class="layout-body">
      <el-aside width="220px" class="layout-aside">
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
          background-color="#ffffff"
          text-color="#606266"
          active-text-color="#409eff"
        >
          <template v-if="userRole === 'admin'">
            <el-menu-item index="/department">
              <el-icon><OfficeBuilding /></el-icon>
              <span>科室管理</span>
            </el-menu-item>
            <el-menu-item index="/doctor">
              <el-icon><UserFilled /></el-icon>
              <span>医生管理</span>
            </el-menu-item>
            <el-menu-item index="/patient">
              <el-icon><Avatar /></el-icon>
              <span>患者管理</span>
            </el-menu-item>
            <el-menu-item index="/medicine">
              <el-icon><Box /></el-icon>
              <span>药品管理</span>
            </el-menu-item>
            <el-menu-item index="/medical-record">
              <el-icon><Document /></el-icon>
              <span>诊疗记录录入</span>
            </el-menu-item>
            <el-menu-item index="/followup-task">
              <el-icon><List /></el-icon>
              <span>随访任务分配</span>
            </el-menu-item>
            <el-menu-item index="/statistics">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据统计</span>
            </el-menu-item>
            <el-menu-item index="/system-settings">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
          </template>
          <template v-else-if="userRole === 'doctor'">
            <el-menu-item index="/doctor-patient">
              <el-icon><Avatar /></el-icon>
              <span>患者管理</span>
            </el-menu-item>
            <el-menu-item index="/doctor-followup-task">
              <el-icon><List /></el-icon>
              <span>随访任务查看</span>
            </el-menu-item>
            <el-menu-item index="/doctor-followup-record">
              <el-icon><EditPen /></el-icon>
              <span>随访记录</span>
            </el-menu-item>
            <el-menu-item index="/personal-center">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, UserFilled, OfficeBuilding, Avatar, Box, Document, List, EditPen, DataAnalysis, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const userInfo = ref({
  name: localStorage.getItem('userName') || '管理员'
})

const userRole = ref(localStorage.getItem('userRole') || 'admin')

const activeMenu = computed(() => route.path)

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  localStorage.removeItem('userRole')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  height: 64px !important;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
  z-index: 1000;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-icon {
  font-size: 18px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.logout-btn {
  color: #fff !important;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.layout-body {
  flex: 1;
  overflow: hidden;
}

.layout-aside {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.layout-aside::-webkit-scrollbar {
  display: none;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #f5f7fa;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background-color: #409eff;
  border-radius: 0 2px 2px 0;
}

.sidebar-menu :deep(.el-icon) {
  margin-right: 8px;
  font-size: 18px;
}

.layout-main {
  background-color: #f5f7fa;
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}
</style>
