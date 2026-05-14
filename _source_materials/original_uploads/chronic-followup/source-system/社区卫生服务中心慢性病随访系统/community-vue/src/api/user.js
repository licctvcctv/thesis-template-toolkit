import request from '@/utils/request'

// 获取当前用户信息
export function getCurrentUser(userId) {
  return request({
    url: '/api/user/current',
    method: 'get',
    params: { userId }
  })
}

// 更新用户信息
export function updateUserInfo(userId, data) {
  return request({
    url: '/api/user/info',
    method: 'put',
    params: { userId },
    data
  })
}

// 修改密码
export function changePassword(userId, data) {
  return request({
    url: '/api/user/password',
    method: 'put',
    params: { userId },
    data
  })
}
