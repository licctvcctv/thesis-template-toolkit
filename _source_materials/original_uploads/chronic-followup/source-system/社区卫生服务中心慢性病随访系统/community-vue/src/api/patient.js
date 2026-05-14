import request from '@/utils/request'

export function getPatientList(params) {
  return request({
    url: '/api/patient/list',
    method: 'get',
    params
  })
}

export function getPatientById(id) {
  return request({
    url: `/api/patient/${id}`,
    method: 'get'
  })
}

export function addPatient(data) {
  return request({
    url: '/api/patient/add',
    method: 'post',
    data
  })
}

export function updatePatient(data) {
  return request({
    url: '/api/patient/update',
    method: 'put',
    data
  })
}

export function deletePatient(id) {
  return request({
    url: `/api/patient/${id}`,
    method: 'delete'
  })
}

export function exportPatient(params) {
  return new Promise((resolve, reject) => {
    const queryString = new URLSearchParams()
    if (params.name) queryString.append('name', params.name)
    if (params.patientNo) queryString.append('patientNo', params.patientNo)
    if (params.diseaseType) queryString.append('diseaseType', params.diseaseType)
    if (params.riskLevel) queryString.append('riskLevel', params.riskLevel)
    
    const token = localStorage.getItem('token')
    const url = `http://localhost:8080/api/patient/export?${queryString.toString()}`
    
    const xhr = new XMLHttpRequest()
    xhr.open('GET', url, true)
    xhr.setRequestHeader('Authorization', token || '')
    xhr.responseType = 'blob'
    
    xhr.onload = function() {
      if (xhr.status === 200) {
        const blob = xhr.response
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `患者信息_${new Date().toISOString().split('T')[0]}.xlsx`
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(link.href)
        resolve()
      } else {
        reject(new Error('导出失败'))
      }
    }
    
    xhr.onerror = function() {
      reject(new Error('导出失败'))
    }
    
    xhr.send()
  })
}

export function importPatient(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/api/patient/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
