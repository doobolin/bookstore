import axiosInstance from './axiosInstance'

// 定义用户接口
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  created_at?: string
}

// 定义登录请求接口
export interface LoginRequest {
  username: string
  password: string
}

// 定义登录响应接口
export interface LoginResponse {
  token: string
  username: string
  role: string
}

// 定义用户状态查询请求接口
export interface CheckUserStatusRequest {
  username: string
}

// 定义用户状态查询响应接口
export interface CheckUserStatusResponse {
  exists: boolean
  status?: 'active' | 'inactive'
}

// 获取所有用户
export const getAllUsers = async (): Promise<User[]> => {
  try {
    console.log('调用getAllUsers开始')
    const response = await axiosInstance.get('/users')
    console.log('getAllUsers响应数据类型:', typeof response)
    console.log('getAllUsers完整响应数据:', JSON.stringify(response))
    
    // 详细检查响应的每个部分
    console.log('response.code:', response?.code)
    console.log('response.data是否存在:', response?.data !== undefined)
    console.log('response.data.users是否存在:', response?.data?.users !== undefined)
    console.log('response.data.users是否为数组:', Array.isArray(response?.data?.users))
    
    // 检查响应格式并返回用户数据
    if (response && response.code === 200 && response.data && response.data.users && Array.isArray(response.data.users)) {
      console.log('成功获取用户列表，数量:', response.data.users.length)
      return response.data.users
    } else {
      console.error('响应格式不正确，详细信息:')
      console.error('- response存在:', !!response)
      console.error('- response.code为200:', response?.code === 200)
      console.error('- response.data存在:', !!response?.data)
      console.error('- response.data.users存在:', !!response?.data?.users)
      console.error('- response.data.users是数组:', Array.isArray(response?.data?.users))
    }
    return []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    console.error('错误类型:', error instanceof Error ? error.name : typeof error)
    console.error('错误详细信息:', error instanceof Error ? error.message : JSON.stringify(error))
    throw error
  }
}

// 添加用户
export const addUser = async (userData: {
  username: string
  email: string
  password: string
  role: 'admin' | 'user'
}): Promise<User> => {
  try {
    const response = await axiosInstance.post('/users', userData)
    return response.data
  } catch (error) {
    console.error('添加用户失败:', error)
    throw error
  }
}

// 更新用户
export const updateUser = async (
  id: number,
  userData: {
    username?: string
    email?: string
    password?: string
    role?: 'admin' | 'user'
    status?: 'active' | 'inactive'
  }
): Promise<User> => {
  try {
    const response = await axiosInstance.put(`/users/${id}`, userData)
    return response.data
  } catch (error) {
    console.error('更新用户失败:', error)
    throw error
  }
}

// 删除用户
export const deleteUser = async (id: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/users/${id}`)
  } catch (error) {
    console.error('删除用户失败:', error)
    throw error
  }
}

// 切换用户状态（启用/禁用）
export const toggleUserStatus = async (id: number, status: 'active' | 'inactive'): Promise<User> => {
  try {
    const response = await axiosInstance.patch(`/users/${id}/status`, { status })
    return response.data
  } catch (error) {
    console.error('切换用户状态失败:', error)
    throw error
  }
}

// 检查用户表是否存在
export const checkUsersTable = async (): Promise<{
  exists: boolean
  columns?: Array<{
    Field: string
    Type: string
    Null: string
    Key: string
    Default: string | null
    Extra: string
  }>
}> => {
  try {
    const response = await axiosInstance.get('/check-users-table')
    return response.data
  } catch (error) {
    console.error('检查用户表失败:', error)
    throw error
  }
}

// 定义用户计数响应接口
export interface UsersCountResponse {
  total: number
  active: number
  inactive: number
}

// 检查用户状态
export const checkUserStatus = async (username: string): Promise<CheckUserStatusResponse> => {
  try {
    console.log('调用checkUserStatus开始')
    const response = await axiosInstance.post('/check-user-status', { username })
    console.log('checkUserStatus响应数据:', response)
    return response.data
  } catch (error) {
    console.error('检查用户状态失败:', error)
    console.error('错误类型:', error instanceof Error ? error.name : typeof error)
    console.error('错误详细信息:', error instanceof Error ? error.message : JSON.stringify(error))
    throw error
  }
}

// 获取用户总数
export const getUsersCount = async (): Promise<UsersCountResponse> => {
  try {
    console.log('调用getUsersCount开始')
    const response = await axiosInstance.get('/users/count')
    console.log('getUsersCount响应数据:', response)
    return response.data
  } catch (error) {
    console.error('获取用户总数失败:', error)
    console.error('错误类型:', error instanceof Error ? error.name : typeof error)
    console.error('错误详细信息:', error instanceof Error ? error.message : JSON.stringify(error))
    throw error
  }
}

// 用户登录
export const loginUser = async (loginData: LoginRequest): Promise<LoginResponse> => {
  try {
    console.log('调用loginUser开始')
    const response = await axiosInstance.post('/login', loginData)
    console.log('loginUser响应数据:', response)
    return response.data
  } catch (error) {
    console.error('登录失败:', error)
    console.error('错误类型:', error instanceof Error ? error.name : typeof error)
    console.error('错误详细信息:', error instanceof Error ? error.message : JSON.stringify(error))
    throw error
  }
}