<template>
  <div class="app-shell">
    <header class="app-header">
      <span class="brand">乐背 · 后台管理</span>
      <nav class="app-nav" aria-label="主导航">
        <RouterLink class="nav-link" to="/leaderboard">排行榜</RouterLink>
        <RouterLink class="nav-link" to="/profile">个人中心</RouterLink>
      </nav>
      <button type="button" class="btn-text" @click="onLogout">退出登录</button>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { setToken } from "../api/client";

const router = useRouter();

function onLogout() {
  setToken(null);
  router.replace("/login");
}
</script>
