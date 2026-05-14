import request from '@/utils/request'

export function getDoctorList(params) {
  return request({
    url: '/api/doctor/list',
    method: 'get',
    params
  })
}

export function getDoctorById(id) {
  return request({
    url: `/api/doctor/${id}`,
    method: 'get'
  })
}

export function getDoctorByUserId(userId) {
  return request({
    url: `/api/doctor/by-user/${userId}`,
    method: 'get'
  })
}

export function addDoctor(data) {
  return request({
    url: '/api/doctor/add',
    method: 'post',
    data
  })
}

export function updateDoctor(data) {
  return request({
    url: '/api/doctor/update',
    method: 'put',
    data
  })
}

export function deleteDoctor(id) {
  return request({
    url: `/api/doctor/${id}`,
    method: 'delete'
  })
}

export function updateDoctorStatus(id, status) {
  return request({
    url: `/api/doctor/status/${id}`,
    method: 'put',
    params: { status }
  })
}
