<template>
  <NuxtLayout>
    <div class="compliance-container">
      <!-- High Impact Hero Banner -->
      <div class="compliance-hero section-glass mb-8">
        <div class="hero-content">
          <div class="hero-icon-box" :class="complianceLevel.class">
            <component :is="complianceLevel.icon" :size="32" />
          </div>
          <div class="hero-text">
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-black text-main">Compliance Status: {{ complianceLevel.label }}</h1>
              <span class="badge badge-success-light px-3">{{ complianceScore }}% Audit Ready</span>
            </div>
            <p class="text-muted text-sm mt-1">
              {{ complianceLevel.desc }}
            </p>
          </div>
        </div>
        <div class="hero-actions flex gap-3">
           <div class="period-control flex gap-2">
              <select v-model="selectedMonth" class="select-premium" @change="refreshData">
                <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
              </select>
           </div>
           <UiButton variant="primary" @click="scanEtims" :loading="scanning">
             <FileSearch :size="16" /> Audit Current Period
           </UiButton>
        </div>
      </div>

      <div class="compliance-grid">
        <!-- Stats Row -->
        <div class="stats-cards-row">
          <UiCard glass class="audit-summary-card">
            <template #header><h3 class="card-title">eTIMS Coverage</h3></template>
            <div class="audit-meters mt-4">
              <div class="meter-item">
                <div class="flex justify-between mb-2">
                  <span class="text-xs font-bold text-muted uppercase">Verified Tax Value</span>
                  <span class="text-xs font-bold text-success">{{ summary?.totals?.Expense?.tax ? '85%' : '0%' }}</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill success" :style="{ width: summary?.totals?.Expense?.tax ? '85%' : '0%' }"></div>
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4 mt-6">
                <div class="mini-stat">
                  <p class="text-[10px] text-muted font-bold uppercase mb-1">Total Input VAT</p>
                  <p class="text-lg font-black text-main">KES {{ summary?.totals?.Expense?.tax?.toLocaleString() || '0' }}</p>
                </div>
                <div class="mini-stat">
                   <p class="text-[10px] text-muted font-bold uppercase mb-1">Exposure Gap</p>
                   <p class="text-lg font-black text-danger">KES {{ (summary?.totals?.Expense?.tax ? (summary.totals.Expense.tax * 0.15) : 0).toLocaleString() }}</p>
                </div>
              </div>
            </div>
          </UiCard>

          <UiCard glass>
            <template #header><h3 class="card-title">Risk Alerts</h3></template>
            <div class="risk-alerts-list mt-2">
               <div v-if="totalItems === 0" class="empty-risks py-6 text-center">
                  <CheckCircle2 :size="32" class="text-success opacity-20 mx-auto mb-2" />
                  <p class="text-sm text-muted">All active expenses are matched with eTIMS invoices.</p>
               </div>
               <template v-else>
                 <div class="risk-alert-item">
                   <AlertTriangle class="text-warning" :size="18" />
                   <div>
                     <p class="text-sm font-bold text-main">Missing eTIMS Invoices</p>
                     <p class="text-xs text-muted">{{ totalItems }} transactions lack digital tax receipts.</p>
                   </div>
                 </div>
                 <div class="risk-alert-item danger">
                   <ShieldAlert class="text-danger" :size="18" />
                   <div>
                     <p class="text-sm font-bold text-main">High-Value Unverified</p>
                     <p class="text-xs text-muted">Large purchases over KES 10,000 need manual review.</p>
                   </div>
                 </div>
               </template>
            </div>
          </UiCard>
        </div>

        <!-- Risky Transactions Table -->
        <div class="mt-8">
          <UiCard>
            <template #header>
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="card-title">Reconciliation Queue</h3>
                  <p class="text-xs text-muted">Transactions requiring eTIMS verification to avoid KRA audit flags.</p>
                </div>
                <div class="flex items-center gap-2">
                   <span class="text-xs text-muted">Page {{ currentPage }} of {{ Math.ceil(totalItems/pageSize) || 1 }}</span>
                </div>
              </div>
            </template>
            <div v-if="pending" class="py-12 text-center">
               <div class="spinner mx-auto mb-4"></div>
               <p class="text-muted">Loading risk data...</p>
            </div>
            <TransactionTable 
              v-else
              :transactions="riskyTransactions" 
              :current-page="currentPage"
              :total-items="totalItems"
              :page-size="pageSize"
              @update:current-page="currentPage = $event"
              @update:page-size="pageSize = $event; currentPage = 1"
              @verify="handleVerifyRow"
            />
          </UiCard>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { 
  ShieldCheck, FileSearch, CheckCircle2, AlertTriangle, 
  ShieldAlert, ShieldX, TrendingUp, Search
} from 'lucide-vue-next'

