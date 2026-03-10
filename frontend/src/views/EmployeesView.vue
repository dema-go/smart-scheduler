<template>
  <div class="employees-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>添加员工
          </el-button>
        </div>
      </template>

      <el-table :data="employees" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="可用日期" width="150">
          <template #default="{ row }">
            <el-tag v-for="day in formatDays(row.available_days)" :key="day" size="small" style="margin-right: 4px">
              {{ day }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑员工' : '添加员工'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
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
        <el-form-item label="偏好班次">
          <el-select v-model="form.preferred_shifts" multiple placeholder="选择偏好班次">
            <el-option v-for="shift in shifts" :key="shift.id" :label="shift.name" :value="shift.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { employeeApi, shiftApi } from '../api'

const employees = ref([])
const shifts = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  name: '',
  position: '',
  phone: '',
  email: '',
  available_days: [],
  preferred_shifts: []
})

const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const formatDays = (days) => {
  if (!days) return []
  return days.map(d => dayNames[d])
}

const loadData = async () => {
  try {
    const [empRes, shiftRes] = await Promise.all([
      employeeApi.getAll(),
      shiftApi.getAll()
    ])
    employees.value = empRes.data
    shifts.value = shiftRes.data
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null,
    name: '',
    position: '',
    phone: '',
    email: '',
    available_days: [],
    preferred_shifts: []
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row, available_days: row.available_days || [], preferred_shifts: row.preferred_shifts || [] }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await employeeApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await employeeApi.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除员工 ${row.name} 吗?`, '提示', { type: 'warning' })
    await employeeApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.employees-view {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
