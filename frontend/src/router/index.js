import { createRouter, createWebHistory } from 'vue-router'
import AuthPanel from '../components/AuthPanel.vue'
import UserDashboard from '../components/UserDashboard.vue'
import AdminDashboard from '../components/AdminDashboard.vue'
import AdminQuizzes from '../components/AdminQuizzes.vue'
import QuizWindow from '../components/QuizWindow.vue'
import UserSummary from '../components/UserSummary.vue'
import AdminSummary from '../components/AdminSummary.vue'

const routes = [
  { path: '/', component: AuthPanel },
  { path: '/user/dashboard', component: UserDashboard },
  { path: '/admin/dashboard', component: AdminDashboard },
  { path: '/admin/quizzes', component: AdminQuizzes },
  { path: '/user/quiz', component: QuizWindow },
  { path: '/user/summary', component: UserSummary },
  { path: '/admin/summary', component: AdminSummary }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const role = localStorage.getItem('role')

  if (to.path.startsWith('/admin') && (!token || role !== 'admin')) {
    return next('/')
  }
  if (to.path.startsWith('/user') && (!token || role !== 'user')) {
    return next('/')
  }

  next()
})


export default router
