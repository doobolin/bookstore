import axiosInstance from './axiosInstance'

// 定义图书接口
export interface Book {
  id: number
  title: string
  author: string
  category: string
  category_id?: number
  description: string
  price: string | number
  rating: number
  image: string
  stock?: number
  isbn?: string
  status?: string
  created_at?: string
  updated_at?: string
}

// 定义分类接口
export interface Category {
  id: number
  name: string
  description?: string
}

// 获取所有图书
export const getAllBooks = async (): Promise<Book[]> => {
  try {
    const response = await axiosInstance.get('/books')
    // 检查响应格式并返回图书数据
    if (response && response.data && Array.isArray(response.data.books)) {
      return response.data.books
    }
    return []
  } catch (error) {
    console.error('获取图书列表失败:', error)
    throw error
  }
}

// 根据ID获取图书详情
export const getBookById = async (id: number): Promise<Book | null> => {
  try {
    const response = await axiosInstance.get(`/books/${id}`)
    if (response && response.code === 200 && response.data) {
      return response.data
    }
    return null
  } catch (error) {
    console.error('获取图书详情失败:', error)
    throw error
  }
}

// 获取所有分类
export const getAllCategories = async (): Promise<Category[]> => {
  try {
    const response = await axiosInstance.get('/categories')
    if (response && response.data && Array.isArray(response.data.categories)) {
      return response.data.categories
    }
    return []
  } catch (error) {
    console.error('获取分类列表失败:', error)
    throw error
  }
}

// 搜索图书参数接口
export interface SearchBooksParams {
  q?: string        // 搜索关键词
  category?: string // 分类筛选
}

// 搜索图书
export const searchBooks = async (params: SearchBooksParams): Promise<Book[]> => {
  try {
    const response = await axiosInstance.get('/books/search', {
      params: params
    })
    if (response && response.data && Array.isArray(response.data.books)) {
      return response.data.books
    }
    return []
  } catch (error) {
    console.error('搜索图书失败:', error)
    throw error
  }
}
