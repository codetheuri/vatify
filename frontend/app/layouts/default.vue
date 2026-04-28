<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <img src="/vatify-logo.png" alt="Vatify" class="logo-img" />
      </div>
      
      <nav class="sidebar-nav">
        <NuxtLink to="/" class="nav-item" active-class="active">
          <LayoutDashboard :size="18" /> Dashboard
        </NuxtLink>
        <NuxtLink to="/transactions" class="nav-item" active-class="active">
          <ReceiptText :size="18" /> Transactions
        </NuxtLink>
        <NuxtLink to="/documents" class="nav-item" active-class="active">
          <FolderOpen :size="18" /> Documents
        </NuxtLink>
        <NuxtLink to="/compliance" class="nav-item" active-class="active">
          <ShieldCheck :size="18" /> Compliance
        </NuxtLink>
        <NuxtLink to="/returns" class="nav-item" active-class="active">
          <FileText :size="18" /> Tax Returns
        </NuxtLink>
        <NuxtLink to="/settings" class="nav-item" active-class="active">
          <Settings :size="18" /> Settings
        </NuxtLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="avatar">{{ userInitial }}</div>
          <div class="user-info">
            <p class="user-name">{{ user?.full_name || 'Guest' }}</p>
            <p class="user-pin">{{ user?.kra_pin || 'No PIN' }}</p>
          </div>
          <button @click="logout" class="ml-auto text-muted hover:text-danger transition-colors" title="Logout">
            <LogOut :size="16" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <header class="top-nav glass">
        <div class="page-title">
          <h1>{{ currentPageTitle }}</h1>
        </div>
        <div class="nav-actions">
          <UiButton variant="ghost" size="sm">
            <HelpCircle :size="16" /> Help
          </UiButton>
          <UiButton variant="primary" size="sm" @click="navigateTo('/transactions')">
            <Upload :size="16" /> Quick Import
          </UiButton>
        </div>
      </header>

      <div class="content-wrapper animate-fade-in">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { 
  LayoutDashboard, 
  ReceiptText, 
  ShieldCheck, 
  FileText, 
  Settings,
  HelpCircle,
  Upload,
  FolderOpen,
  User as UserIcon,
  LogOut
} from 'lucide-vue-next'

const route = useRoute()
const { user, logout } = useAuth()

const userInitial = computed(() => {
  if (!user.value?.full_name) return '?'
  return user.value.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const currentPageTitle = computed(() => {
  const titles = {
    'index': 'Dashboard Overview',
    'transactions': 'Transaction History',
    'documents': 'Document Center',
    'compliance': 'Tax Compliance',
    'returns': 'Tax Returns',
    'settings': 'Account Settings'
  }
  return titles[route.name] || 'Vatify'
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Styling */
.sidebar {
  width: 280px;
  background-color: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 50;
}

.logo {
  padding: 1.5rem 1.5rem;
  display: flex;
  align-items: center;
}

.logo-img {
  width: 140px;
  height: auto;
  object-fit: contain;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--primary);
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: white;
  font-weight: 800;
  font-size: 1.2rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.02em;
}

.sidebar-nav {
  flex: 1;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition);
}

.nav-item:hover {
  background-color: var(--primary-light);
  color: var(--primary);
}

.nav-item.active {
  background-color: var(--primary);
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 32px;
  height: 32px;
  background-color: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
}

.user-name { font-size: 0.875rem; font-weight: 500; margin: 0; }
.user-pin { font-size: 0.75rem; color: #94a3b8; margin: 0; }

/* Main Content Styling */
.main-content {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
}

.top-nav {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 40;
}

.page-title h1 {
  font-size: 1.125rem;
  margin: 0;
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.content-wrapper {
  padding: 2rem;
  flex: 1;
}
</style>
