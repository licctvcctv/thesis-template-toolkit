import request from '@/utils/request'

export function getDepartmentList(params) {
  return request({
    url: '/api/department/list',
    method: 'get',
    params
  })
}

export function getEnabledDepartmentList() {
  return request({
    url: '/api/department/enabled',
    method: 'get'
  })
}

export function getDepartmentById(id) {
  return request({
    url: `/api/department/${id}`,
    method: 'get'
  })
}

export function addDepartment(data) {
  return request({
    url: '/api/department/add',
    method: 'post',
    data
  })
}

export function updateDepartment(data) {
  return request({
    url: '/api/department/update',
    method: 'put',
    data
  })
}

export function deleteDepartment(id) {
  return request({
    url: `/api/department/${id}`,
    method: 'delete'
  })
}
