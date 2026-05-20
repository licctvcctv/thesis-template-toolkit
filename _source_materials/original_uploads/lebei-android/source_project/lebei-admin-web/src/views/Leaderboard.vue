<template>
  <div>
    <h1>App 用户学习排行榜</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="rows.length" class="leaderboard-scroll">
      <table class="leaderboard-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>用户名</th>
            <th>已学习单词数</th>
            <th>掌握词汇</th>
            <th>积分</th>
            <th>今日学习</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.rank + r.username">
            <td>{{ r.rank }}</td>
            <td>{{ r.username }}</td>
            <td>{{ r.learnedWordsCount }}</td>
            <td>{{ r.masteredWordsCount }}</td>
            <td>{{ r.studyPoints }}</td>
            <td>{{ r.todayLearnedCount }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!loading" class="muted">暂无数据</p>
    <p v-if="loading" class="muted">加载中…</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { api, type LeaderboardEntry } from "../api/client";

const rows = ref<LeaderboardEntry[]>([]);
const loading = ref(true);
const error = ref("");

let pollTimer: ReturnType<typeof setInterval> | null = null;

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get<LeaderboardEntry[]>("admin/leaderboard", { params: { limit: 100 } });
    rows.value = data;
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { message?: string } } };
    error.value = ax.response?.data?.message || "加载失败";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  load();
  pollTimer = window.setInterval(load, 5000);
});

onUnmounted(() => {
  if (pollTimer != null) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
});
</script>

<style scoped>
.leaderboard-scroll {
  max-height: calc(2.75rem * 11);
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: #fff;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.leaderboard-table th,
.leaderboard-table td {
  padding: 0.55rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.leaderboard-table thead th {
  position: sticky;
  top: 0;
  background: #f1f3f5;
  z-index: 1;
  font-weight: 600;
}

.leaderboard-table tbody tr:last-child td {
  border-bottom: none;
}
</style>
