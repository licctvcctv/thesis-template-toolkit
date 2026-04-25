import http from 'node:http'
import { URL } from 'node:url'

const PORT = 8088

const now = '2026-04-24 10:30:00'

const users = [
  { id: 1, username: 'admin', phone: '13800000000', nickname: '系统管理员', gender: 1, email: 'admin@parking.local', role: 'ADMIN', status: 1, createTime: '2026-04-01 09:00:00' },
  { id: 2, username: 'testuser', phone: '13800000001', nickname: '演示用户', gender: 1, email: 'test@example.com', role: 'USER', status: 1, createTime: '2026-04-03 10:12:00' },
  { id: 3, username: 'zhangsan', phone: '13900001001', nickname: '张三', gender: 1, email: 'zhangsan@example.com', role: 'USER', status: 1, createTime: '2026-04-06 11:18:00' },
  { id: 4, username: 'lisi', phone: '13900001002', nickname: '李四', gender: 1, email: 'lisi@example.com', role: 'USER', status: 1, createTime: '2026-04-08 15:22:00' },
  { id: 5, username: 'wangwu', phone: '13900001003', nickname: '王五', gender: 2, email: 'wangwu@example.com', role: 'USER', status: 1, createTime: '2026-04-10 13:36:00' },
  { id: 6, username: 'wujiu', phone: '13900001007', nickname: '吴九', gender: 2, email: 'wujiu@example.com', role: 'USER', status: 0, createTime: '2026-04-13 08:30:00' }
]

const lots = [
  { id: 1, name: '人民广场智慧停车场', address: '上海市黄浦区人民大道100号', longitude: 121.47519, latitude: 31.228833, totalSpaces: 128, availableSpaces: 46, hourlyRate: 8.00, openTime: '00:00', closeTime: '23:59', contactPhone: '021-63210001', images: '', status: 1, createTime: '2026-04-05 10:00:00' },
  { id: 2, name: '陆家嘴中心停车场', address: '上海市浦东新区陆家嘴环路1000号', longitude: 121.506377, latitude: 31.245105, totalSpaces: 160, availableSpaces: 62, hourlyRate: 10.00, openTime: '07:00', closeTime: '23:00', contactPhone: '021-58880002', images: '', status: 1, createTime: '2026-04-06 10:30:00' },
  { id: 3, name: '静安寺地下停车场', address: '上海市静安区南京西路1686号', longitude: 121.444309, latitude: 31.224361, totalSpaces: 96, availableSpaces: 18, hourlyRate: 9.00, openTime: '08:00', closeTime: '22:00', contactPhone: '021-62480003', images: '', status: 1, createTime: '2026-04-07 09:10:00' },
  { id: 4, name: '徐家汇商圈停车场', address: '上海市徐汇区肇嘉浜路1111号', longitude: 121.43757, latitude: 31.195556, totalSpaces: 150, availableSpaces: 75, hourlyRate: 6.00, openTime: '06:00', closeTime: '23:30', contactPhone: '021-64260004', images: '', status: 1, createTime: '2026-04-08 09:50:00' },
  { id: 5, name: '虹桥火车站P6停车场', address: '上海市闵行区申贵路1500号', longitude: 121.31962, latitude: 31.1946, totalSpaces: 220, availableSpaces: 95, hourlyRate: 5.00, openTime: '00:00', closeTime: '23:59', contactPhone: '021-51050005', images: '', status: 1, createTime: '2026-04-09 14:05:00' },
  { id: 6, name: '南京东路地下停车场', address: '上海市黄浦区南京东路800号', longitude: 121.48732, latitude: 31.23719, totalSpaces: 118, availableSpaces: 20, hourlyRate: 12.00, openTime: '07:00', closeTime: '22:00', contactPhone: '021-63220006', images: '', status: 1, createTime: '2026-04-10 11:15:00' },
  { id: 7, name: '世纪公园停车场', address: '上海市浦东新区锦绣路1001号', longitude: 121.55125, latitude: 31.2148, totalSpaces: 80, availableSpaces: 50, hourlyRate: 4.00, openTime: '06:00', closeTime: '22:00', contactPhone: '021-58900007', images: '', status: 1, createTime: '2026-04-11 16:20:00' },
  { id: 8, name: '已关闭的测试停车场', address: '上海市宝山区牡丹江路1800号', longitude: 121.4502, latitude: 31.3806, totalSpaces: 50, availableSpaces: 0, hourlyRate: 5.00, openTime: '08:00', closeTime: '20:00', contactPhone: '021-56100013', images: '', status: 0, createTime: '2026-04-12 10:00:00' }
]

