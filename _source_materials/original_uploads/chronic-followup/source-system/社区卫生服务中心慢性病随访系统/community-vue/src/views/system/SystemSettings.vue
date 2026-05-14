<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="个人信息管理" name="info">
          <el-form
            ref="infoFormRef"
            :model="userInfo"
            :rules="infoRules"
            label-width="120px"
            style="max-width: 600px; margin-top: 20px;"
          >
            <el-form-item label="用户名">
              <el-input v-model="userInfo.username" disabled />
            </el-form-item>
            <el-form-item label="姓名" prop="name">
              <el-input v-model="userInfo.name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="角色">
              <el-input v-model="userInfo.role" disabled />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateInfo">保存</el-button>
              <el-button @click="handleResetInfo">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="密码修改" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="120px"
            style="max-width: 600px; margin-top: 20px;"
          >
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入原密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
              <el-button @click="handleResetPassword">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCurrentUser, updateUserInfo, changePassword } from '@/api/user'

const activeTab = ref('info')
const infoFormRef = ref(null)
const passwordFormRef = ref(null)

const userInfo = reactive({
  id: null,
  username: '',
  name: '',
  role: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const infoRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const loadUserInfo = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      ElMessage.error('用户ID不存在')
      return
    }
    const res = await getCurrentUser(userId)
    Object.assign(userInfo, res.data)
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

const handleUpdateInfo = async () => {
  try {
    await infoFormRef.value.validate()
    const userId = localStorage.getItem('userId')
    await updateUserInfo(userId, { name: userInfo.name })
    ElMessage.success('更新成功')
    localStorage.setItem('userName', userInfo.name)
    // 刷新页面用户信息显示
    window.location.reload()
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}

const handleResetInfo = () => {
  loadUserInfo()
}

const handleChangePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    const userId = localStorage.getItem('userId')
    await changePassword(userId, {
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功，请重新登录')
    // 清空表单
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    // 延迟跳转到登录页
    setTimeout(() => {
      localStorage.clear()
      window.location.href = '/login'
    }, 1500)
  } catch (error) {
    ElMessage.error(error.message || '密码修改失败')
  }
}

const handleResetPassword = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordFormRef.value?.clearValidate()
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.system-settings {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
