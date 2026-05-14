import request from '@/utils/request'

export function getFollowupRecordPage(params) {
  return request({
    url: '/api/followup-record/page',
    method: 'get',
    params
  })
}

export function getFollowupRecordById(id) {
  return request({
    url: `/api/followup-record/${id}`,
    method: 'get'
  })
}

export function createFollowupRecord(data) {
  return request({
    url: '/api/followup-record',
    method: 'post',
    data
  })
}

export function updateFollowupRecord(id, data) {
  return request({
    url: `/api/followup-record/${id}`,
    method: 'put',
    data
  })
}

export function deleteFollowupRecord(id) {
  return request({
    url: `/api/followup-record/${id}`,
    method: 'delete'
  })
}

export function exportFollowupRecord(id) {
  return request({
    url: `/api/followup-record/${id}/export`,
    method: 'get'
  })
}