const spaces = [
  { id: 1, lotId: 1, lotName: '人民广场智慧停车场', spaceCode: 'A-001', floor: 'B1-A区', spaceType: 'NORMAL', status: 0, createTime: now },
  { id: 2, lotId: 1, lotName: '人民广场智慧停车场', spaceCode: 'A-002', floor: 'B1-A区', spaceType: 'NORMAL', status: 2, createTime: now },
  { id: 3, lotId: 1, lotName: '人民广场智慧停车场', spaceCode: 'A-003', floor: 'B1-A区', spaceType: 'ACCESSIBLE', status: 0, createTime: now },
  { id: 4, lotId: 1, lotName: '人民广场智慧停车场', spaceCode: 'B-001', floor: 'B1-B区', spaceType: 'VIP', status: 1, createTime: now },
  { id: 5, lotId: 1, lotName: '人民广场智慧停车场', spaceCode: 'B-002', floor: 'B1-B区', spaceType: 'LARGE', status: 0, createTime: now },
  { id: 6, lotId: 1, lotName: '人民广场智慧停车场', spaceCode: 'M-001', floor: 'B2-M区', spaceType: 'NORMAL', status: 3, createTime: now },
  { id: 7, lotId: 2, lotName: '陆家嘴中心停车场', spaceCode: 'L-001', floor: 'B2-L区', spaceType: 'NORMAL', status: 0, createTime: now },
  { id: 8, lotId: 2, lotName: '陆家嘴中心停车场', spaceCode: 'L-002', floor: 'B2-L区', spaceType: 'NORMAL', status: 0, createTime: now },
  { id: 9, lotId: 2, lotName: '陆家嘴中心停车场', spaceCode: 'V-001', floor: 'B1-V区', spaceType: 'VIP', status: 1, createTime: now },
  { id: 10, lotId: 4, lotName: '徐家汇商圈停车场', spaceCode: 'A-001', floor: 'B1-A区', spaceType: 'NORMAL', status: 0, createTime: now },
  { id: 11, lotId: 4, lotName: '徐家汇商圈停车场', spaceCode: 'A-002', floor: 'B1-A区', spaceType: 'NORMAL', status: 0, createTime: now },
  { id: 12, lotId: 4, lotName: '徐家汇商圈停车场', spaceCode: 'B-003', floor: 'B2-B区', spaceType: 'VIP', status: 2, createTime: now }
]

const vehicles = [
  { id: 1, userId: 2, plateNumber: '沪A12345', vehicleType: 'SMALL', vehicleColor: '白色', vehicleBrand: '演示车辆', isDefault: 1, createTime: '2026-04-12 09:30:00' },
  { id: 2, userId: 2, plateNumber: '沪B88888', vehicleType: 'SMALL', vehicleColor: '黑色', vehicleBrand: '特斯拉 Model 3', isDefault: 0, createTime: '2026-04-16 15:02:00' }
]

