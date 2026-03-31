import axios from 'axios'

// 创建 axios 实例
const instance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 15000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 在这里可以添加请求前的处理，比如添加 token 等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 在这里可以统一处理错误
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

export default instance 