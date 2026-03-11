import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import EmployeesView from './views/EmployeesView.vue'
import ShiftsView from './views/ShiftsView.vue'
import SchedulesView from './views/SchedulesView.vue'
import SchedulesCalendarView from './views/SchedulesCalendarView.vue'

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
  },
  {
    path: '/schedules/calendar',
    name: 'schedules-calendar',
    component: SchedulesCalendarView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
