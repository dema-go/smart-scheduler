<template>
  <div class="schedules-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排班管理</span>
          <div class="header-actions">
            <el-button type="success" @click="handleGenerate">
              <el-icon><Refresh /></el-icon>智能排班
            </el-button>
            <el-button type="warning" @click="handleExport">
              <el-icon><Download /></el-icon>导出
            </el-button>
          </div>
        </div>
      </template>

      <el-form inline>
        <el-form-item label="开始日期">
          <el-date-picker v-model="queryParams.start_date" type="date" placeholder="选择开始日期" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="queryParams.end_date" type="date" placeholder="选择结束日期" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="schedules" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="员工" width="120">
          <template #default="{ row }">
            {{ getEmployeeName(row.employee_id) }}
          </template>
        </el-table-column>
        <el-table-column label="班次" width="120">
          <template #default="{ row }">
            <el-tag :color="getShiftColor(row.shift_id)">
              {{ getShiftName(row.shift_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { scheduleApi, employeeApi, shiftApi } from '../api'

const schedules = ref([])
const employees = ref([])
const shifts = ref([])
const queryParams = ref({
  start_date: '',
  end_date: ''
})

const loadData = async () => {
  try {
    const [schedRes, empRes, shiftRes] = await Promise.all([
      scheduleApi.getAll(queryParams.value),
      employeeApi.getAll(),
      shiftApi.getAll()
    ])
    schedules.value = schedRes.data
    employees.value = empRes.data
    shifts.value = shiftRes.data
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const getEmployeeName = (id) => {
  const emp = employees.value.find(e => e.id === id)
  return emp ? emp.name : '-'
}

const getShiftName = (id) => {
  const shift = shifts.value.find(s => s.id === id)
  return shift ? shift.name : '-'
}

const getShiftColor = (id) => {
  const shift = shifts.value.find(s => s.id === id)
  return shift ? shift.color : '#909399'
}

const handleGenerate = async () => {
  try {
    if (!queryParams.value.start_date || !queryParams.value.end_date) {
      ElMessage.warning('请选择开始和结束日期')
      return
    }
    await scheduleApi.generate(queryParams.value)
    ElMessage.success('排班生成成功')
    loadData()
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

const handleExport = async () => {
  try {
    const res = await scheduleApi.export(queryParams.value)
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '排班表.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleDelete = async (row) => {
  try {
    await scheduleApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.schedules-view {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
