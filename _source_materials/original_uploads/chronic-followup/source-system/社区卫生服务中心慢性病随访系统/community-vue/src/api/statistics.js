import request from '@/utils/request'

export function getStatistics() {
  return request({
    url: '/api/statistics',
    method: 'get'
  })
}
