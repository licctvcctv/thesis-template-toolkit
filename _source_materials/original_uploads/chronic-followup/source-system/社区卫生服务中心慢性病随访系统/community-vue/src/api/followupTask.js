import request from '@/utils/request'

export function getFollowupTaskPage(params) {
  return request({
    url: '/api/followup-task/page',
    method: 'get',
    params
  })
}

export function getFollowupTaskById(id) {
  return request({
    url: `/api/followup-task/${id}`,
    method: 'get'
  })
}

export function createFollowupTask(data) {
  return request({
    url: '/api/followup-task',
    method: 'post',
    data
  })
}

export function updateFollowupTask(id, data) {
  return request({
    url: `/api/followup-task/${id}`,
    method: 'put',
    data
  })
}

export function deleteFollowupTask(id) {
  return request({
    url: `/api/followup-task/${id}`,
    method: 'delete'
  })
}

export function updateFollowupTaskStatus(id, status) {
  return request({
    url: `/api/followup-task/${id}/status`,
    method: 'put',
    params: { status }
  })
}

export function getFollowupTaskStatistics() {
  return request({
    url: '/api/followup-task/statistics',
    method: 'get'
  })
}
