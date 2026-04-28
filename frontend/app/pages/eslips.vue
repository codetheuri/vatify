<template>
  <NuxtLayout>
    <div class="eslips-page">
      <header class="flex justify-between items-end mb-8">
        <div>
          <h1 class="text-3xl font-black text-main tracking-tight">KRA E-Slips</h1>
          <p class="text-muted text-sm mt-1">History of payment registration numbers and slips generated.</p>
        </div>
        <div class="flex gap-3">
          <UiButton variant="ghost" to="/profile">
            <User :size="16" />
            Profile
          </UiButton>
          <UiButton variant="primary" @click="fetchESlips" :loading="loading" class="shadow-primary">
            <RefreshCcw :size="16" :class="{ 'animate-spin': loading }" />
            Refresh History
          </UiButton>
        </div>
      </header>

      <div v-if="eslips.length === 0 && !loading" class="empty-state py-20 text-center bg-white rounded-3xl border-2 border-dashed border-slate-100">
        <div class="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 text-slate-300">
          <FileText :size="32" />
        </div>
        <h3 class="font-bold text-main">No E-Slips Found</h3>
        <p class="text-sm text-muted mt-1 max-w-xs mx-auto">Sync your profile to fetch recent payment registrations from the KRA system.</p>
        <UiButton variant="primary" class="mt-6" @click="fetchESlips">Sync Now</UiButton>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UiCard v-for="slip in eslips" :key="slip.id" glass class="slip-card">
          <div class="flex justify-between items-start mb-4">
            <div class="p-2 bg-primary/10 rounded-lg text-primary">
              <Receipt :size="20" />
            </div>
            <div :class="['status-badge', slip.status.toLowerCase()]">
              {{ slip.status }}
            </div>
          </div>
          
          <h4 class="font-black text-main text-lg">{{ formatCurrency(slip.amount) }}</h4>
          <p class="text-[10px] font-bold text-muted uppercase tracking-widest mt-1">{{ slip.obligation_name }}</p>
          
          <div class="mt-4 space-y-3 pt-4 border-t border-border-color">
            <div class="flex justify-between items-center">
              <span class="text-xs text-muted">E-Slip No</span>
              <span class="text-xs font-black text-main">{{ slip.eslip_number }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-xs text-muted">PRN</span>
              <span class="text-xs font-mono font-bold text-primary">{{ slip.payment_registration_number }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-xs text-muted">Tax Period</span>
              <span class="text-xs font-bold text-main">{{ slip.tax_period }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-xs text-muted">Generated At</span>
              <span class="text-xs font-medium text-main">{{ formatDate(slip.generated_at) }}</span>
            </div>
          </div>

          <template #footer>
            <UiButton block variant="ghost" size="sm" @click="downloadSlip(slip)">
              <Download :size="14" />
              Download Slip PDF
            </UiButton>
          </template>
        </UiCard>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { FileText, RefreshCcw, User, Receipt, Download, ChevronRight } from 'lucide-vue-next'

const api = useApi()
const toast = useToast()

const eslips = ref([])
const loading = ref(false)

const fetchESlips = async () => {
  loading.value = true
  try {
    // First trigger a sync to ensure we have latest from sandbox
    await api.post('/users/refresh-obligations')
    
    // Then fetch from our DB
    const res = await api.get('/users/me/eslips')
    eslips.value = res.dataPayload.data
  } catch (err) {
    toast.error('Failed to load E-Slips.')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KSh',
    minimumFractionDigits: 0
  }).format(amount)
}

const downloadSlip = (slip) => {
  toast.info('Downloading E-Slip ' + slip.eslip_number + '...')
  // Simulate download
  setTimeout(() => {
    toast.success('Download complete.')
  }, 1500)
}

onMounted(() => {
  fetchESlips()
})
</script>

<style scoped>
.eslips-page {
  width: 100%;
}

.status-badge {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.05em;
}

.status-badge.paid { background: #dcfce7; color: #15803d; }
.status-badge.pending { background: #fefce8; color: #a16207; }

.slip-card {
  transition: transform 0.2s;
}

.slip-card:hover {
  transform: translateY(-4px);
}

.shadow-primary {
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
}
</style>
