import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import Library from '../components/Library.vue'
import BookDetail from '../components/BookDetail.vue'
import Cart from '../components/Cart.vue'
import OrderDetail from '../components/OrderDetail.vue'
import OrderCheckout from '../components/OrderCheckout.vue'
import UserProfile from '../components/UserProfile.vue'

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
    path: '/library',
    name: 'Library',
    component: Library
  },
  {
    path: '/book/:id',
    name: 'bookDetail',
    component: BookDetail,
    props: true
  },
  {
    path: '/cart',
    name: 'Cart',
    component: Cart
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: OrderDetail,
    props: true
  },
  {
    path: '/checkout',
    name: 'OrderCheckout',
    component: OrderCheckout
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router