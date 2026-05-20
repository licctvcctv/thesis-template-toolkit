<template>
  <div>
    <h1>管理员个人中心</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="user" class="card" style="max-width: 640px">
      <p><strong>用户名</strong>：{{ user.username }}</p>
      <p><strong>角色</strong>：{{ roleLabel(user.role) }}</p>
      <p><strong>管理员 ID</strong>：{{ user.id }}</p>
      <p class="muted">
        管理员账号用于登录本 Web 端；学习数据、词库计划等属于 App 用户，请在排行榜中查看学员同步情况。
      </p>
      <button class="primary" type="button" @click="refresh" :disabled="loading">刷新</button>
    </div>
    <p v-else-if="!loading" class="muted">无法加载资料</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, type UserProfile } from "../api/client";

const user = ref<UserProfile | null>(null);
const loading = ref(true);
const error = ref("");

function roleLabel(role: string | undefined) {
  if (role === "ADMIN") return "管理员";
  if (role === "APP_USER") return "App 用户";
  return role || "—";
}

async function refresh() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get<UserProfile>("admin/me");
    user.value = data;
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { message?: string } } };
    error.value = ax.response?.data?.message || "加载失败";
  } finally {
    loading.value = false;
  }
}

onMounted(refresh);
</script>
