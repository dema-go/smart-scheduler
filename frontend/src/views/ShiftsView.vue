<template>
  <div class="shifts-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班次管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>添加班次
          </el-button>
        </div>
      </template>

      <el-table :data="shifts" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="班次名称" width="120" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column label="颜色" width="100">
          <template #default="{ row }">
            <el-tag :color="row.color" style="color: #fff; border: none;">
              {{ row.color }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="required_count" label="需要人数" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班次' : '添加班次'" width="450px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="班次名称">
          <el-input v-model="form.name" placeholder="如：早班、中班、晚班" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker v-model="startTime" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker v-model="endTime" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="需要人数">
          <el-input-number v-model="form.required_count" :min="1" :max="10" />
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { shiftApi } from '../api'

const shifts = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const startTime = ref('08:00')
const endTime = ref('16:00')
const form = ref({
  id: null,
  name: '',
  start_time: '08:00',
  end_time: '16:00',
  color: '#409EFF',
  required_count: 1
})

const loadData = async () => {
  try {
    const res = await shiftApi.getAll()
    shifts.value = res.data
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleAdd = () => {
  isEdit.value = false
  startTime.value = '08:00'
  endTime.value = '16:00'
  form.value = {
    id: null,
    name: '',
    start_time: '08:00',
    end_time: '16:00',
    color: '#409EFF',
    required_count: 1
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  startTime.value = row.start_time
  endTime.value = row.end_time
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    form.value.start_time = startTime.value
    form.value.end_time = endTime.value

    if (isEdit.value) {
      await shiftApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await shiftApi.create(form.value)
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
    await ElMessageBox.confirm(`确定要删除班次 ${row.name} 吗?`, '提示', { type: 'warning' })
    await shiftApi.delete(row.id)
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
.shifts-view {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