const orders = [
  { id: 1, orderNo: 'PK20260424100001', userId: 2, username: 'testuser', vehicleId: 1, plateNumber: '沪A12345', lotId: 1, lotName: '人民广场智慧停车场', spaceId: 2, spaceCode: 'A-002', reserveTime: '2026-04-24 09:15:00', expireTime: '2026-04-24 09:45:00', enterTime: null, exitTime: null, durationMinutes: null, hourlyRate: 8.00, amount: null, status: 0, payStatus: 0, createTime: '2026-04-24 09:15:00' },
  { id: 2, orderNo: 'PK20260424100002', userId: 3, username: 'zhangsan', vehicleId: 3, plateNumber: '沪A66666', lotId: 4, lotName: '徐家汇商圈停车场', spaceId: 12, spaceCode: 'B-003', reserveTime: '2026-04-24 08:50:00', expireTime: '2026-04-24 09:20:00', enterTime: '2026-04-24 09:03:00', exitTime: null, durationMinutes: null, hourlyRate: 6.00, amount: null, status: 1, payStatus: 0, createTime: '2026-04-24 08:50:00' },
  { id: 3, orderNo: 'PK20260423100011', userId: 4, username: 'lisi', vehicleId: 4, plateNumber: '沪D22222', lotId: 2, lotName: '陆家嘴中心停车场', spaceId: 9, spaceCode: 'V-001', reserveTime: '2026-04-23 14:10:00', expireTime: '2026-04-23 14:40:00', enterTime: '2026-04-23 14:22:00', exitTime: '2026-04-23 16:02:00', durationMinutes: 100, hourlyRate: 10.00, amount: 20.00, status: 2, payStatus: 0, createTime: '2026-04-23 14:10:00' },
  { id: 4, orderNo: 'PK20260422100009', userId: 2, username: 'testuser', vehicleId: 1, plateNumber: '沪A12345', lotId: 5, lotName: '虹桥火车站P6停车场', spaceId: 18, spaceCode: 'P6-006', reserveTime: '2026-04-22 10:20:00', expireTime: '2026-04-22 10:50:00', enterTime: '2026-04-22 10:34:00', exitTime: '2026-04-22 13:15:00', durationMinutes: 161, hourlyRate: 5.00, amount: 15.00, status: 3, payStatus: 1, createTime: '2026-04-22 10:20:00' },
  { id: 5, orderNo: 'PK20260421200003', userId: 5, username: 'wangwu', vehicleId: 7, plateNumber: '沪F44444', lotId: 6, lotName: '南京东路地下停车场', spaceId: 45, spaceCode: 'N-001', reserveTime: '2026-04-21 19:20:00', expireTime: '2026-04-21 19:50:00', cancelTime: '2026-04-21 19:42:00', durationMinutes: null, hourlyRate: 12.00, amount: null, status: 4, payStatus: 0, cancelReason: '用户主动取消', createTime: '2026-04-21 19:20:00' }
]

const logs = [
  { id: 1, operatorId: 1, operator: 'admin', operateType: 'LOGIN', module: '系统登录', content: '管理员登录系统', requestMethod: 'POST', requestUrl: '/api/public/auth/login', ip: '127.0.0.1', createTime: '2026-04-24 09:00:00' },
  { id: 2, operatorId: 1, operator: 'admin', operateType: 'INSERT', module: '停车场管理', content: '新增停车场：人民广场智慧停车场', requestMethod: 'POST', requestUrl: '/api/admin/parking-lot', ip: '127.0.0.1', createTime: '2026-04-23 15:30:00' },
  { id: 3, operatorId: 1, operator: 'admin', operateType: 'UPDATE', module: '车位管理', content: '批量修改车位状态', requestMethod: 'PUT', requestUrl: '/api/admin/parking-space/batch-status', ip: '127.0.0.1', createTime: '2026-04-23 16:04:00' },
  { id: 4, operatorId: 1, operator: 'admin', operateType: 'UPDATE', module: '订单管理', content: '手动出场：订单PK20260423100011', requestMethod: 'PUT', requestUrl: '/api/admin/order/3/exit', ip: '127.0.0.1', createTime: '2026-04-23 16:02:00' }
]

const configs = [
  { id: 1, configKey: 'reserve_timeout_minutes', configValue: '30', description: '预约锁定时长（分钟）', createTime: now, updateTime: now },
  { id: 2, configKey: 'default_hourly_rate', configValue: '5.00', description: '默认收费标准（元/小时）', createTime: now, updateTime: now },
  { id: 3, configKey: 'max_vehicles_per_user', configValue: '5', description: '每用户最多绑定车辆数', createTime: now, updateTime: now },
  { id: 4, configKey: 'system_notice', configValue: '欢迎使用城市智慧停车系统', description: '系统公告', createTime: now, updateTime: now }
]

function ok(data) {
  return { code: 200, message: 'success', data }
}

function page(records, params) {
  const size = Number(params.get('size') || params.get('pageSize') || 10)
  const current = Number(params.get('page') || 1)
  const start = (current - 1) * size
  return { records: records.slice(start, start + size), total: records.length, current, size }
}

