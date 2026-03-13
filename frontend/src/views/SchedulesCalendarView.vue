<template>
  <div class="schedules-calendar">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排班日历</span>
          <div class="header-actions">
            <el-button type="success" @click="handleGenerate">
              <el-icon><Refresh /></el-icon>智能排班
            </el-button>
          </div>
        </div>
      </template>

      <!-- 月份选择 -->
      <div class="calendar-header">
        <el-button circle @click="prevMonth">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span class="current-month">{{ currentYear }}年{{ currentMonth + 1 }}月</span>
        <el-button circle @click="nextMonth">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button type="primary" plain size="small" @click="goToToday" style="margin-left: 15px">
          今天
        </el-button>
      </div>

      <!-- 班次筛选标签 -->
      <div class="shift-filters">
        <el-tag
          v-for="shift in shifts"
          :key="shift.id"
          :style="{ background: shift.color, borderColor: shift.color, color: '#fff' }"
          :effect="selectedShiftFilter === shift.id ? 'dark' : 'plain'"
          class="shift-tag"
          @click="toggleShiftFilter(shift.id)"
        >
          {{ shift.name }}
        </el-tag>
        <el-tag
          v-if="selectedShiftFilter !== null"
          type="info"
          effect="plain"
          class="shift-tag"
          @click="clearShiftFilter"
        >
          清除筛选
        </el-tag>
      </div>

      <!-- 日历主体 -->
      <div class="calendar-grid">
        <!-- 星期标题 -->
        <div class="weekday-row">
          <div v-for="day in weekDays" :key="day" class="weekday-cell">{{ day }}</div>
        </div>
        
        <!-- 日期格子 -->
        <div class="date-grid">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            class="date-cell"
            :class="{
              'other-month': !day.isCurrentMonth,
              'today': day.isToday
            }"
          >
            <div class="date-number">{{ day.date }}</div>
            <div class="date-shifts">
              <div
                v-for="shift in day.shifts"
                :key="shift.id"
                class="shift-item"
                :style="{ background: shift.shift_color }"
                :title="`${shift.employee_name} - ${shift.shift_name}`"
                @click.stop="showShiftDetail(shift)"
              >
                {{ shift.employee_name }} {{ shift.shift_name }}
              </div>
              <div v-if="day.shifts.length > 3" class="more-shifts">
                +{{ day.shifts.length - 3 }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 智能排班对话框 -->
    <el-dialog v-model="generateDialogVisible" title="智能排班" width="450px">
      <el-form :model="generateForm" label-width="80px">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="generateForm.start_date"
            type="date"
            placeholder="选择开始日期"
            value-format="YYYY-MM-DD"
            :disabled-date="disableBeforeDate"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="generateForm.end_date"
            type="date"
            placeholder="选择结束日期"
            value-format="YYYY-MM-DD"
            :disabled-date="disableBeforeDate"
          />
        </el-form-item>
        <el-form-item label="清除已有">
          <el-switch v-model="generateForm.clear_existing" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerate">生成</el-button>
      </template>
    </el-dialog>

    <!-- 班次详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="班次详情" width="500px">
      <div v-if="selectedShift" class="shift-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="日期">
            {{ selectedShift.date }}
          </el-descriptions-item>
          <el-descriptions-item label="班次">
            <el-tag :color="selectedShift.shift_color" effect="dark">
              {{ selectedShift.shift_name }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="班次时间">
            {{ getShiftTime(selectedShift.shift_type_id) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>员工信息</el-divider>

        <el-descriptions :column="1" border v-if="selectedEmployee">
          <el-descriptions-item label="姓名">
            {{ selectedEmployee.name }}
          </el-descriptions-item>
          <el-descriptions-item label="职位">
            {{ selectedEmployee.position || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="电话">
            {{ selectedEmployee.phone || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ selectedEmployee.email || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="可用天数">
            {{ formatAvailableDays(selectedEmployee.available_days) }}
          </el-descriptions-item>
          <el-descriptions-item label="可用时间">
            {{ selectedEmployee.available_start_time || '-' }} - {{ selectedEmployee.available_end_time || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="偏好班次">
            {{ getPreferredShifts(selectedEmployee.preferred_shifts) }}
          </el-descriptions-item>
          <el-descriptions-item label="偏好说明">
            {{ selectedEmployee.preference_note || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="danger" @click="handleDeleteShift">删除排班</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleApi, employeeApi, shiftApi } from '../api'

const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())

const schedules = ref([])
const employees = ref([])
const shifts = ref([])

// 班次筛选
const selectedShiftFilter = ref(null)

const generateDialogVisible = ref(false)
const generateForm = ref({
  start_date: '',
  end_date: '',
  clear_existing: true
})

// 班次详情相关
const detailDialogVisible = ref(false)
const selectedShift = ref(null)
const selectedEmployee = ref(null)

// 生成日历数据
const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  
  // 获取当月第一天是星期几 (0=周一, 6=周日)
  let startWeekday = firstDay.getDay() - 1
  if (startWeekday < 0) startWeekday = 6
  
  // 上月剩余天数
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  for (let i = startWeekday - 1; i >= 0; i--) {
    const date = prevMonthLastDay - i
    const dateStr = formatDate(new Date(currentYear.value, currentMonth.value - 1, date))
    days.push({
      date,
      dateStr,
      isCurrentMonth: false,
      isToday: false,
      shifts: getShiftsForDate(dateStr)
    })
  }
  
  // 当月天数
  for (let date = 1; date <= lastDay.getDate(); date++) {
    const dateStr = formatDate(new Date(currentYear.value, currentMonth.value, date))
    days.push({
      date,
      dateStr,
      isCurrentMonth: true,
      isToday: isToday(date),
      shifts: getShiftsForDate(dateStr)
    })
  }
  
  // 下月补齐42格
  const remaining = 42 - days.length
  for (let date = 1; date <= remaining; date++) {
    const dateStr = formatDate(new Date(currentYear.value, currentMonth.value + 1, date))
    days.push({
      date,
      dateStr,
      isCurrentMonth: false,
      isToday: false,
      shifts: getShiftsForDate(dateStr)
    })
  }
  
  return days
})

const formatDate = (d) => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const isToday = (date) => {
  return currentYear.value === today.getFullYear() &&
         currentMonth.value === today.getMonth() &&
         date === today.getDate()
}

const getShiftsForDate = (dateStr) => {
  let result = schedules.value.filter(s => s.date === dateStr)
  // 应用班次筛选
  if (selectedShiftFilter.value !== null) {
    result = result.filter(s => s.shift_type_id === selectedShiftFilter.value)
  }
  return result
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const goToToday = () => {
  currentYear.value = today.getFullYear()
  currentMonth.value = today.getMonth()
}

const disableBeforeDate = (time) => {
  return time.getTime() < Date.now() - 86400000
}

const loadData = async () => {
  try {
    // 加载当月数据
    const startDate = formatDate(new Date(currentYear.value, currentMonth.value, 1))
    const endDate = formatDate(new Date(currentYear.value, currentMonth.value + 1, 0))

    // 设置较大的 page_size 以获取当月所有数据
    const [schedRes] = await Promise.all([
      scheduleApi.getAll({ start_date: startDate, end_date: endDate, page: 1, page_size: 1000 })
    ])
    // 后端返回分页数据结构，需要访问 items
    schedules.value = schedRes.data.items || []
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

const loadEmployees = async () => {
  try {
    const res = await employeeApi.getAll()
    employees.value = res.data
  } catch (error) {
    console.error('加载员工数据失败:', error)
    ElMessage.error('加载员工数据失败')
  }
}

const loadShifts = async () => {
  try {
    const res = await shiftApi.getAll()
    shifts.value = res.data
  } catch (error) {
    console.error('加载班次数据失败:', error)
    ElMessage.error('加载班次数据失败')
  }
}

const handleGenerate = () => {
  generateForm.value.start_date = formatDate(new Date())
  const nextWeek = new Date()
  nextWeek.setDate(nextWeek.getDate() + 6)
  generateForm.value.end_date = formatDate(nextWeek)
  generateDialogVisible.value = true
}

const confirmGenerate = async () => {
  try {
    if (!generateForm.value.start_date || !generateForm.value.end_date) {
      ElMessage.warning('请选择开始和结束日期')
      return
    }

    await scheduleApi.generate({
      start_date: generateForm.value.start_date,
      end_date: generateForm.value.end_date,
      clear_existing: generateForm.value.clear_existing
    })

    ElMessage.success('排班生成成功')
    generateDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('生成失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 显示班次详情
const showShiftDetail = (shift) => {
  selectedShift.value = shift
  // 查找对应的员工信息
  selectedEmployee.value = employees.value.find(e => e.id === shift.employee_id)
  detailDialogVisible.value = true
}

// 根据班次类型ID获取班次时间字符串
const getShiftTime = (shiftTypeId) => {
  const shift = shifts.value.find(s => s.id === shiftTypeId)
  if (!shift) return '-'
  return `${shift.start_time} - ${shift.end_time}`
}

// 将数字数组格式化为中文星期字符串
const formatAvailableDays = (availableDays) => {
  if (!availableDays || !Array.isArray(availableDays) || availableDays.length === 0) {
    return '-'
  }
  const weekDayMap = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return availableDays.map(day => weekDayMap[day]).join('、')
}

// 获取偏好班次名称列表
const getPreferredShifts = (preferredShifts) => {
  if (!preferredShifts || !Array.isArray(preferredShifts) || preferredShifts.length === 0) {
    return '-'
  }
  const shiftNames = preferredShifts
    .map(shiftId => {
      const shift = shifts.value.find(s => s.id === shiftId)
      return shift ? shift.name : ''
    })
    .filter(name => name)
  return shiftNames.join('、') || '-'
}

// 删除当前选中的排班
const handleDeleteShift = async () => {
  if (!selectedShift.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除 ${selectedShift.value.employee_name} 在 ${selectedShift.value.date} 的排班吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await scheduleApi.delete(selectedShift.value.id)
    ElMessage.success('删除成功')
    detailDialogVisible.value = false
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 切换班次筛选
const toggleShiftFilter = (shiftId) => {
  if (selectedShiftFilter.value === shiftId) {
    selectedShiftFilter.value = null
  } else {
    selectedShiftFilter.value = shiftId
  }
}

// 清除班次筛选
const clearShiftFilter = () => {
  selectedShiftFilter.value = null
}

// 监听月份变化重新加载
watch(
  () => [currentYear.value, currentMonth.value],
  () => loadData()
)

onMounted(() => {
  loadData()
  loadEmployees()
  loadShifts()
})
</script>

<style scoped>
.schedules-calendar {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.shift-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.shift-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.shift-tag:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.current-month {
  font-size: 18px;
  font-weight: 600;
  margin: 0 20px;
  min-width: 120px;
  text-align: center;
}

.calendar-grid {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.weekday-cell {
  padding: 10px;
  text-align: center;
  font-weight: 600;
  color: #606266;
}

.date-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.date-cell {
  min-height: 100px;
  border-right: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  padding: 5px;
  background: #fff;
}

.date-cell:nth-child(7n) {
  border-right: none;
}

.date-cell.other-month {
  background: #fafafa;
}

.date-cell.other-month .date-number {
  color: #c0c4cc;
}

.date-cell.today {
  background: #ecf5ff;
}

.date-cell.today .date-number {
  color: #409eff;
  font-weight: bold;
}

.date-number {
  font-size: 14px;
  margin-bottom: 5px;
}

.date-shifts {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.shift-item {
  font-size: 11px;
  color: #fff;
  padding: 2px 4px;
  border-radius: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.more-shifts {
  font-size: 11px;
  color: #909399;
  text-align: center;
}
</style>
