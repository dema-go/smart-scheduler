<template>
  <div class="preferences-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工排班偏好设置</span>
        </div>
      </template>

      <el-alert
        title="设置说明"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #default>
          在此页面设置您的可用工作时间和偏好班次。智能排班算法会根据您的偏好进行优化排班。
        </template>
      </el-alert>

      <el-form :model="form" label-width="100px" v-loading="loading">
        <el-form-item label="选择员工">
          <el-select v-model="form.employee_id" placeholder="请选择员工" @change="handleEmployeeChange" style="width: 300px">
            <el-option v-for="emp in employees" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-form-item>

        <template v-if="form.employee_id">
          <el-divider content-position="left">可用工作时间</el-divider>

          <el-form-item label="可用日期">
            <el-checkbox-group v-model="form.available_days">
              <el-checkbox :label="0">周一</el-checkbox>
              <el-checkbox :label="1">周二</el-checkbox>
              <el-checkbox :label="2">周三</el-checkbox>
              <el-checkbox :label="3">周四</el-checkbox>
              <el-checkbox :label="4">周五</el-checkbox>
              <el-checkbox :label="5">周六</el-checkbox>
              <el-checkbox :label="6">周日</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="可用时间">
            <el-time-select
              v-model="form.available_start_time"
              placeholder="开始时间"
              start="06:00"
              step="00:30"
              end="22:00"
              style="width: 150px; margin-right: 10px"
            />
            <span style="margin: 0 10px">至</span>
            <el-time-select
              v-model="form.available_end_time"
              placeholder="结束时间"
              start="06:00"
              step="00:30"
              end="22:00"
              style="width: 150px"
            />
          </el-form-item>

          <el-divider content-position="left">班次偏好</el-divider>

          <el-form-item label="偏好班次">
            <el-select v-model="form.preferred_shifts" multiple placeholder="选择偏好班次" style="width: 400px">
              <el-option v-for="shift in shifts" :key="shift.id" :label="shift.name" :value="shift.id">
                <span :style="{ color: shift.color }">{{ shift.name }}</span>
                <span style="float: right; color: #999; font-size: 12px">
                  {{ shift.start_time }} - {{ shift.end_time }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="偏好说明">
            <el-input
              v-model="form.preference_note"
              type="textarea"
              :rows="3"
              placeholder="添加任何额外的偏好说明，如：不希望连续上晚班、希望周末休息等"
              style="width: 400px"
            />
          </el-form-item>

          <el-divider content-position="left">当前设置预览</el-divider>

          <div class="preview-section">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="员工姓名">
                {{ currentEmployee?.name }}
              </el-descriptions-item>
              <el-descriptions-item label="职位">
                {{ currentEmployee?.position || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="可用日期">
                <el-tag v-for="day in formatDays(form.available_days)" :key="day" size="small" style="margin-right: 4px">
                  {{ day }}
                </el-tag>
                <span v-if="!form.available_days?.length" style="color: #999">未设置</span>
              </el-descriptions-item>
              <el-descriptions-item label="可用时间">
                {{ form.available_start_time && form.available_end_time ? `${form.available_start_time} - ${form.available_end_time}` : '未设置' }}
              </el-descriptions-item>
              <el-descriptions-item label="偏好班次" :span="2">
                <el-tag v-for="shiftId in form.preferred_shifts" :key="shiftId" size="small" :color="getShiftColor(shiftId)" style="margin-right: 4px; color: #fff">
                  {{ getShiftName(shiftId) }}
                </el-tag>
                <span v-if="!form.preferred_shifts?.length" style="color: #999">未设置</span>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <el-form-item>
            <el-button type="primary" @click="handleSave" :loading="saving">保存偏好设置</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </template>

        <el-empty v-if="!form.employee_id" description="请先选择员工" />
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { employeeApi, shiftApi } from '../api'

const loading = ref(false)
const saving = ref(false)
const employees = ref([])
const shifts = ref([])

const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const form = ref({
  employee_id: null,
  available_days: [],
  available_start_time: '09:00',
  available_end_time: '18:00',
  preferred_shifts: [],
  preference_note: ''
})

const currentEmployee = computed(() => {
  return employees.value.find(e => e.id === form.value.employee_id)
})

const formatDays = (days) => {
  if (!days || !Array.isArray(days)) return []
  return days.map(d => dayNames[d]).filter(Boolean)
}

const getShiftName = (shiftId) => {
  const shift = shifts.value.find(s => s.id === shiftId)
  return shift?.name || ''
}

const getShiftColor = (shiftId) => {
  const shift = shifts.value.find(s => s.id === shiftId)
  return shift?.color || '#409EFF'
}

const loadData = async () => {
  loading.value = true
  try {
    const [empRes, shiftRes] = await Promise.all([
      employeeApi.getAll(),
      shiftApi.getAll()
    ])
    employees.value = empRes.data
    shifts.value = shiftRes.data
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleEmployeeChange = async (employeeId) => {
  if (!employeeId) return

  loading.value = true
  try {
    const res = await employeeApi.getById(employeeId)
    const emp = res.data
    form.value.available_days = emp.available_days || []
    form.value.preferred_shifts = emp.preferred_shifts || []
    // 偏好设置存储在扩展字段中
    form.value.preference_note = emp.preference_note || ''
    form.value.available_start_time = emp.available_start_time || '09:00'
    form.value.available_end_time = emp.available_end_time || '18:00'
  } catch (error) {
    ElMessage.error('获取员工信息失败')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!form.value.employee_id) {
    ElMessage.warning('请先选择员工')
    return
  }

  if (!form.value.available_days?.length) {
    ElMessage.warning('请至少选择一个可用日期')
    return
  }

  saving.value = true
  try {
    await employeeApi.update(form.value.employee_id, {
      available_days: form.value.available_days,
      preferred_shifts: form.value.preferred_shifts,
      preference_note: form.value.preference_note,
      available_start_time: form.value.available_start_time,
      available_end_time: form.value.available_end_time
    })
    ElMessage.success('偏好设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleReset = () => {
  if (form.value.employee_id) {
    handleEmployeeChange(form.value.employee_id)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.preferences-view {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-section {
  margin-bottom: 20px;
}
</style>
