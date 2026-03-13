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
        <el-form-item label="班组">
          <el-select v-model="queryParams.team_id" placeholder="选择班组" clearable style="width: 150px">
            <el-option v-for="team in teams" :key="team.id" :label="team.name" :value="team.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="queryParams = { start_date: null, end_date: null, employee_name: '', team_id: null }">重置</el-button>
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
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑排班" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="员工">
          <el-select v-model="editForm.employee_id" placeholder="选择员工" style="width: 100%">
            <el-option v-for="emp in employees" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班次">
          <el-select v-model="editForm.shift_id" placeholder="选择班次" style="width: 100%">
            <el-option v-for="shift in shifts" :key="shift.id" :label="shift.name" :value="shift.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="editForm.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleApi, employeeApi, shiftApi, teamApi } from '../api'

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
const selectedIds = ref([])
const queryParams = ref({
  start_date: null,
  end_date: null,
  employee_name: '',
  team_id: null
})

// 分页相关
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})

// 编辑相关
const editDialogVisible = ref(false)
const editForm = ref({
  id: null,
  employee_id: null,
  shift_id: null,
  date: null
})
const employees = ref([])
const shifts = ref([])
const teams = ref([])

const loadData = async () => {
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size
    }
    if (queryParams.value.start_date) params.start_date = queryParams.value.start_date
    if (queryParams.value.end_date) params.end_date = queryParams.value.end_date

    const [schedRes, empRes, shiftRes, teamRes] = await Promise.all([
      scheduleApi.getAll(params),
      employeeApi.getAll(),
      shiftApi.getAll(),
      teamApi.getAll()
    ])

    // 后端返回分页数据结构
    const items = schedRes.data.items
    pagination.value.total = schedRes.data.total
    employees.value = empRes.data
    shifts.value = shiftRes.data
    teams.value = teamRes.data

    // 客户端过滤员工名称
    applyFilter(items)
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const applyFilter = (items) => {
  // 员工名称过滤在客户端进行，因为后端只支持 employee_id 过滤
  if (!queryParams.value.employee_name) {
    schedules.value = items || []
    return
  }
  const keyword = queryParams.value.employee_name.toLowerCase()
  schedules.value = (items || []).filter(s =>
    s.employee_name?.toLowerCase().includes(keyword)
  )
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadData()
}

const handleSizeChange = (size) => {
  pagination.value.page_size = size
  pagination.value.page = 1
  loadData()
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
    const params = {
      start_date: queryParams.value.start_date,
      end_date: queryParams.value.end_date,
      clear_existing: true
    }
    if (queryParams.value.team_id) {
      params.team_id = queryParams.value.team_id
    }
    await scheduleApi.generate(params)
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

const handleEdit = (row) => {
  editForm.value = {
    id: row.id,
    employee_id: row.employee_id,
    shift_id: row.shift_id,
    date: row.date
  }
  editDialogVisible.value = true
}

const handleEditSubmit = async () => {
  try {
    await scheduleApi.update(editForm.value.id, {
      employee_id: editForm.value.employee_id,
      shift_id: editForm.value.shift_id,
      date: editForm.value.date
    })
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
