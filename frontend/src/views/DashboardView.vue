<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409EFF">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.employeeCount }}</div>
              <div class="stat-label">员工总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67C23A">
              <el-icon :size="30"><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.shiftCount }}</div>
              <div class="stat-label">班次类型</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #E6A23C">
              <el-icon :size="30"><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.todayScheduleCount }}</div>
              <div class="stat-label">今日排班</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #F56C6C">
              <el-icon :size="30"><List /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.weekScheduleCount }}</div>
              <div class="stat-label">本周排班</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日排班</span>
          </template>
          <el-table :data="todaySchedules" stripe v-if="todaySchedules.length">
            <el-table-column prop="employee_name" label="员工" />
            <el-table-column label="班次">
              <template #default="{ row }">
                <el-tag :color="row.shift_color" style="color: #fff; border: none;">
                  {{ row.shift_name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="日期" />
          </el-table>
          <el-empty v-else description="今日暂无排班" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/schedules')">
              <el-icon><Calendar /></el-icon>管理排班
            </el-button>
            <el-button type="success" @click="$router.push('/employees')">
              <el-icon><User /></el-icon>管理员工
            </el-button>
            <el-button type="warning" @click="$router.push('/shifts')">
              <el-icon><Clock /></el-icon>管理班次
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>本月员工排班统计</span>
              <el-select v-model="statsYearMonth.year" size="small" style="width: 100px; margin-right: 10px" @change="loadStats">
                <el-option v-for="y in availableYears" :key="y" :label="y + '年'" :value="y" />
              </el-select>
              <el-select v-model="statsYearMonth.month" size="small" style="width: 80px" @change="loadStats">
                <el-option v-for="m in 12" :key="m" :label="m + '月'" :value="m" />
              </el-select>
            </div>
          </template>
          <el-table :data="employeeStats" stripe v-if="employeeStats.length">
            <el-table-column prop="employee_name" label="员工" />
            <el-table-column prop="total_days" label="本月排班天数" width="150" />
            <el-table-column label="班次分布">
              <template #default="{ row }">
                <el-tag v-for="(count, shift) in row.shift_distribution" :key="shift"
                  type="info" style="margin-right: 5px; margin-bottom: 5px;">
                  {{ shift }}: {{ count }}
                </el-tag>
                <span v-if="Object.keys(row.shift_distribution).length === 0" style="color: #909399;">
                  暂无排班
                </span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无员工数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { employeeApi, shiftApi, scheduleApi } from '../api'

const stats = ref({
  employeeCount: 0,
  shiftCount: 0,
  todayScheduleCount: 0,
  weekScheduleCount: 0
})

const todaySchedules = ref([])

// 员工排班统计
const employeeStats = ref([])
const currentYear = new Date().getFullYear()
const statsYearMonth = reactive({
  year: currentYear,
  month: new Date().getMonth() + 1
})
const availableYears = [currentYear - 1, currentYear, currentYear + 1]

const loadStats = async () => {
  try {
    const res = await scheduleApi.getStats(statsYearMonth.year, statsYearMonth.month)
    employeeStats.value = res.data.employees || []
  } catch (error) {
    console.error('加载统计数据失败:', error)
    employeeStats.value = []
  }
}

const loadData = async () => {
  try {
    const today = new Date()
    const todayStr = today.toISOString().split('T')[0]

    const weekEnd = new Date(today)
    weekEnd.setDate(weekEnd.getDate() + 6)
    const weekEndStr = weekEnd.toISOString().split('T')[0]

    const [empRes, shiftRes, schedRes] = await Promise.all([
      employeeApi.getAll(),
      shiftApi.getAll(),
      scheduleApi.getAll({ start_date: todayStr, end_date: weekEndStr })
    ])

    stats.value.employeeCount = empRes.data.length
    stats.value.shiftCount = shiftRes.data.length

    // 今日排班
    const todaySched = schedRes.data.filter(s => s.date === todayStr)
    todaySchedules.value = todaySched
    stats.value.todayScheduleCount = todaySched.length

    // 本周排班
    stats.value.weekScheduleCount = schedRes.data.length
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-actions .el-button {
  width: 100%;
  justify-content: flex-start;
}
</style>
