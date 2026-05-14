import request from '@/utils/request'

export function getMedicalRecordList(params) {
  return request({
    url: '/api/medical-record/list',
    method: 'get',
    params
  })
}

export function getMedicalRecordById(id) {
  return request({
    url: `/api/medical-record/${id}`,
    method: 'get'
  })
}

export function addMedicalRecord(data) {
  return request({
    url: '/api/medical-record/add',
    method: 'post',
    data
  })
}

export function updateMedicalRecord(data) {
  return request({
    url: '/api/medical-record/update',
    method: 'put',
    data
  })
}

export function deleteMedicalRecord(id) {
  return request({
    url: `/api/medical-record/${id}`,
    method: 'delete'
  })
}

export function getMedicalRecordStatistics(params) {
  return request({
    url: '/api/medical-record/statistics',
    method: 'get',
    params
  })
}
