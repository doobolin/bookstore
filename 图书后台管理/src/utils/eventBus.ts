import { ref } from 'vue'

// 创建全局事件总线
class EventBus {
  private events: Map<string, Function[]>

  constructor() {
    this.events = new Map()
  }

  // 注册事件监听器
  on(event: string, callback: Function) {
    if (!this.events.has(event)) {
      this.events.set(event, [])
    }
    this.events.get(event)?.push(callback)
  }

  // 触发事件
  emit(event: string, ...args: any[]) {
    if (this.events.has(event)) {
      this.events.get(event)?.forEach(callback => {
        callback(...args)
      })
    }
  }

  // 移除事件监听器
  off(event: string, callback?: Function) {
    if (this.events.has(event)) {
      if (callback) {
        const callbacks = this.events.get(event)
        if (callbacks) {
          const index = callbacks.indexOf(callback)
          if (index > -1) {
            callbacks.splice(index, 1)
          }
        }
      } else {
        this.events.delete(event)
      }
    }
  }
}

// 创建并导出事件总线实例
export const eventBus = new EventBus()

// 定义事件类型
export const EventTypes = {
  NEW_BOOK_ADDED: 'new-book-added',
  BOOK_REMOVED: 'book-removed',
  LOW_STOCK_ALERT: 'low-stock-alert'
}