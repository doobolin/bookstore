import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import BookDetail from '../components/BookDetail.vue'
import OrderList from '../components/OrderList.vue'
import OrderDetail from '../components/OrderDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/book/:id',
    name: 'bookDetail',
    component: BookDetail,
    props: true
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: OrderList
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: OrderDetail,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router