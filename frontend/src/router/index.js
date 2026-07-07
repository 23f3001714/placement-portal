import { createRouter, createWebHistory } from 'vue-router'

import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import RegisterStudent from '../views/RegisterStudent.vue'
import RegisterCompany from '../views/RegisterCompany.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import CompanyDetails from '../views/CompanyDetails.vue'
import JobDetails from '../views/JobDetails.vue'
import StudentPage from '../views/StudentPage.vue'
import ViewApplication from '../views/ApplicationDetails.vue'
import CompanyJobDetails from '../views/CompanyJobDetails.vue'
import CompanyApplicationDetails from '../views/CompanyApplicationDetails.vue'
import CompanyPlacementDetails from '../views/CompanyPlacementDetails.vue'
import StudentApplicationDetails from '../views/StudentApplicationDetails.vue'
import StudentJobDetails from '../views/StudentJobDetails.vue'

const protectedRoute = (role) => ({
  requiresAuth: true,
  role
})

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/register/student',
    name: 'register-student',
    component: RegisterStudent
  },
  {
    path: '/register/company',
    name: 'register-company',
    component: RegisterCompany
  },
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: protectedRoute('admin')
  },
  {
    path: '/student/dashboard',
    name: 'student-dashboard',
    component: StudentDashboard,
    meta: protectedRoute('student')
  },
  {
    path: '/company/dashboard',
    name: 'company-dashboard',
    component: CompanyDashboard,
    meta: protectedRoute('company')
  },
  {
    path: '/admin/company/:id',
    name: 'company-details',
    component: CompanyDetails,
    meta: protectedRoute('admin')
  },
  {
    path: '/admin/job/:id',
    name: 'job-details',
    component: JobDetails,
    meta: protectedRoute('admin')
  },
  {
    path: '/admin/student/:id',
    name: 'student-details',
    component: StudentPage,
    meta: protectedRoute('admin')
  },
  {
    path: '/admin/application/:id',
    name: 'application-details',
    component: ViewApplication,
    meta: protectedRoute('admin')
  },
  {
    path: '/company/job/:id',
    name: 'company-job-details',
    component: CompanyJobDetails,
    meta: protectedRoute('company')
  },
  {
    path: '/company/application/:id',
    name: 'company-application-details',
    component: CompanyApplicationDetails,
    meta: protectedRoute('company')
  },
  {
    path: '/company/placement/:id',
    name: 'company-placement-details',
    component: CompanyPlacementDetails,
    meta: protectedRoute('company')
  },
  {
    path: '/student/job/:id',
    name: 'student-job-details',
    component: StudentJobDetails,
    meta: protectedRoute('student')
  },
  {
    path: '/student/application/:id',
    name: 'student-application-details',
    component: StudentApplicationDetails,
    meta: protectedRoute('student')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next()
  }

  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  const authenticated = Boolean(token)
  const authorized = role === to.meta.role

  if (!authenticated || !authorized) {
    return next({ name: 'login' })
  }

  next()
})

export default router