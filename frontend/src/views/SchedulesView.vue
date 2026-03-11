<template>
  <div class="schedules-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排班管理</span>
          <div class="header-actions">
            <el-button
              type="danger"
              :disabled="selectedIds.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>批量删除 ({{ selectedIds.length }})
            </el-button>
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
        <el-form-item label="员工">
          <el-input v-model="queryParams.employee_name" placeholder="搜索员工" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="queryParams = { start_date: null, end_date: null, employee_name: '' }">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        ref="tableRef"
        :data="schedules"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="员工" width="120">
          <template #default="{ row }">
            {{ row.employee_name }}
          </template>
        </el-table-column>
        <el-table-column label="班次" width="120">
          <template #default="{ row }">
            <el-tag :style="{ backgroundColor: row.shift_color, color: getTextColor(row.shift_color) }">
              {{ row.shift_name }}
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleApi } from '../api'

// 根据背景色计算文字颜色（深色背景用白色文字，浅色背景用黑色文字）
const getTextColor = (color) => {
  if (!color) return '#000000'
  // 去掉 # 前缀
  const hex = color.replace('#', '')
  // 解析 RGB
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  // 计算亮度 (使用标准公式)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  return brightness > 128 ? '#000000' : '#ffffff'
}

const tableRef = ref(null)
const schedules = ref([])
const allSchedules = ref([])
const selectedIds = ref([])
const queryParams = ref({
  start_date: null,
  end_date: null,
  employee_name: ''
})

const loadData = async () => {
  try {
    const params = {}
    if (queryParams.value.start_date) params.start_date = queryParams.value.start_date
    if (queryParams.value.end_date) params.end_date = queryParams.value.end_date

    const schedRes = await scheduleApi.getAll(params)
    allSchedules.value = schedRes.data
    applyFilter()
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const applyFilter = () => {
  if (!queryParams.value.employee_name) {
    schedules.value = allSchedules.value
    return
  }
  const keyword = queryParams.value.employee_name.toLowerCase()
  schedules.value = allSchedules.value.filter(s =>
    s.employee_name?.toLowerCase().includes(keyword)
  )
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleGenerate = async () => {
  try {
    if (!queryParams.value.start_date || !queryParams.value.end_date) {
      ElMessage.warning('请选择开始和结束日期')
      return
    }
    await scheduleApi.generate({
      start_date: queryParams.value.start_date,
      end_date: queryParams.value.end_date,
      clear_existing: true
    })
    ElMessage.success('排班生成成功')
    loadData()
  } catch (error) {
    ElMessage.error('生成失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleExport = async () => {
  try {
    // 过滤掉空值
    const params = {}
    if (queryParams.value.start_date) params.start_date = queryParams.value.start_date
    if (queryParams.value.end_date) params.end_date = queryParams.value.end_date

    const res = await scheduleApi.export(params)
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
    await ElMessageBox.confirm(`确定要删除 ${row.employee_name} 的排班吗?`, '提示', { type: 'warning' })
    await scheduleApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的排班')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条排班记录吗?`,
      '批量删除确认',
      { type: 'warning' }
    )

    await scheduleApi.batchDelete(selectedIds.value)
    ElMessage.success(`成功删除 ${selectedIds.value.length} 条排班记录`)
    selectedIds.value = []
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败: ' + (error.response?.data?.detail || error.message))
    }
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
