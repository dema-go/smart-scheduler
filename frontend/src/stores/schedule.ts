/**
 * 排班状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { scheduleApi } from '../api'

export interface Schedule {
  id: number
  employee_id: number
  shift_type_id: number
  date: string
  employee_name?: string
  shift_name?: string
  shift_color?: string
}

export interface PaginatedSchedules {
  items: Schedule[]
  total: number
  page: number
  page_size: number
}

export const useScheduleStore = defineStore('schedule', () => {
  // 状态
  const schedules = ref<Schedule[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const generating = ref(false)
  const error = ref<string | null>(null)

  // 方法
  async function fetchAll(params: {
    start_date?: string
    end_date?: string
    employee_id?: number
    page?: number
    page_size?: number
  } = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await scheduleApi.getAll({
        page: params.page || page.value,
        page_size: params.page_size || pageSize.value,
        ...params
      })
      schedules.value = res.data.items
      total.value = res.data.total
      page.value = res.data.page
      pageSize.value = res.data.page_size
    } catch (e: any) {
      error.value = e.message || '获取排班列表失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: Partial<Schedule>) {
    const res = await scheduleApi.create(data)
    return res.data
  }

  async function update(id: number, data: Partial<Schedule>) {
    const res = await scheduleApi.update(id, data)
    const index = schedules.value.findIndex(s => s.id === id)
    if (index !== -1) {
      schedules.value[index] = { ...schedules.value[index], ...res.data }
    }
    return res.data
  }

  async function remove(id: number) {
    await scheduleApi.delete(id)
    schedules.value = schedules.value.filter(s => s.id !== id)
    total.value -= 1
  }

  async function batchRemove(ids: number[]) {
    await scheduleApi.batchDelete(ids)
    schedules.value = schedules.value.filter(s => !ids.includes(s.id))
    total.value -= ids.length
  }

  async function generate(params: {
    start_date: string
    end_date: string
    team_id?: number
    clear_existing?: boolean
  }) {
    generating.value = true
    error.value = null
    try {
      const res = await scheduleApi.generate(params)
      return res.data
    } catch (e: any) {
      error.value = e.message || '生成排班失败'
      throw e
    } finally {
      generating.value = false
    }
  }

  async function exportSchedules(params: {
    start_date?: string
    end_date?: string
    format?: string
  }) {
    const res = await scheduleApi.export(params)
    return res.data
  }

  async function getStats(params: {
    type: string
    year: number
    month?: number
    week?: number
  }) {
    const res = await scheduleApi.getStats(params)
    return res.data
  }

  return {
    // 状态
    schedules,
    total,
    page,
    pageSize,
    loading,
    generating,
    error,
    // 方法
    fetchAll,
    create,
    update,
    remove,
    batchRemove,
    generate,
    exportSchedules,
    getStats
  }
})
