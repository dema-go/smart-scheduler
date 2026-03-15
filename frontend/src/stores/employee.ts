/**
 * 员工状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { employeeApi } from '../api'

export interface Employee {
  id: number
  name: string
  position: string | null
  phone: string | null
  email: string | null
  is_active: boolean
  team_id: number | null
  team_name: string | null
  available_days: number[]
  preferred_shifts: number[]
}

export const useEmployeeStore = defineStore('employee', () => {
  // 状态
  const employees = ref<Employee[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeEmployees = computed(() =>
    employees.value.filter(e => e.is_active)
  )

  const employeeOptions = computed(() =>
    employees.value.map(e => ({
      label: e.name,
      value: e.id
    }))
  )

  // 方法
  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const res = await employeeApi.getAll()
      employees.value = res.data
    } catch (e: any) {
      error.value = e.message || '获取员工列表失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: Partial<Employee>) {
    const res = await employeeApi.create(data)
    employees.value.push(res.data)
    return res.data
  }

  async function update(id: number, data: Partial<Employee>) {
    const res = await employeeApi.update(id, data)
    const index = employees.value.findIndex(e => e.id === id)
    if (index !== -1) {
      employees.value[index] = res.data
    }
    return res.data
  }

  async function remove(id: number) {
    await employeeApi.delete(id)
    employees.value = employees.value.filter(e => e.id !== id)
  }

  function getById(id: number) {
    return employees.value.find(e => e.id === id)
  }

  return {
    // 状态
    employees,
    loading,
    error,
    // 计算属性
    activeEmployees,
    employeeOptions,
    // 方法
    fetchAll,
    create,
    update,
    remove,
    getById
  }
})
