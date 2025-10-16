import axiosInstance from './axiosInstance'

// 定义图书计数响应接口
export interface BooksCountResponse {
  total: number
  totalStock: number
}

// 定义图书接口
export interface Book {
  id: number
  title: string
  author: string
  price: number
  stock: number
  isbn?: string
  category?: string
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

// 添加图书
export const addBook = async (bookData: {
  title: string
  author: string
  price: number
  stock: number
  isbn?: string
  category_id?: number
  description?: string
}): Promise<Book> => {
  try {
    const response = await axiosInstance.post('/books', bookData)
    return response.data
  } catch (error) {
    console.error('添加图书失败:', error)
    throw error
  }
}

// 更新图书
export const updateBook = async (
  id: number,
  bookData: {
    title?: string
    author?: string
    price?: number
    stock?: number
    isbn?: string
    category_id?: number
    description?: string
  }
): Promise<Book> => {
  try {
    const response = await axiosInstance.put(`/books/${id}`, bookData)
    return response.data
  } catch (error) {
    console.error('更新图书失败:', error)
    throw error
  }
}

// 删除图书
export const deleteBook = async (id: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/books/${id}`)
  } catch (error) {
    console.error('删除图书失败:', error)
    throw error
  }
}

// 获取图书总数
 export const getBooksCount = async (): Promise<BooksCountResponse> => {
  try {
    console.log('调用getBooksCount开始')
    const response = await axiosInstance.get('/books/count')
    console.log('getBooksCount响应数据:', response)
    return response.data
  } catch (error) {
    console.error('获取图书总数失败:', error)
    console.error('错误类型:', error instanceof Error ? error.name : typeof error)
    console.error('错误详细信息:', error instanceof Error ? error.message : JSON.stringify(error))
    throw error
  }
}

// 定义低库存图书响应接口
export interface LowStockResponse {
  books: Book[]
  total: number
}

// 获取低库存图书（库存低于20本的图书）
export const getLowStockBooks = async (): Promise<LowStockResponse> => {
  try {
    const response = await axiosInstance.get('/books/low-stock')
    return response.data
  } catch (error) {
    console.error('获取低库存图书失败:', error)
    throw error
  }
}