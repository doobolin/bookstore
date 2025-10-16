import axios from 'axios'

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: '/api', // 后端API基础地址（通过Vite代理转发）
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 添加token等认证信息
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    // 统一处理响应数据格式
    return response.data
  },
  (error) => {
    // 统一错误处理
    console.error('API请求错误:', error)
    if (error.response) {
      // 服务器返回错误状态码
      console.error('错误状态码:', error.response.status)
      console.error('错误信息:', error.response.data)
    } else if (error.request) {
      // 请求发出但没有收到响应
      console.error('网络错误，服务器无响应')
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
