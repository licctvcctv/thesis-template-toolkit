<template>
  <div class="auth-view">
    <div class="card">
      <h1>管理员登录</h1>
      <p class="muted">
        此处仅用于<strong>后台管理员</strong>登录，与 Android App 注册用户<strong>不是同一套账号</strong>。默认管理员在首次启动后端时写入数据库，见服务端
        <code>application.yml</code> 中 <code>lebei.admin</code> 配置。
      </p>
      <div v-if="error" class="error">{{ error }}</div>
      <form @submit.prevent="submit">
        <label>管理员用户名</label>
        <input v-model="username" autocomplete="username" />
        <label>密码</label>
        <input v-model="password" type="password" autocomplete="current-password" />
        <button class="primary" type="submit" :disabled="loading">登录</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, setToken, type AuthResponse } from "../api/client";

const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    const { data } = await api.post<AuthResponse>("/admin/auth/login", {
      username: username.value.trim(),
      password: password.value,
    });
    setToken(data.token);
    const raw = route.query.redirect as string | undefined;
    const redirect =
      raw && raw !== "/login" ? raw : { name: "leaderboard" as const };
    await router.replace(redirect);
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { message?: string } } };
    error.value = ax.response?.data?.message || "登录失败";
  } finally {
    loading.value = false;
  }
}
</script>
