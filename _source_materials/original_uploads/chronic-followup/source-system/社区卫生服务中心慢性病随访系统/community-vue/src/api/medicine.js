import request from '@/utils/request'

export function getMedicineList(params) {
  return request({
    url: '/api/medicine/list',
    method: 'get',
    params
  })
}

export function getMedicineById(id) {
  return request({
    url: `/api/medicine/${id}`,
    method: 'get'
  })
}

export function addMedicine(data) {
  return request({
    url: '/api/medicine/add',
    method: 'post',
    data
  })
}

export function updateMedicine(data) {
  return request({
    url: '/api/medicine/update',
    method: 'put',
    data
  })
}

export function deleteMedicine(id) {
  return request({
    url: `/api/medicine/${id}`,
    method: 'delete'
  })
}
