import request from '@/utils/request'

export function getDoctorAssignmentList(params) {
  return request({
    url: '/api/doctor-assignment/list',
    method: 'get',
    params
  })
}

export function getDoctorAssignmentById(id) {
  return request({
    url: `/api/doctor-assignment/${id}`,
    method: 'get'
  })
}

export function assignDoctor(params) {
  return request({
    url: '/api/doctor-assignment/assign',
    method: 'post',
    params
  })
}
