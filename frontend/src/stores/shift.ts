/**
 * 班次状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { shiftApi } from '../api'

export interface Shift {
  id: number
  name: string
  start_time: string
  end_time: string
  color: string
  is_active: boolean
  required_count: number
}

export const useShiftStore = defineStore('shift', () => {
  // 状态
  const shifts = ref<Shift[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeShifts = computed(() =>
    shifts.value.filter(s => s.is_active)
  )

  const shiftOptions = computed(() =>
    shifts.value.map(s => ({
      label: s.name,
      value: s.id
    }))
  )

  // 方法
  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const res = await shiftApi.getAll()
      shifts.value = res.data
    } catch (e: any) {
      error.value = e.message || '获取班次列表失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: Partial<Shift>) {
    const res = await shiftApi.create(data)
    shifts.value.push(res.data)
    return res.data
  }

  async function update(id: number, data: Partial<Shift>) {
    const res = await shiftApi.update(id, data)
    const index = shifts.value.findIndex(s => s.id === id)
    if (index !== -1) {
      shifts.value[index] = res.data
    }
    return res.data
  }

  async function remove(id: number) {
    await shiftApi.delete(id)
    shifts.value = shifts.value.filter(s => s.id !== id)
  }

  function getById(id: number) {
    return shifts.value.find(s => s.id === id)
  }

  return {
    // 状态
    shifts,
    loading,
    error,
    // 计算属性
    activeShifts,
    shiftOptions,
    // 方法
    fetchAll,
    create,
    update,
    remove,
    getById
  }
})
