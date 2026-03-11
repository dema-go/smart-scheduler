<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-title">
        <el-icon size="24"><Calendar /></el-icon>
        <span>智能排班系统</span>
      </div>
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        router
        class="header-menu"
      >
        <el-menu-item index="/dashboard">首页</el-menu-item>
        <el-menu-item index="/schedules">排班管理</el-menu-item>
        <el-menu-item index="/schedules/calendar">日历视图</el-menu-item>
        <el-menu-item index="/employees">员工管理</el-menu-item>
        <el-menu-item index="/shifts">班次管理</el-menu-item>
        <el-menu-item index="/preferences">偏好设置</el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-menu {
  border-bottom: none !important;
}

.app-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
