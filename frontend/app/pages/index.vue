<template>
  <NuxtLayout>
    <div class="dashboard-v2">
      <!-- Welcome Hero -->
      <header class="dashboard-hero mb-8">
        <div class="hero-left">
          <h1 class="text-3xl font-black text-main tracking-tight">Welcome back, {{ user?.full_name || 'Business Owner' }}</h1>
          <p class="text-muted text-sm mt-1">Your business tax health at a glance for {{ currentMonthName }} {{ currentYear }}.</p>
        </div>
        <div class="hero-right flex gap-3">
           <div class="sync-status glass px-4 py-2 rounded-full border border-border-color flex items-center gap-2">
              <span class="pulse green"></span>
              <span class="text-[10px] font-black text-main uppercase italic">{{ isMonthlyFiler ? 'Monthly Filing Active' : 'Annual Tracking Active' }}</span>
           </div>
           <UiButton variant="ghost" size="sm" @click="logout" class="text-danger">
             <LogOut :size="16" />
           </UiButton>
        </div>
      </header>

      <!-- Glass KPI Grid -->
      <section class="premium-kpi-grid mb-10">
        <div class="kpi-card glass hover-lift" v-for="kpi in kpis" :key="kpi.label">
          <div class="kpi-header mb-4">
             <div class="kpi-icon-box" :class="kpi.colorClass">
               <component :is="kpi.icon" :size="20" />
             </div>
             <span class="kpi-growth" :class="kpi.trendClass">{{ kpi.trend }}</span>
          </div>
          <p class="kpi-label">{{ kpi.label }}</p>
          <h2 class="kpi-value font-black">{{ kpi.value }}</h2>
          <div class="kpi-footer mt-4">
             <div class="mini-progress">
               <div class="progress-fill" :class="kpi.colorClass" :style="{ width: '70%' }"></div>
             </div>
          </div>
        </div>
      </section>

      <!-- Main Content Split -->
      <div class="dashboard-content-split">
        <!-- Left Column: Insights & Activity -->
        <main class="content-left">
          <UiCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="font-bold text-main flex items-center gap-2">
                  <TrendingUp :size="18" class="text-primary" />
                  Tax Liability Trend
                </h3>
                <UiButton variant="ghost" size="sm" @click="handleDownloadSummary" :loading="downloadingPdf">Download PDF</UiButton>
              </div>
            </template>
            
            <div class="chart-container py-6">
               <div class="flex items-end justify-between h-[180px] px-4">
                  <div v-for="(h, i) in [40, 65, 30, 85, 55, 90]" :key="i" class="bar-group flex flex-col items-center gap-2">
                     <div class="bar-fill" :style="{ height: h + '%' }" :class="{ active: i === 5 }">
                        <div class="bar-tooltip">KES {{ (h * 1200).toLocaleString() }}</div>
                     </div>
                     <span class="text-[10px] text-muted font-bold uppercase">{{ ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'][i] }}</span>
                  </div>
               </div>
            </div>
            
            <div class="p-4 bg-bg-main rounded-xl mt-4 border border-border-color">
              <div class="flex gap-4 items-center">
                <div :class="['w-10 h-10 rounded-full flex items-center justify-center', auditReadiness.iconClass]">
                  <CheckCircle2 v-if="auditReadiness.level === 'High'" :size="20" />
                  <AlertCircle v-else :size="20" />
                </div>
                <div>
                  <p class="text-sm font-bold text-main">eTIMS Audit Readiness: {{ auditReadiness.level }}</p>
                  <p class="text-xs text-muted">{{ auditReadiness.message }}</p>
                </div>
              </div>
            </div>
          </UiCard>

          <div class="mt-8">
            <h3 class="text-sm font-bold text-muted uppercase tracking-widest mb-4">Recent Activity</h3>
            <div class="activity-feed">
               <div class="activity-item" v-for="act in activity" :key="act.id">
                  <div class="act-icon-box">
                    <component :is="act.icon" :size="14" />
                  </div>
                  <div class="act-info">
                    <p class="act-title font-bold text-sm text-main">{{ act.title }}</p>
                    <p class="text-xs text-muted">{{ act.time }}</p>
                  </div>
                  <span class="act-amount" :class="act.type">{{ act.amount }}</span>
               </div>
            </div>
          </div>
        </main>

        
        <aside class="content-right">
          <UiCard glass class="mb-6">
            <template #header><h3 class="font-bold text-main">Sync Actions</h3></template>
            <div class="action-buttons-stack">
              <UiButton block variant="outline" class="action-btn" @click="$router.push('/transactions')">
                <FileUp :size="16" /> Upload Statement
              </UiButton>
              <UiButton block variant="outline" class="action-btn" @click="handleScanEtims" :loading="scanning" v-if="isVatRegistered">
                <ScanLine :size="16" /> Verify eTIMS Invoice
              </UiButton>
              <UiButton block variant="primary" class="action-btn shadow-primary" @click="$router.push('/returns')" v-if="isMonthlyFiler">
                 File {{ currentMonthName }} Return 
              </UiButton>
              <UiButton block variant="primary" class="action-btn shadow-primary" @click="$router.push('/returns')" v-else-if="obligations.includes('Income Tax')">
                 Reconcile Monthly Figures
              </UiButton>
              <div v-else class="text-xs text-muted p-2 text-center bg-slate-50 rounded-xl">
                 Sync profile to enable filing actions
              </div>
            </div>
          </UiCard>

          <UiCard>
            <template #header><h3 class="font-bold text-main">KRA Obligations</h3></template>
            <div class="deadlines-list">
              <div class="deadline-item" v-if="isVatRegistered">
                <div class="deadline-calendar">
                  <span class="month">{{ currentMonthName.slice(0,3).toUpperCase() }}</span>
                  <span class="day">20</span>
                </div>
                <div class="deadline-info">
                  <p class="text-sm font-bold">VAT Return + Payment</p>
                  <p class="text-[10px] text-muted">{{ currentMonthName }} {{ currentYear }}</p>
                </div>
                <div class="status-indicator warning"></div>
              </div>

              <div class="deadline-item" v-if="isTotRegistered">
                <div class="deadline-calendar">
                  <span class="month">{{ currentMonthName.slice(0,3).toUpperCase() }}</span>
                  <span class="day">20</span>
                </div>
                <div class="deadline-info">
                  <p class="text-sm font-bold">TOT Return</p>
                  <p class="text-[10px] text-muted">{{ currentMonthName }} {{ currentYear }}</p>
                </div>
                <div class="status-indicator warning"></div>
              </div>

              <div class="deadline-item" v-if="obligations.includes('Income Tax')">
                <div class="deadline-calendar">
                  <span class="month">JUN</span>
                  <span class="day">30</span>
                </div>
                <div class="deadline-info">
                  <p class="text-sm font-bold">Annual Income Tax (IT1)</p>
                  <p class="text-[10px] text-muted">Year {{ currentYear - 1 }} Return</p>
                </div>
                <div class="status-indicator"></div>
              </div>

              <div v-if="!isMonthlyFiler && !obligations.includes('Income Tax')" class="p-4 text-center text-xs text-muted">
                No active deadlines found for your current obligations.
              </div>
            </div>
          </UiCard>
          
          <div class="compliance-tip mt-6 p-4 rounded-2xl bg-primary/5 border border-primary/10">
             <div class="flex gap-3">
               <Lightbulb class="text-primary flex-shrink-0" :size="20" />
                <p class="text-[11px] leading-relaxed text-slate-600">
                  Pro Tip: Categorizing your M-Pesa business till transactions daily reduces manual review time by 40% at the end of the month.
                </p>
             </div>
          </div>
        </aside>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { 
  TrendingUp, TrendingDown, FileText, AlertCircle, 
  FileUp, ScanLine, CheckCircle2, ShieldCheck,
  RefreshCcw, Download, Lightbulb, LogOut
} from 'lucide-vue-next'

const { user, logout } = useAuth()
const obligations = computed(() => user.value?.tax_obligations || 'Income Tax')

const isVatRegistered = computed(() => obligations.value.toUpperCase().includes('VAT'))
const isTotRegistered = computed(() => obligations.value.toUpperCase().includes('TOT') || obligations.value.toUpperCase().includes('TURNOVER'))
const isMonthlyFiler = computed(() => isVatRegistered.value || isTotRegistered.value)

const api = useApi()
const toast = useToast()
const scanning = ref(false)
const downloadingPdf = ref(false)

// Use the real current date — the API queries the actual DB period
const now = new Date()
const currentMonth = now.getMonth() + 1  // 1-indexed
const currentYear = now.getFullYear()
const currentMonthName = now.toLocaleString('default', { month: 'long' })

const { data: summary, refresh: refreshSummary } = await useAsyncData('home-summary', async () => {
  try {
    const res = await api.get(`/transactions/dashboard-summary?month=${currentMonth}&year=${currentYear}`)
    return res?.dataPayload?.data
  } catch (e) {
    return null
  }
})

const { data: catSummary } = await useAsyncData('home-cat-summary', async () => {
  try {
    const res = await api.get(`/transactions/category-summary?month=${currentMonth}&year=${currentYear}`)
    return res?.dataPayload?.data
  } catch (e) {
    return null
  }
})

const netVatPayable = computed(() => catSummary.value?.grand_totals?.net_vat_payable ?? 0)

const kpis = computed(() => {
  const list = [
    { 
      label: 'Monthly Income', 
      value: `KES ${(summary.value?.totals?.Income?.amount || 0).toLocaleString()}`, 
      icon: TrendingUp, 
      colorClass: 'success', 
      trend: currentMonthName, 
      trendClass: 'trend-neutral' 
    },
    { 
      label: 'Total Expenses', 
      value: `KES ${(summary.value?.totals?.Expense?.amount || 0).toLocaleString()}`, 
      icon: TrendingDown, 
      colorClass: 'danger', 
      trend: currentMonthName, 
      trendClass: 'trend-neutral'
    }
  ]

  if (isMonthlyFiler.value) {
    list.push({ 
      label: 'Net VAT Due', 
      value: `KES ${Math.abs(netVatPayable.value).toLocaleString()}`, 
      icon: FileText, 
      colorClass: 'info', 
      trend: netVatPayable.value >= 0 ? 'Payable' : 'Credit', 
      trendClass: netVatPayable.value >= 0 ? 'trend-warn' : 'trend-up'
    })
  } else {
    list.push({
      label: 'Annual Status',
      value: 'Drafting IT1',
      icon: FileText,
      colorClass: 'info',
      trend: 'FY 2026',
      trendClass: 'trend-neutral'
    })
  }

  list.push({ 
    label: 'Risk Alerts', 
    value: `${summary.value?.compliance_risk_count || 0} items`, 
    icon: AlertCircle, 
    colorClass: 'warning', 
    trend: 'Unverified', 
    trendClass: 'trend-warn' 
  })

  return list
})

const activity = [
  { id: 1, title: `M-Pesa Import processed`, time: 'Last upload', amount: `KES ${(summary.value?.totals?.Income?.amount || 0).toLocaleString()}`, icon: FileUp, type: 'income' },
  { id: 2, title: `${summary.value?.compliance_risk_count || 0} items need eTIMS verification`, time: currentMonthName, amount: `KES ${(summary.value?.unvalidated_sum || 0).toLocaleString()}`, icon: ShieldCheck, type: 'expense' },
  { id: 3, title: 'AI Categorization available', time: 'On demand', amount: 'Run now →', icon: RefreshCcw, type: 'neutral' },
  { id: 4, title: 'KRA CSV Export ready', time: 'Export anytime', amount: 'CSV', icon: Download, type: 'neutral' },
]
const auditReadiness = computed(() => {
  const riskCount = summary.value?.compliance_risk_count || 0
  const totalExpenses = summary.value?.totals?.Expense?.amount || 0
  const unvalidatedSum = summary.value?.unvalidated_sum || 0
  // pct of expenses that ARE verified (totalExpenses - unvalidatedSum)
  const verifiedSum = Math.max(0, totalExpenses - unvalidatedSum)
  const pct = totalExpenses > 0 ? Math.round((verifiedSum / totalExpenses) * 100) : 100
  const safePct = Math.max(0, Math.min(100, pct))
  
  if (safePct >= 80) return {
    level: 'High', 
    iconClass: 'bg-success/10 text-success',
    message: `${safePct}% of expenses backed by eTIMS invoices. ${riskCount} items still need verification.`
  }
  if (safePct >= 50) return {
    level: 'Medium',
    iconClass: 'bg-warning/10 text-warning',
    message: `${safePct}% verified. ${riskCount} transactions are at risk of being disallowed by KRA.`
  }
  return {
    level: 'Low',
    iconClass: 'bg-danger/10 text-danger',
    message: `${safePct}% of expenses verified. Run eTIMS check for the ${riskCount} at-risk items to improve your audit readiness.`
  }
})

const handleDownloadSummary = async () => {
  downloadingPdf.value = true
  try {
    const res = await api.get(
      `/transactions/export-itax?type=purchases&month=${currentMonth}&year=${currentYear}`,
      { responseType: 'blob' }
    )
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `vatify_summary_${currentMonthName}_${currentYear}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success(`Summary exported for ${currentMonthName} ${currentYear}`)
  } catch (err) {
    toast.error('Export failed — no data for this period')
  } finally {
    downloadingPdf.value = false
  }
}

const handleScanEtims = async () => {
  const invoiceNum = prompt("Enter Sandbox eTIMS Invoice Number (e.g. KRACU0100058659/5134):", "KRACU0100058659/5134")
  if (!invoiceNum) return

  scanning.value = true
  try {
    await api.post(`/transactions/scan-etims?invoice_number=${encodeURIComponent(invoiceNum)}`)
    toast.success('eTIMS Sync Complete! Matched with records.')
    refreshSummary()
  } catch (err) {
    toast.error('Verification failed — check invoice details')
  } finally {
    scanning.value = false
  }
}
</script>

<style scoped>
.dashboard-v2 {
  width: 100%;
}

.hero-left h1 { letter-spacing: -0.05em; }

/* KPI Grid */
.premium-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.kpi-card {
  padding: 1.5rem;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.kpi-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
  border-color: var(--primary-light);
}

.kpi-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon-box.success { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.kpi-icon-box.danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.kpi-icon-box.info { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.kpi-icon-box.warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }

.kpi-header { display: flex; justify-content: space-between; align-items: center; }
.kpi-growth { font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 10px; }
.trend-up { background: #d1fae5; color: #065f46; }
.trend-warn { background: #fef3c7; color: #92400e; }
.trend-neutral { background: #f1f5f9; color: #475569; }

.kpi-label { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; margin-bottom: 0.5rem; }
.kpi-value { font-size: 1.6rem; color: var(--text-main); letter-spacing: -0.02em; }

.mini-progress { height: 4px; background: #f1f5f9; border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; transition: width 1s ease; }
.progress-fill.success { background: #10b981; }
.progress-fill.danger { background: #ef4444; }
.progress-fill.info { background: #3b82f6; }
.progress-fill.warning { background: #f59e0b; }

/* Dashboard Split */
.dashboard-content-split {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 2rem;
}

/* Custom Chart Bars */
.bar-fill {
  width: 44px;
  background: var(--bg-main);
  border-radius: 8px 8px 4px 4px;
  position: relative;
  transition: all 0.5s ease;
  cursor: pointer;
}

.bar-fill:hover { background: var(--primary-light); }
.bar-fill.active { background: var(--primary); }

.bar-tooltip {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--text-main);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}
.bar-fill:hover .bar-tooltip { opacity: 1; }

/* Activity Feed */
.activity-feed { display: flex; flex-direction: column; gap: 1rem; }
.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.act-icon-box {
  width: 32px;
  height: 32px;
  background: var(--bg-main);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.act-info { flex: 1; }
.act-amount { font-weight: 800; font-size: 0.8rem; }
.act-amount.income { color: var(--success); }
.act-amount.expense { color: var(--danger); }

/* Deadlines */
.deadline-item {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}
.deadline-item:last-child { border-bottom: none; }

.deadline-calendar {
  width: 44px;
  height: 44px;
  background: var(--bg-main);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.deadline-calendar .month { font-size: 9px; font-weight: 800; opacity: 0.6; }
.deadline-calendar .day { font-size: 16px; font-weight: 900; }

.status-indicator { width: 8px; height: 8px; border-radius: 50%; background: #e2e8f0; }
.status-indicator.warning { background: var(--warning); box-shadow: 0 0 8px var(--warning); }

/* Buttons */
.action-btn { justify-content: flex-start; gap: 0.75rem; padding: 0.75rem 1.25rem; }
.shadow-primary { box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.pulse.green {
  background: #10b981;
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

@media (max-width: 1100px) {
  .premium-kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .dashboard-content-split { grid-template-columns: 1fr; }
}
</style>
