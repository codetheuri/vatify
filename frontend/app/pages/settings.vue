<template>
  <NuxtLayout>
    <div class="settings-wrapper">
      <div class="settings-header">
        <h1 class="page-title">Account Settings</h1>
        <p class="page-subtitle">Manage your profile, KRA credentials, and security.</p>
      </div>

      <div class="settings-grid">
        <!-- Sidebar Navigation -->
        <aside class="settings-sidebar">
          <nav class="settings-nav">
            <button
              v-for="item in navItems"
              :key="item.id"
              :class="['nav-link', { active: activeTab === item.id }]"
              @click="activeTab = item.id"
            >
              <component :is="item.icon" :size="18" />
              <span>{{ item.label }}</span>
              <ChevronRight v-if="activeTab === item.id" :size="14" class="ms-auto" />
            </button>
          </nav>

          <!-- KRA PIN Status Card -->
          <div class="pin-status-card mt-6">
            <div class="pin-icon">
              <ShieldCheck :size="22" />
            </div>
            <div>
              <p class="pin-value">{{ authUser?.kra_pin || '—' }}</p>
              <p class="pin-label">{{ authUser?.pin_status || 'Active' }}</p>
            </div>
          </div>
        </aside>

        <!-- Content Area -->
        <main class="settings-content">
          <Transition name="fade-slide" mode="out-in">

            <!-- ── TAB: Profile ── -->
            <div v-if="activeTab === 'profile'" key="profile" class="tab-pane">
              <UiCard>
                <template #header>
                  <div class="flex items-center gap-3">
                    <User class="text-primary" :size="20" />
                    <div>
                      <h3 class="card-title">Personal Information</h3>
                      <p class="card-subtitle">Your account details and business identity.</p>
                    </div>
                  </div>
                </template>

                <div class="form-grid p-6">
                  <UiInput label="Full Name" v-model="form.full_name" placeholder="John Doe" />
                  <UiInput label="Email Address" v-model="form.email" disabled />
                  <UiInput label="Mobile Number" v-model="form.phone_number" placeholder="+254 7XX XXX XXX" />
                  <UiInput label="Business / Trading Name" v-model="form.business_name" placeholder="Acme Services Ltd" />
                  <div class="col-span-2">
                    <UiInput label="Physical Address" v-model="form.physical_address" placeholder="Nairobi, Kenya" />
                  </div>
                </div>

                <template #footer>
                  <div class="flex justify-end gap-3">
                    <UiButton variant="ghost" @click="resetForm">Reset</UiButton>
                    <UiButton variant="primary" @click="handleSaveProfile" :loading="saving">
                      <Save :size="16" /> Save Changes
                    </UiButton>
                  </div>
                </template>
              </UiCard>
            </div>

            <!-- ── TAB: KRA Account ── -->
            <div v-else-if="activeTab === 'kra'" key="kra" class="tab-pane">

              <!-- Business Info (read-only from KRA sync) -->
              <UiCard glass class="mb-6">
                <template #header>
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <Key class="text-primary" :size="20" />
                      <div>
                        <h3 class="card-title">KRA Registration</h3>
                        <p class="card-subtitle">Data pulled from the KRA Sandbox via your PIN.</p>
                      </div>
                    </div>
                    <UiButton variant="outline" size="sm" :loading="syncing" @click="handleSync">
                      <RefreshCcw :size="14" :class="{ 'animate-spin': syncing }" />
                      Sync KRA
                    </UiButton>
                  </div>
                </template>

                <div class="info-grid p-6">
                  <div class="info-row">
                    <span class="info-label">KRA PIN</span>
                    <span class="info-value font-mono">{{ authUser?.kra_pin || '—' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">PIN Status</span>
                    <span class="badge-active">{{ authUser?.pin_status || 'Active' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">Taxpayer Name</span>
                    <span class="info-value">{{ authUser?.full_name || '—' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">KRA Status</span>
                    <span class="info-value">{{ authUser?.kra_status || 'Active' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">Physical Address</span>
                    <span class="info-value">{{ authUser?.physical_address || 'Not synced yet' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">Last Synced</span>
                    <span class="info-value">{{ lastSyncFormatted }}</span>
                  </div>
                </div>
              </UiCard>

              <!-- Obligations List -->
              <UiCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <h3 class="card-title">Tax Obligations</h3>
                    <UiButton variant="ghost" size="sm" @click="$router.push('/eslips')">
                      Browse E-Slips
                      <ChevronRight :size="14" class="ml-1" />
                    </UiButton>
                  </div>
                </template>

                <div class="p-0">
                  <div
                    v-for="obs in obligationsList"
                    :key="obs"
                    class="flex items-center justify-between px-5 py-4 border-b border-border-color last:border-0 hover:bg-slate-50 transition-colors"
                  >
                    <div class="flex items-center gap-4">
                      <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-black text-sm">
                        {{ obs.charAt(0) }}
                      </div>
                      <div>
                        <p class="font-bold text-sm text-main">{{ obs }}</p>
                        <p class="text-[10px] text-muted uppercase tracking-wider font-bold">KRA Registered Obligation</p>
                      </div>
                    </div>
                    <span class="badge-active">Active</span>
                  </div>
                  <div v-if="obligationsList.length === 0" class="px-5 py-8 text-center text-sm text-muted">
                    No obligations found. Sync your KRA data first.
                  </div>
                </div>
              </UiCard>
            </div>

            <!-- ── TAB: Security ── -->
            <div v-else-if="activeTab === 'security'" key="security" class="tab-pane">
              <!-- MFA Toggle -->
              <UiCard class="mb-6">
                <template #header>
                  <div class="flex items-center gap-3">
                    <ShieldCheck class="text-primary" :size="20" />
                    <div>
                      <h3 class="card-title">Multi-Factor Authentication</h3>
                      <p class="card-subtitle">Require an email OTP on every login for extra security.</p>
                    </div>
                  </div>
                </template>

                <div class="p-6">
                  <div class="flex items-center justify-between py-2">
                    <div>
                      <p class="font-bold text-main text-sm">Email OTP Verification</p>
                      <p class="text-xs text-muted mt-1">A 6-digit code will be sent to <strong>{{ authUser?.email }}</strong> on each login.</p>
                    </div>
                    <label class="mfa-toggle">
                      <input type="checkbox" :checked="authUser?.mfa_enabled" @change="toggleMfa" class="sr-only peer" />
                      <div class="toggle-track peer-checked:bg-primary">
                        <div class="toggle-thumb peer-checked:translate-x-5"></div>
                      </div>
                    </label>
                  </div>
                </div>
              </UiCard>

              <!-- Change Password -->
              <UiCard>
                <template #header>
                  <div class="flex items-center gap-3">
                    <Lock class="text-primary" :size="20" />
                    <div>
                      <h3 class="card-title">Change Password</h3>
                      <p class="card-subtitle">Update your account password.</p>
                    </div>
                  </div>
                </template>

                <div class="p-6 space-y-4">
                  <UiInput label="Current Password" v-model="pwForm.current" type="password" placeholder="••••••••" />
                  <UiInput label="New Password" v-model="pwForm.new_password" type="password" placeholder="••••••••" />
                  <UiInput label="Confirm New Password" v-model="pwForm.confirm" type="password" placeholder="••••••••" />
                </div>

                <template #footer>
                  <div class="flex justify-end">
                    <UiButton variant="primary" @click="handleChangePassword" :loading="changingPw">
                      Update Password
                    </UiButton>
                  </div>
                </template>
              </UiCard>
            </div>

          </Transition>
        </main>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import {
  User, Key, ShieldCheck, Lock, Save, ChevronRight, RefreshCcw
} from 'lucide-vue-next'

const api = useApi()
const toast = useToast()
const { user: authUser, setUser, token, refreshToken } = useAuth()

const saving = ref(false)
const syncing = ref(false)
const changingPw = ref(false)
const activeTab = ref('profile')

const navItems = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'kra',     label: 'KRA Account', icon: Key },
  { id: 'security',label: 'Security', icon: ShieldCheck },
]

// ── Form state seeded from auth store ──
const form = ref({
  full_name:       authUser.value?.full_name       || '',
  email:           authUser.value?.email            || '',
  phone_number:    authUser.value?.phone_number     || '',
  business_name:   authUser.value?.business_name   || '',
  physical_address:authUser.value?.physical_address || '',
})

watch(authUser, (val) => {
  if (val) {
    form.value = {
      full_name:        val.full_name       || '',
      email:            val.email            || '',
      phone_number:     val.phone_number     || '',
      business_name:    val.business_name   || '',
      physical_address: val.physical_address || '',
    }
  }
}, { immediate: true })

const resetForm = () => {
  form.value = {
    full_name:        authUser.value?.full_name       || '',
    email:            authUser.value?.email            || '',
    phone_number:     authUser.value?.phone_number     || '',
    business_name:    authUser.value?.business_name   || '',
    physical_address: authUser.value?.physical_address || '',
  }
}

const pwForm = ref({ current: '', new_password: '', confirm: '' })

// ── Computed ──
const obligationsList = computed(() =>
  (authUser.value?.tax_obligations || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
)

const lastSyncFormatted = computed(() => {
  if (!authUser.value?.last_sync_at) return 'Never'
  return new Date(authUser.value.last_sync_at * 1000).toLocaleString('en-KE')
})

// ── Actions ──
const handleSaveProfile = async () => {
  saving.value = true
  try {
    const res = await api.post('/users/update-profile', form.value)
    const updated = res.dataPayload.data
    setUser(updated, token.value, refreshToken.value)
    toast.success('Profile updated successfully!')
  } catch (err) {
    const msg = err.data?.alertifyPayload?.message || err.data?.errorPayload?.errors || 'Failed to save profile'
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

const handleSync = async () => {
  syncing.value = true
  try {
    const res = await api.post('/users/refresh-obligations')
    const updated = res.dataPayload.data
    setUser(updated, token.value, refreshToken.value)
    toast.success('KRA data synced successfully!')
  } catch (err) {
    toast.error('KRA Sync failed. Try again later.')
  } finally {
    setTimeout(() => syncing.value = false, 800)
  }
}

const toggleMfa = async (e) => {
  const enabled = e.target.checked
  try {
    const res = await api.post('/users/toggle-mfa', { enabled })
    const updated = res.dataPayload.data
    setUser(updated, token.value, refreshToken.value)
    toast.success(`MFA ${enabled ? 'enabled' : 'disabled'} successfully.`)
  } catch (err) {
    toast.error('Failed to update MFA setting.')
    e.target.checked = !enabled
  }
}

const handleChangePassword = async () => {
  if (!pwForm.value.current || !pwForm.value.new_password) {
    toast.error('Please fill in all password fields.')
    return
  }
  if (pwForm.value.new_password !== pwForm.value.confirm) {
    toast.error('New passwords do not match.')
    return
  }
  changingPw.value = true
  try {
    await api.post('/users/change-password', {
      current_password: pwForm.value.current,
      new_password: pwForm.value.new_password
    })
    toast.success('Password changed successfully!')
    pwForm.value = { current: '', new_password: '', confirm: '' }
  } catch (err) {
    const msg = err.data?.alertifyPayload?.message || err.data?.errorPayload?.errors || 'Failed to change password'
    toast.error(msg)
  } finally {
    changingPw.value = false
  }
}
</script>

<style scoped>
.settings-wrapper { width: 100%; }

.settings-header { margin-bottom: 2.5rem; }

.page-title {
  font-size: 1.875rem;
  font-weight: 800;
  color: var(--text-main);
  letter-spacing: -0.025em;
  margin-bottom: 0.25rem;
}

.page-subtitle { color: var(--text-muted); font-size: 0.9rem; }

.settings-grid {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 2.5rem;
  align-items: flex-start;
}

/* ── Sidebar ── */
.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
  transition: all 0.2s ease;
  cursor: pointer;
}
.nav-link:hover { background: rgba(var(--primary-rgb), 0.05); color: var(--primary); }
.nav-link.active {
  background: white;
  color: var(--primary);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid var(--border-color);
}

.ms-auto { margin-left: auto; }

.pin-status-card {
  background: var(--primary);
  color: white;
  border-radius: var(--radius-md);
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.pin-icon {
  width: 40px; height: 40px;
  background: rgba(255,255,255,0.15);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.pin-value { font-size: 0.8rem; font-weight: 800; font-family: monospace; margin: 0; }
.pin-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.8; margin: 0.15rem 0 0; }

/* ── Cards ── */
.card-title { font-size: 1rem; font-weight: 800; color: var(--text-main); margin: 0; }
.card-subtitle { font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}
.col-span-2 { grid-column: span 2; }

/* ── KRA Info Grid ── */
.info-grid { display: flex; flex-direction: column; gap: 0; }
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-color);
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
.info-value { font-size: 0.875rem; font-weight: 600; color: var(--text-main); text-align: right; }

.badge-active {
  background: #dcfce7;
  color: #15803d;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 3px 10px;
  border-radius: 20px;
}

/* ── MFA Toggle ── */
.mfa-toggle { position: relative; cursor: pointer; }
.toggle-track {
  width: 44px; height: 24px;
  background: #e2e8f0;
  border-radius: 12px;
  transition: background 0.3s;
  position: relative;
  display: block;
}
.toggle-thumb {
  position: absolute;
  top: 3px; left: 3px;
  width: 18px; height: 18px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.peer:checked ~ .toggle-track { background: var(--primary); }
.peer:checked ~ .toggle-track .toggle-thumb { transform: translateX(20px); }

/* ── Transition ── */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from { opacity: 0; transform: translateY(8px); }
.fade-slide-leave-to  { opacity: 0; transform: translateY(-8px); }

@media (max-width: 900px) {
  .settings-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .col-span-2 { grid-column: span 1; }
}
</style>