const api = useApi()
const toast = useToast()

const selectedMonth = ref(new Date().getMonth() + 1)
const scanning = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)

const months = [
  'January', 'February', 'March', 'April', 'May', 'June', 
  'July', 'August', 'September', 'October', 'November', 'December'
]

const { data: summary, refresh: refreshSummary } = await useAsyncData('compl-summary', async () => {
  const res = await api.get(`/transactions/dashboard-summary?month=${selectedMonth.value}&year=2026&user_id=1`)
  return res.dataPayload.data
}, { watch: [selectedMonth] })

const { data: fetchResult, pending, refresh: refreshTx } = await useAsyncData(
  'risky-tx', 
  () => api.get(`/transactions/users/1?transaction_type=Expense&etims_validated=false&is_excluded=false&page=${currentPage.value}&per_page=${pageSize.value}`),
  { watch: [currentPage, pageSize] }
)

const riskyTransactions = computed(() => {
  return Array.isArray(fetchResult.value?.dataPayload?.data) 
    ? fetchResult.value.dataPayload.data 
    : []
})

watch(fetchResult, (newVal) => {
  if (newVal?.dataPayload) {
    totalItems.value = newVal.dataPayload.totalCount
  }
}, { immediate: true })

const complianceScore = computed(() => {
  if (totalItems.value === 0) return 100
  if (totalItems.value < 5) return 85
  if (totalItems.value < 15) return 60
  return 35
})

const complianceLevel = computed(() => {
  const score = complianceScore.value
  if (score >= 85) return { 
    label: 'High', 
    icon: ShieldCheck, 
    class: 'success',
    desc: 'Your M-Pesa records are well-matched with eTIMS. Audit risk is minimal.'
  }
  if (score >= 60) return { 
    label: 'Moderate', 
    icon: AlertTriangle, 
    class: 'warning',
    desc: 'Several transactions are missing digital receipts. Reconcile these to avoid KRA flags.'
  }
  return { 
    label: 'At Risk', 
    icon: ShieldX, 
    class: 'danger',
    desc: 'Significant tax gap detected. Ensure eTIMS invoices are uploaded for all major expenses.'
  }
})

const refreshData = () => {
  refreshSummary()
  refreshTx()
}

const scanEtims = async () => {
  const invoiceNum = prompt("Enter Sandbox eTIMS Invoice Number (e.g. KRACU0100058659/5134):", "KRACU0100058659/5134")
  if (!invoiceNum) return

  scanning.value = true
  try {
    await api.post(`/transactions/scan-etims?invoice_number=${encodeURIComponent(invoiceNum)}&user_id=1`)
    toast.success('GavaConnect Audit Complete! Matched with eTIMS records.')
    refreshData()
  } catch (err) {
    toast.error('Audit sync failed.')
  } finally {
    scanning.value = false
  }
}

const handleVerifyRow = async (tx) => {
  const invoiceNum = prompt(`Enter eTIMS Invoice for ${tx.description} (KES ${tx.amount}):`, "KRACU0100058659/5134")
  if (!invoiceNum) return
  
  scanning.value = true
  try {
    await api.post(`/transactions/scan-etims?invoice_number=${encodeURIComponent(invoiceNum)}&user_id=1`)
    toast.success('Transaction Verified successfully!')
    refreshData()
  } catch (err) {
    toast.error('Verification failed.')
  } finally {
    scanning.value = false
  }
}
</script>

<style scoped>
.compliance-container {
  width: 100%;
}

.section-glass {
  background: white;
  padding: 2rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
}

.compliance-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, white, var(--bg-main));
}

.hero-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.hero-icon-box {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-icon-box.success { background: var(--success-light); color: var(--success); }
.hero-icon-box.warning { background: var(--warning-light); color: var(--warning); }
.hero-icon-box.danger { background: var(--danger-light); color: var(--danger); }

.select-premium {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: white;
  font-weight: 600;
  font-size: 0.9rem;
  outline: none;
}

.stats-cards-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.progress-bar {
  height: 8px;
  background: var(--bg-main);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill.success { background: var(--success); }

.mini-stat {
  padding: 1rem;
  background: var(--bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.risk-alert-item {
  display: flex;
  gap: 1rem;
  padding: 0.875rem;
  border-radius: var(--radius-md);
  background: #fffbeb;
  border: 1px solid #fde68a;
  margin-bottom: 0.75rem;
}

.risk-alert-item.danger {
  background: #fef2f2;
  border-color: #fee2e2;
}

.card-title { font-size: 1.1rem; font-weight: 800; color: var(--text-main); }

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--primary-light);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .compliance-hero { flex-direction: column; align-items: flex-start; gap: 1.5rem; }
  .stats-cards-row { grid-template-columns: 1fr; }
}
</style>
