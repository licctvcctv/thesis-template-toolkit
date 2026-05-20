import { createRouter, createWebHistory } from "vue-router";
import { getToken } from "../api/client";
import MainLayout from "../layouts/MainLayout.vue";
import Login from "../views/Login.vue";
import Leaderboard from "../views/Leaderboard.vue";
import Profile from "../views/Profile.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: { name: "leaderboard" } },
        {
          path: "leaderboard",
          name: "leaderboard",
          component: Leaderboard,
          meta: { requiresAuth: true },
        },
        {
          path: "profile",
          name: "profile",
          component: Profile,
          meta: { requiresAuth: true },
        },
      ],
    },
    { path: "/login", name: "login", component: Login, meta: { guest: true } },
    {
      path: "/:pathMatch(.*)*",
      redirect: () => (getToken() ? { name: "leaderboard" } : { name: "login" }),
    },
  ],
});

router.beforeEach((to) => {
  const token = getToken();
  const needsAuth = to.matched.some((record) => record.meta.requiresAuth === true);
  if (needsAuth && !token) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.guest === true && token) {
    return { name: "leaderboard" };
  }
  return true;
});
