import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import EmployeesView from './views/EmployeesView.vue'
import ShiftsView from './views/ShiftsView.vue'
import SchedulesView from './views/SchedulesView.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView
  },
  {
    path: '/employees',
    name: 'employees',
    component: EmployeesView
  },
  {
    path: '/shifts',
    name: 'shifts',
    component: ShiftsView
  },
  {
    path: '/schedules',
    name: 'schedules',
    component: SchedulesView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
