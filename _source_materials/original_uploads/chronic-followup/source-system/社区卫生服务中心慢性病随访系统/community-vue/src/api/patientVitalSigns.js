import request from '@/utils/request'

export function getPatientVitalSignsPage(params) {
  return request({
    url: '/api/patient-vital-signs/page',
    method: 'get',
    params
  })
}

export function getPatientVitalSignsById(id) {
  return request({
    url: `/api/patient-vital-signs/${id}`,
    method: 'get'
  })
}

export function getPatientVitalSignsByPatientId(patientId, params) {
  return request({
    url: `/api/patient-vital-signs/patient/${patientId}`,
    method: 'get',
    params
  })
}

export function createPatientVitalSigns(data) {
  return request({
    url: '/api/patient-vital-signs',
    method: 'post',
    data
  })
}

export function updatePatientVitalSigns(id, data) {
  return request({
    url: `/api/patient-vital-signs/${id}`,
    method: 'put',
    data
  })
}

export function deletePatientVitalSigns(id) {
  return request({
    url: `/api/patient-vital-signs/${id}`,
    method: 'delete'
  })
}
