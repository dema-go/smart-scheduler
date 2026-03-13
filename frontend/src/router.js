import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import EmployeesView from './views/EmployeesView.vue'
import ShiftsView from './views/ShiftsView.vue'
import SchedulesView from './views/SchedulesView.vue'
import SchedulesCalendarView from './views/SchedulesCalendarView.vue'
import TeamsView from './views/TeamsView.vue'
import PreferencesView from './views/PreferencesView.vue'

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
    path: '/teams',
    name: 'teams',
    component: TeamsView
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
  },
  {
    path: '/preferences',
    name: 'preferences',
    component: PreferencesView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
