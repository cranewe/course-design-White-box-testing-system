<template>
  <el-container>
    <el-aside width="200px">
      <el-menu
        router
        :default-active="$route.path"
        class="el-menu-vertical"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/">
          <i class="el-icon-s-home"></i>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/source-code">
          <i class="el-icon-document"></i>
          <span>源代码管理</span>
        </el-menu-item>
        <el-menu-item index="/test-case">
          <i class="el-icon-files"></i>
          <span>测试用例生成</span>
        </el-menu-item>
        <el-menu-item index="/data-resources">
          <i class="el-icon-connection"></i>
          <span>数据资源配置</span>
        </el-menu-item>
       
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <h3>软件白盒测试用例生成系统</h3>
          <el-dropdown>
            <span class="el-dropdown-link">
              <el-avatar :size="40" :src="user.avatar"></el-avatar>
              {{ user.name }}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default {
  data() {
    return {
      user: {
        name: '管理员',
        avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
      }
    }
  }
}
</script>

<style scoped>
.el-container {
  height: 100vh;
}
.el-aside {
  background-color: #545c64;
}
.el-menu-vertical {
  height: 100%;
}
.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
}
.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.el-dropdown-link .el-avatar {
  margin-right: 10px;
}
</style>