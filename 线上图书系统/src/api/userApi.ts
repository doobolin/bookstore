import axiosInstance from './axiosInstance'

// 定义登录请求接口
export interface LoginRequest {
  username: string
  password: string
}

// 定义登录响应接口
export interface LoginResponse {
  token: string
  user_id: number
  username: string
  role: string
}

// 定义注册请求接口
export interface RegisterRequest {
  username: string
  email: string
  password: string
}

// 定义用户信息接口
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  created_at?: string
}

// 定义用户资料接口
export interface UserProfile {
  id: number
  username: string
  nickname?: string
  email: string
  phone?: string
  avatar?: string
  gender?: 'male' | 'female' | 'other'
  birthday?: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  created_at?: string
  stats?: {
    total_orders: number
    completed_orders: number
    total_spent: number
  }
}

// 定义用户资料更新接口
export interface UserProfileUpdate {
  nickname?: string
  email?: string
  phone?: string
  avatar?: string
  gender?: 'male' | 'female' | 'other'
  birthday?: string
}

// 定义修改密码接口
export interface PasswordChange {
  old_password: string
  new_password: string
}

// 用户登录
export const loginUser = async (loginData: LoginRequest): Promise<LoginResponse> => {
  try {
    const response = await axiosInstance.post('/login', loginData)
    if (response && response.data) {
      return response.data
    }
    throw new Error('登录失败')
  } catch (error) {
    console.error('登录失败:', error)
    throw error
  }
}

// 用户注册
export const registerUser = async (registerData: RegisterRequest): Promise<User> => {
  try {
    const response = await axiosInstance.post('/register', registerData)
    if (response && response.data) {
      return response.data
    }
    throw new Error('注册失败')
  } catch (error) {
    console.error('注册失败:', error)
    throw error
  }
}

// 检查用户状态
export const checkUserStatus = async (username: string): Promise<{ exists: boolean; status?: 'active' | 'inactive' }> => {
  try {
    const response = await axiosInstance.post('/check-user-status', { username })
    if (response && response.data) {
      return response.data
    }
    return { exists: false }
  } catch (error) {
    console.error('检查用户状态失败:', error)
    throw error
  }
}

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User | null> => {
  try {
    const response = await axiosInstance.get('/user/info')
    if (response && response.data) {
      return response.data
    }
    return null
  } catch (error) {
    console.error('获取用户信息失败:', error)
    throw error
  }
}

// 获取用户完整资料
export const getUserProfile = async (userId: number): Promise<UserProfile> => {
  try {
    const response: any = await axiosInstance.get(`/user/profile/${userId}`)
    if (response && response.data) {
      return response.data
    }
    throw new Error('获取用户资料失败')
  } catch (error) {
    console.error('获取用户资料失败:', error)
    throw error
  }
}

// 更新用户资料
export const updateUserProfile = async (userId: number, profileData: UserProfileUpdate): Promise<void> => {
  try {
    await axiosInstance.put(`/user/profile/${userId}`, profileData)
  } catch (error) {
    console.error('更新用户资料失败:', error)
    throw error
  }
}

// 修改密码
export const changePassword = async (userId: number, passwordData: PasswordChange): Promise<void> => {
  try {
    await axiosInstance.put(`/user/password/${userId}`, passwordData)
  } catch (error) {
    console.error('修改密码失败:', error)
    throw error
  }
}
