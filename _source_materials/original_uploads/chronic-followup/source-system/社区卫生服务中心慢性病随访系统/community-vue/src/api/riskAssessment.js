import request from '@/utils/request'

export function getRiskAssessmentList(params) {
  return request({
    url: '/api/risk-assessment/list',
    method: 'get',
    params
  })
}

export function getRiskAssessmentById(id) {
  return request({
    url: `/api/risk-assessment/${id}`,
    method: 'get'
  })
}

export function addRiskAssessment(data) {
  return request({
    url: '/api/risk-assessment/add',
    method: 'post',
    data
  })
}

export function getRiskLevelConfigs() {
  return request({
    url: '/api/risk-level-config/enabled',
    method: 'get'
  })
}
