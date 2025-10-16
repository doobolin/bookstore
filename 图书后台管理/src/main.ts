import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)
app.mount('#app')

// 添加鼠标点击emoji表情特效
const addEmojiEffect = () => {
  const style = document.createElement('style');
  style.textContent = `
    /* Emoji表情特效样式 */
    .emoji {
      position: fixed;
      font-size: 24px;
      pointer-events: none;
      z-index: 9998;
      animation: emojiAnimation 2s forwards;
      transform: translate(-50%, -50%);
    }
    
    @keyframes emojiAnimation {
      0% {
        transform: translate(-50%, -50%) rotate(0deg) scale(1);
        opacity: 1;
      }
      100% {
        transform: translate(calc(-50% + var(--emoji-offset-x)), calc(-50% - 150px)) rotate(var(--emoji-rotation)) scale(0.5);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
  
  // 定义emoji表情列表
  const emojiList = ['😊', '😂', '😍', '🤔', '😎', '🥰', '🤗', '🤩', '😇', '😜', '💕', '💖'];
  
  // 创建emoji元素的函数
  const createEmoji = (x: number, y: number) => {
    const emojiElement = document.createElement('div');
    emojiElement.className = 'emoji';
    emojiElement.innerText = emojiList[Math.floor(Math.random() * emojiList.length)];
    emojiElement.style.left = `${x}px`;
    emojiElement.style.top = `${y}px`;
    
    // 随机水平偏移和旋转角度
    const offsetX = (Math.random() - 0.5) * 100;
    const rotation = (Math.random() - 0.5) * 180;
    
    emojiElement.style.setProperty('--emoji-offset-x', `${offsetX}px`);
    emojiElement.style.setProperty('--emoji-rotation', `${rotation}deg`);
    
    document.body.appendChild(emojiElement);
    
    // 2秒后移除emoji元素
    setTimeout(() => {
      emojiElement.remove();
    }, 2000);
  };
  
  // 监听鼠标左键点击事件
  document.addEventListener('click', (e) => {
    if (e.button === 0) { // 0表示左键
      // 创建emoji表情
      createEmoji(e.clientX, e.clientY);
    }
  });
};

// 等待DOM加载完成后添加emoji表情特效
document.addEventListener('DOMContentLoaded', addEmojiEffect);
