import axios from "axios";

/** Web 管理端专用，与 App 用户 token 隔离 */
const TOKEN_KEY = "lebei_admin_token";

export const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export interface UserProfile {
  id: number;
  username: string;
  ageGroup: number | null;
  level: string | null;
  currentBookId: string | null;
  profileComplete: boolean;
  dailyNewWords: number;
  dailyReviewWords: number;
  learnedWordsCount: number;
  masteredWordsCount: number;
  role?: string;
}

export interface AuthResponse {
  token: string;
  user: UserProfile;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  learnedWordsCount: number;
  masteredWordsCount: number;
  studyPoints: number;
  todayLearnedCount: number;
}
