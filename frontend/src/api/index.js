import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 员工 API
export const employeeApi = {
  getAll: () => api.get('/employees'),
  getById: (id) => api.get(`/employees/${id}`),
  create: (data) => api.post('/employees', data),
  update: (id, data) => api.put(`/employees/${id}`, data),
  delete: (id) => api.delete(`/employees/${id}`)
}

// 班次 API
export const shiftApi = {
  getAll: () => api.get('/shifts'),
  getById: (id) => api.get(`/shifts/${id}`),
  create: (data) => api.post('/shifts', data),
  update: (id, data) => api.put(`/shifts/${id}`, data),
  delete: (id) => api.delete(`/shifts/${id}`)
}

// 排班 API
export const scheduleApi = {
  getAll: (params) => api.get('/schedules', { params }),
  getById: (id) => api.get(`/schedules/${id}`),
  create: (data) => api.post('/schedules', data),
  update: (id, data) => api.put(`/schedules/${id}`, data),
  delete: (id) => api.delete(`/schedules/${id}`),
  generate: (params) => api.post('/schedules/generate', null, { params }),
  clear: (params) => api.delete('/schedules/clear', { params }),
  export: (params) => api.get('/schedules/export', { params, responseType: 'blob' })
}

export default api
