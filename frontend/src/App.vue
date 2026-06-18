<script setup lang="ts">
import { RouterView, useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/help/create', title: '发起求助', icon: '📞', desc: '一键呼叫家人帮助' },
  { path: '/guidance', title: '远程指导', icon: '💬', desc: '查看所有求助记录' },
  { path: '/stepcards', title: '步骤卡整理', icon: '📋', desc: '沉淀可复用操作指南' },
  { path: '/library', title: '高频问题库', icon: '📚', desc: '历史方案快速查找' },
  { path: '/stats', title: '数据统计', icon: '📊', desc: '求助数据可视化' }
]

const currentIndex = computed(() => {
  return navItems.findIndex((item) => route.path.startsWith(item.path.split('/').slice(0, 3).join('/')))
})
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">👵📱</div>
        <div>
          <div class="logo-title">长者智慧助老</div>
          <div class="logo-sub">智能手机求助平台</div>
        </div>
      </div>

      <nav class="nav">
        <button
          v-for="(item, index) in navItems"
          :key="item.path"
          class="nav-item"
          :class="{ active: currentIndex === index }"
          @click="router.push(item.path)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">
            <span class="nav-title">{{ item.title }}</span>
            <span class="nav-desc">{{ item.desc }}</span>
          </span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div class="user-card">
          <div class="avatar">👴</div>
          <div>
            <div class="user-name">张奶奶</div>
            <div class="user-role">使用者</div>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="page-header">
        <h1 class="page-title">
          <span>{{ navItems[currentIndex]?.icon }}</span>
          {{ navItems[currentIndex]?.title }}
        </h1>
        <p class="page-subtitle" v-if="navItems[currentIndex]">
          {{ navItems[currentIndex]?.desc }}
        </p>
      </header>
      <div class="page-content">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
}

.logo {
  padding: 28px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 36px;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
}

.logo-sub {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 2px;
}

.nav {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
}

.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  text-align: left;
  margin-bottom: 4px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.nav-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.nav-text {
  display: flex;
  flex-direction: column;
}

.nav-title {
  font-size: 15px;
  font-weight: 600;
}

.nav-desc {
  font-size: 11px;
  opacity: 0.75;
  margin-top: 2px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
}

.user-role {
  font-size: 11px;
  opacity: 0.6;
}

.main-content {
  flex: 1;
  margin-left: 280px;
  min-height: 100vh;
}

.page-header {
  padding: 32px 40px 16px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title span:first-child {
  font-size: 30px;
}

.page-subtitle {
  color: #64748b;
  margin-top: 4px;
  font-size: 14px;
}

.page-content {
  padding: 28px 40px 40px;
}

@media (max-width: 900px) {
  .sidebar {
    width: 72px;
  }
  .logo > div:last-child,
  .nav-text,
  .user-card > div:last-child {
    display: none;
  }
  .main-content {
    margin-left: 72px;
  }
  .page-header,
  .page-content {
    padding-left: 24px;
    padding-right: 24px;
  }
}
</style>