function readBody(req) {
  return new Promise(resolve => {
    let body = ''
    req.on('data', chunk => { body += chunk })
    req.on('end', () => {
      try { resolve(body ? JSON.parse(body) : {}) } catch { resolve({}) }
    })
  })
}

function findLot(id) {
  return lots.find(item => item.id === Number(id)) || lots[0]
}

async function route(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`)
  const path = url.pathname.replace(/^\/api/, '')
  const params = url.searchParams

  if (req.method === 'OPTIONS') return send(res, 204)

  if (path === '/public/auth/login' && req.method === 'POST') {
    const body = await readBody(req)
    const isAdmin = String(body.username || '').toLowerCase().includes('admin')
    const userInfo = isAdmin ? users[0] : users[1]
    return sendJson(res, ok({ token: `${isAdmin ? 'admin' : 'user'}-mock-token`, userInfo }))
  }

  if (path === '/public/auth/register' && req.method === 'POST') {
    return sendJson(res, ok({ id: 8, username: 'newuser' }))
  }

  if (path === '/public/parking-lot/list') {
    let data = [...lots]
    const keyword = params.get('keyword')
    if (keyword) data = data.filter(item => item.name.includes(keyword) || item.address.includes(keyword))
    if (params.get('status') !== null) data = data.filter(item => item.status === Number(params.get('status')))
    if (params.get('hasSpace') === 'true') data = data.filter(item => item.availableSpaces > 0)
    if (params.get('sortBy') === 'price') data.sort((a, b) => a.hourlyRate - b.hourlyRate)
    if (params.get('sortBy') === 'available') data.sort((a, b) => b.availableSpaces - a.availableSpaces)
    return sendJson(res, ok(page(data, params)))
  }

  if (path === '/public/parking-lot/nearby') {
    return sendJson(res, ok(lots.filter(item => item.status === 1).slice(0, 6)))
  }

  const lotDetail = path.match(/^\/public\/parking-lot\/(\d+)$/)
  if (lotDetail) return sendJson(res, ok(findLot(lotDetail[1])))

  const lotSpaces = path.match(/^\/public\/parking-lot\/(\d+)\/spaces$/)
  if (lotSpaces) return sendJson(res, ok(spaces.filter(item => item.lotId === Number(lotSpaces[1]))))

  if (path === '/user/profile') return sendJson(res, ok(users[1]))
  if (path === '/user/vehicle/list') return sendJson(res, ok(vehicles))
  if (path === '/user/order/list') return sendJson(res, ok(page(orders.filter(item => item.userId === 2), params)))

  const userOrderDetail = path.match(/^\/user\/order\/(\d+)$/)
  if (userOrderDetail) return sendJson(res, ok(orders.find(item => item.id === Number(userOrderDetail[1])) || orders[0]))

  const findCar = path.match(/^\/user\/order\/(\d+)\/find-car$/)
  if (findCar) return sendJson(res, ok({ lotName: '人民广场智慧停车场', floor: 'B1-A区', spaceCode: 'A-002', address: '上海市黄浦区人民大道100号' }))

  if (path === '/user/order/reserve' && req.method === 'POST') return sendJson(res, ok(orders[0]))
  if (/^\/user\/order\/\d+\/(cancel|enter)$/.test(path)) return sendJson(res, ok(true))
  if (path === '/user/payment/pay') return sendJson(res, ok({ id: 1, orderNo: orders[2].orderNo, amount: 20.00, payMethod: 'ALIPAY', payTime: now, status: 1 }))
  if (/^\/user\/payment\/\d+$/.test(path)) return sendJson(res, ok({ id: 1, orderNo: orders[2].orderNo, amount: 20.00, payMethod: 'ALIPAY', payTime: now, status: 1 }))

  if (path === '/admin/dashboard/summary') return sendJson(res, ok({ todayRevenue: 168.00, revenueChange: 12.5, todayOrders: 18, orderChange: 8.0, activeVehicles: 36, totalUsers: users.length }))
  if (path === '/admin/dashboard/revenue-trend') return sendJson(res, ok([
    { date: '2026-04-18', value: 96 }, { date: '2026-04-19', value: 132 }, { date: '2026-04-20', value: 118 },
    { date: '2026-04-21', value: 156 }, { date: '2026-04-22', value: 145 }, { date: '2026-04-23', value: 188 }, { date: '2026-04-24', value: 168 }
  ]))
  if (path === '/admin/dashboard/order-trend') return sendJson(res, ok([
    { date: '2026-04-18', value: 11 }, { date: '2026-04-19', value: 16 }, { date: '2026-04-20', value: 15 },
    { date: '2026-04-21', value: 18 }, { date: '2026-04-22', value: 17 }, { date: '2026-04-23', value: 21 }, { date: '2026-04-24', value: 18 }
  ]))
  if (path === '/admin/dashboard/lot-usage') return sendJson(res, ok(lots.slice(0, 6).map(item => ({ name: item.name, usage: Math.round((1 - item.availableSpaces / item.totalSpaces) * 100) }))))
  if (path === '/admin/dashboard/order-status') return sendJson(res, ok([
    { status: '已预约', count: 5 }, { status: '进行中', count: 8 }, { status: '待支付', count: 3 }, { status: '已完成', count: 28 }, { status: '已取消', count: 4 }
  ]))

  if (path === '/admin/parking-lot/list') return sendJson(res, ok(page(lots, params)))
  if (/^\/admin\/parking-lot\/\d+$/.test(path)) return sendJson(res, ok(findLot(path.split('/').pop())))
  if (path === '/admin/parking-lot' || /^\/admin\/parking-lot\/\d+$/.test(path)) return sendJson(res, ok(true))

  if (path === '/admin/parking-space/list') return sendJson(res, ok(page(spaces, params)))
  if (path === '/admin/parking-space' || path === '/admin/parking-space/batch' || path === '/admin/parking-space/batch-status' || /^\/admin\/parking-space\/\d+$/.test(path)) return sendJson(res, ok(true))

  if (path === '/admin/order/list') return sendJson(res, ok(page(orders, params)))
  const adminOrderDetail = path.match(/^\/admin\/order\/(\d+)$/)
  if (adminOrderDetail) return sendJson(res, ok(orders.find(item => item.id === Number(adminOrderDetail[1])) || orders[0]))
  if (/^\/admin\/order\/\d+\/(enter|exit|remark)$/.test(path)) return sendJson(res, ok(true))
  if (path === '/admin/order/export') return send(res, 200, 'order_no,plate_number,lot_name\nPK20260424100001,沪A12345,人民广场智慧停车场\n', 'text/csv')

  if (path === '/admin/user/list') return sendJson(res, ok(page(users, params)))
  const adminUserDetail = path.match(/^\/admin\/user\/(\d+)$/)
  if (adminUserDetail) return sendJson(res, ok(users.find(item => item.id === Number(adminUserDetail[1])) || users[1]))
  if (/^\/admin\/user\/\d+\/(reset-password|status)$/.test(path)) return sendJson(res, ok(true))

  if (path === '/admin/log/list') return sendJson(res, ok(page(logs, params)))
  if (path === '/admin/config/list') return sendJson(res, ok(configs))
  if (/^\/admin\/config\/.+$/.test(path)) return sendJson(res, ok(true))
  if (path === '/common/upload') return sendJson(res, ok('/mock-upload/parking-lot.png'))

  return sendJson(res, { code: 404, message: `mock endpoint not found: ${path}`, data: null }, 404)
}

function corsHeaders(type = 'application/json; charset=utf-8') {
  return {
    'Content-Type': type,
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization,Content-Type'
  }
}

function send(res, status, body = '', type = 'text/plain; charset=utf-8') {
  res.writeHead(status, corsHeaders(type))
  res.end(body)
}

function sendJson(res, payload, status = 200) {
  send(res, status, JSON.stringify(payload), 'application/json; charset=utf-8')
}

const server = http.createServer((req, res) => {
  route(req, res).catch(err => {
    console.error(err)
    sendJson(res, { code: 500, message: err.message, data: null }, 500)
  })
})

server.listen(PORT, '127.0.0.1', () => {
  console.log(`mock api listening on http://127.0.0.1:${PORT}/api`)
})
