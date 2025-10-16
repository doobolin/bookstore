import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import { ElMessage } from 'element-plus'

// 导入管理页面组件
import HomeView from '../views/HomeView.vue'
import BookManageView from '../views/BookManageView.vue'
import UserManageView from '../views/UserManageView.vue'
import OrderManageView from '../views/OrderManageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'book-manage',
          name: 'bookManage',
          component: BookManageView,
          meta: { requiresAuth: true }
        },
        {
          path: 'user-manage',
          name: 'userManage',
          component: UserManageView,
          meta: { requiresAuth: true }
        },
        {
          path: 'order-manage',
          name: 'orderManage',
          component: OrderManageView,
          meta: { requiresAuth: true }
        }
      ]
    }
  ]
})

// 路由守卫，确保只有登录后才能访问管理页面，且只有管理员可以访问
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 模拟检查登录状态（实际项目中应检查token等）
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userRole = localStorage.getItem('role');
    
    if (!isLoggedIn) {
      // 未登录，跳转到登录页
      next({
        name: 'login'
      })
    } else if (userRole !== 'admin') {
      // 已登录但不是管理员角色，拒绝访问
      ElMessage.error('普通用户不能访问管理系统');
      // 清除登录信息并返回登录页
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('role');
      localStorage.removeItem('isLoggedIn');
      next({
        name: 'login'
      })
    } else {
      // 已登录且是管理员，继续访问
      next()
    }
  } else {
    // 不需要登录的页面，直接访问
    next()
  }
})

export default router