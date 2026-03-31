import { createStore } from 'vuex'
import request from './utils/axios'

export default createStore({
  state: {
    projects: [
      {
        id: 1,
        name: 'Defects4J-Math',
        language: 'Java',
        size: '2.4 MB',
        uploadTime: '2023-05-15 14:30',
        status: 'analyzed'
      },
      // 其他项目数据...
    ],
    users: [
      {
        id: 1,
        username: 'admin',
        role: 'admin',
        email: 'admin@testcase.com',
        lastLogin: '2023-05-22 09:30',
        status: 'active'
      },
      // 其他用户数据...
    ],
    dataSources: [
      {
        id: 1,
        name: 'Defects4J Dataset',
        type: 'Excel',
        path: '/data/defects4j.xlsx',
        sheet: 'Projects'
      }
      // 其他数据源...
    ],
    environmentResources: [] // 新增
  },
  /////////////////////////////////////////////合并
  mutations: {
    setDataSources(state, dataSources) {
      state.dataSources = [...dataSources]
    },
    //////////////////////////////////////////新增
     setEnvironmentResources(state, resources) { 
      state.environmentResources = resources
    },
    addProject(state, project) {
      state.projects.push(project)
    },
    addUser(state, user) {
      state.users.push(user)
    },
    addDataSource(state, dataSource) {
      state.dataSources.push(dataSource)
    },

      // 更新数据源
    updateDataSource(state, dataSource) {
      const index = state.dataSources.findIndex(ds => ds.id === dataSource.id)
      if (index !== -1) {
        state.dataSources.splice(index, 1, dataSource)
      }
    },
    
    // 删除数据源
    removeDataSource(state, id) {
      const index = state.dataSources.findIndex(ds => ds.id === id)
      if (index !== -1) {
        state.dataSources.splice(index, 1)
      }
    }
  },
  actions: {
// 获取数据源列表
 async fetchDataSources({ commit }, params = {}) {
  try {
    const response = await request.get('/data-resources/filter/', { params })
    commit('setDataSources', response.data)
    return response.data
  } catch (error) {
    console.error('获取数据源列表失败:', error)
    return []
  }
},

// 添加数据源
async addDataSource({ commit }, dataSource) {
  try {
    const response = await request.post('/data-resources/', dataSource)
    commit('addDataSource', response.data)
    return response.data
  } catch (error) {
    console.error('添加数据源失败:', error)
    throw error
  }
},

// 更新数据源
async updateDataSource({ commit }, dataSource) {
  try {
    const response = await request.put(`/data-resources/${dataSource.id}/`, dataSource)
    commit('updateDataSource', response.data)
    return response.data
  } catch (error) {
    console.error('更新数据源失败:', error)
    throw error
  }
},

// 删除数据源
async removeDataSource({ commit }, id) {
  try {
    await request.delete(`/data-resources/${id}/`)
    commit('removeDataSource', id)
    return true
  } catch (error) {
    console.error('删除数据源失败:', error)
    throw error
  }
}    
  }
})