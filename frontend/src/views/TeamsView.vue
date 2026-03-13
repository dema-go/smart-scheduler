<template>
  <div class="teams-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班组管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>添加班组
          </el-button>
        </div>
      </template>

      <el-form inline>
        <el-form-item label="搜索">
          <el-input v-model="searchText" placeholder="搜索班组名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="searchText = ''; loadData()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="filteredTeams" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="班组名称" width="200" />
        <el-table-column prop="description" label="描述" min-width="250" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班组' : '添加班组'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="班组名称">
          <el-input v-model="form.name" placeholder="请输入班组名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入班组描述" />
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { teamApi } from '../api'

const teams = ref([])
const searchText = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  name: '',
  description: ''
})

const filteredTeams = computed(() => {
  if (!searchText.value) return teams.value
  const keyword = searchText.value.toLowerCase()
  return teams.value.filter(team =>
    team.name?.toLowerCase().includes(keyword) ||
    team.description?.toLowerCase().includes(keyword)
  )
})

const loadData = async () => {
  try {
    const res = await teamApi.getAll()
    teams.value = res.data
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null,
    name: '',
    description: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await teamApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await teamApi.create(form.value)
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
    await ElMessageBox.confirm(`确定要删除班组 ${row.name} 吗?`, '提示', { type: 'warning' })
    await teamApi.delete(row.id)
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
.teams-view {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
