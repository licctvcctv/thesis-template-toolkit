<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>社区卫生服务中心慢性病随访系统</h2>
        </div>
      </template>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入账号"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'

const router = useRouter()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await login(loginForm)
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('userName', res.data.name)
        localStorage.setItem('userRole', res.data.role)
        localStorage.setItem('userId', res.data.id)
        
        if (loginForm.rememberMe) {
          localStorage.setItem('rememberUsername', loginForm.username)
          localStorage.setItem('rememberPassword', loginForm.password)
        } else {
          localStorage.removeItem('rememberUsername')
          localStorage.removeItem('rememberPassword')
        }
        
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        ElMessage.error(error.message || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const rememberedUsername = localStorage.getItem('rememberUsername')
const rememberedPassword = localStorage.getItem('rememberPassword')
if (rememberedUsername) {
  loginForm.username = rememberedUsername
  loginForm.rememberMe = true
}
if (rememberedPassword) {
  loginForm.password = rememberedPassword
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: url(./bg.png);
  background-size: cover;
  background-position: center;
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.login-card {
  width: 450px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.login-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-bottom: none;
  padding: 30px 20px;
}

.login-card :deep(.el-card__body) {
  padding: 40px 35px;
  background: transparent;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #fff;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.login-card :deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

.login-card :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.login-card :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.login-card :deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.login-card :deep(.el-checkbox__label) {
  color: #606266;
  font-size: 14px;
}

.login-card :deep(.el-button--primary) {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  border-radius: 8px;
  height: 45px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
  transition: all 0.3s ease;
}

.login-card :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.5);
}

.login-card :deep(.el-button--primary:active) {
  transform: translateY(0);
}

.login-card :deep(.el-form-item) {
  margin-bottom: 25px;
}

.login-card :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}
</style>
