<template>
  <NuxtLayout>
    <div class="returns-container">
      <!-- Top Section: Period Selector & Status -->
      <div class="returns-header section-glass mb-8">
        <div class="header-left">
          <h1 class="text-2xl font-extrabold text-main">Tax Returns Portal</h1>
          <p class="text-muted text-sm">Review, reconcile, and generate your iTax-ready files.</p>
        </div>

        <div class="header-right flex items-center gap-4">
          <div class="period-picker">
            <select v-model="selectedMonth" class="select-premium" @change="refreshData">
              <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
            </select>
            <select v-model="selectedYear" class="select-premium" @change="refreshData">
              <option :value="2026">2026</option>
              <option :value="2025">2025</option>
            </select>
          </div>
          <UiButton variant="ghost" size="sm" @click="refreshData">
            <RefreshCw :size="16" :class="{ 'animate-spin': pending }" />
          </UiButton>
        </div>
      </div>
      
      <!-- Taxpayer Profile Summary (Obligation Awareness) -->
      <div v-if="userData" class="obligation-alert mb-8">
        <div class="flex items-start gap-4 p-5 bg-white border border-border-color rounded-2xl shadow-sm">
          <div class="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
            <UserCircle :size="28" />
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
               <h3 class="font-black text-main text-base">{{ userData.business_name || userData.full_name }} — {{ userData.kra_pin }}</h3>
               <UiButton variant="ghost" size="xs" @click="syncObligations" :loading="syncing" class="h-7 px-2 text-[10px]">Sync with KRA</UiButton>
            </div>
            <div class="flex flex-wrap gap-2 mb-3">
               <span v-for="ob in obligationsList" :key="ob" class="badge-ob">
                 {{ ob }}
               </span>
            </div>
            <p class="text-xs text-slate-600 leading-relaxed max-w-3xl">
              <strong class="text-main">Compliance Profile:</strong> 
              <span v-if="isMonthlyFiler">
                You are registered for monthly obligations ({{ isVatRegistered ? 'VAT' : 'TOT' }}). 
                Even if you have no business activity this month, you <span class="font-bold text-danger">MUST file a NIL return</span> 
                by the 20th of next month to avoid automatic penalties.
              </span>
              <span v-else>
                You are currently an annual filer. While you don't have monthly filing obligations, 
                we recommend categorizing transactions monthly for an effortless June 30th return.
              </span>
            </p>
          </div>
        </div>
      </div>

      <div class="returns-layout">
        <!-- Dashboard Summary Row -->
        <div class="summary-grid mb-8" v-if="isMonthlyFiler">
          <UiCard class="summary-card" glass v-if="isVatRegistered">
            <div class="flex flex-col">
              <span class="text-xs font-bold text-muted uppercase tracking-wider mb-2">VAT on Sales (Output)</span>
              <span class="text-2xl font-black text-main mb-1">KES {{ (categorySummary?.grand_totals?.output_vat || 0).toLocaleString() }}</span>
              <span class="text-xs text-muted">from {{ (summary?.totals?.Income?.amount || 0).toLocaleString() }} sales</span>
            </div>
          </UiCard>

          <UiCard class="summary-card" glass v-if="isVatRegistered">
            <div class="flex flex-col">
              <span class="text-xs font-bold text-muted uppercase tracking-wider mb-2">VAT on Purchases (Input)</span>
              <span class="text-2xl font-black text-main mb-1">KES {{ (categorySummary?.grand_totals?.input_vat || 0).toLocaleString() }}</span>
              <span class="text-xs text-muted">from {{ (summary?.totals?.Expense?.amount || 0).toLocaleString() }} expenses</span>
            </div>
          </UiCard>

          <UiCard class="summary-card highlight" glass v-if="isVatRegistered">
            <div class="flex flex-col">
              <span class="text-xs font-bold text-white/80 uppercase tracking-wider mb-2">Net VAT {{ netVatPayable >= 0 ? 'Payable' : 'Credit' }}</span>
              <span class="text-3xl font-black text-white mb-1">KES {{ Math.abs(netVatPayable).toLocaleString() }}</span>
              <span class="text-xs text-white/70">Due by 20th {{ nextMonthName }}</span>
            </div>
          </UiCard>

          <UiCard class="summary-card" glass v-if="isTotRegistered">
            <div class="flex flex-col">
              <span class="text-xs font-bold text-muted uppercase tracking-wider mb-2">TOT Liability (Estimated)</span>
              <span class="text-2xl font-black text-main mb-1">KES {{ (summary?.totals?.Income?.amount * 0.03 || 0).toLocaleString() }}</span>
              <span class="text-xs text-muted">3% of {{ (summary?.totals?.Income?.amount || 0).toLocaleString() }} turnover</span>
            </div>
          </UiCard>
        </div>

        <!-- KRA Category Financial Breakdown -->
        <div v-if="categorySummary && isVatRegistered" class="breakdown-section mb-8">
            <div class="flex items-center justify-between gap-4">
               <div>
                  <h3 class="font-extrabold text-main text-lg">Step 4: Draft Review & Reconciliation</h3>
                  <p class="text-xs text-muted font-medium uppercase tracking-wider text-primary">Final Stage: Confirm these figures match your internal records</p>
               </div>
               <div class="flex items-center gap-2">
                 <span class="badge badge-primary text-[11px]">KRA Format</span>
                 <UiButton v-if="!draftReviewed" variant="primary" size="sm" @click="handleReviewComplete">
                   <ShieldCheck :size="14" /> Approve Figures for KRA Filing
                 </UiButton>
                 <span v-else class="badge badge-success px-4 py-2 font-black flex items-center gap-2">
                   <ShieldCheck :size="16" /> RECONCILIATION APPROVED
                 </span>
               </div>
            </div>

          <div class="breakdown-grid">
            <!-- Income Side -->
            <div class="breakdown-col">
              <div class="breakdown-col-header income">
                <TrendingUp :size="16" /> Income Sources (VAT Applicable)
              </div>
              <div class="breakdown-table">
                <div class="bt-row bt-head">
                  <span>Category</span><span>Txns</span><span>Total (KES)</span><span>Output VAT</span>
                </div>
                <div v-if="Object.keys(categorySummary.Income || {}).length === 0" class="bt-empty">
                  No income data for this period.
                </div>
                <div v-for="(data, cat) in categorySummary.Income" :key="cat" class="bt-row">
                  <span class="cat-name">{{ cat }}</span>
                  <span class="count-badge">{{ data.count }}</span>
                  <span class="font-bold">{{ data.total.toLocaleString() }}</span>
                  <span class="text-success font-bold">{{ data.vat.toLocaleString() }}</span>
                </div>
                <div class="bt-row bt-total">
                  <span>TOTAL</span>
                  <span>—</span>
                  <span>{{ (categorySummary.grand_totals?.income || 0).toLocaleString() }}</span>
                  <span class="text-success">{{ (categorySummary.grand_totals?.output_vat || 0).toLocaleString() }}</span>
                </div>
              </div>
            </div>

            <!-- Expense Side -->
            <div class="breakdown-col">
              <div class="breakdown-col-header expense">
                <TrendingDown :size="16" /> Expense Categories (VAT Deductible)
              </div>
              <div class="breakdown-table">
                <div class="bt-row bt-head">
                  <span>Category</span><span>Txns</span><span>Total (KES)</span><span>Input VAT</span>
                </div>
                <div v-if="Object.keys(categorySummary.Expense || {}).length === 0" class="bt-empty">
                  No expense data for this period.
                </div>
                <div v-for="(data, cat) in categorySummary.Expense" :key="cat" class="bt-row">
                  <span class="cat-name">{{ cat }}</span>
                  <span class="count-badge">{{ data.count }}</span>
                  <span class="font-bold">{{ data.total.toLocaleString() }}</span>
                  <span class="text-danger font-bold">{{ data.vat.toLocaleString() }}</span>
                </div>
                <div class="bt-row bt-total">
                  <span>TOTAL</span>
                  <span>—</span>
                  <span>{{ (categorySummary.grand_totals?.expenses || 0).toLocaleString() }}</span>
                  <span class="text-danger">{{ (categorySummary.grand_totals?.input_vat || 0).toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Net VAT Footer -->
          <div class="breakdown-net-footer" :class="netVatPayable >= 0 ? 'payable' : 'credit'">
            <span>Net VAT {{ netVatPayable >= 0 ? 'Payable' : 'Credit (Overpaid)' }}:</span>
            <span class="net-amt">KES {{ Math.abs(netVatPayable).toLocaleString() }}</span>
            <span class="text-xs opacity-70">Due by 20th {{ nextMonthName }}</span>
          </div>
        </div>

        <div v-if="!isVatRegistered && isMonthlyFiler" class="breakdown-section mb-8">
            <h3 class="font-extrabold text-main text-lg mb-2">Turnover Tax (TOT) Summary</h3>
            <p class="text-sm text-muted mb-6">Your estimated TOT liability at 3% of monthly gross turnover.</p>
            <div class="p-6 bg-slate-50 rounded-2xl border border-border-color">
               <div class="flex justify-between items-center">
                  <span class="font-bold text-main">Gross Monthly Turnover:</span>
                  <span class="text-xl font-black">KES {{ (summary?.totals?.Income?.amount || 0).toLocaleString() }}</span>
               </div>
               <div class="flex justify-between items-center mt-4 pt-4 border-t border-border-color">
                  <span class="font-bold text-primary">TOT Duty (3%):</span>
                  <span class="text-xl font-black text-primary">KES {{ (summary?.totals?.Income?.amount * 0.03 || 0).toLocaleString() }}</span>
               </div>
            </div>
        </div>

        <div class="main-returns-grid">
          <!-- Compliance Progress & Checklist -->
          <div class="col-left">
            <UiCard>
              <template #header><h3 class="card-title">Filing Readiness</h3></template>
              
              <div class="checklist mt-4">
                  <div 
                    v-for="(step, idx) in filingSteps" 
                    :key="idx" 
                    :class="['step-item', { 
                      done: step.checked, 
                      'cursor-pointer hover:opacity-100': step.title === 'Draft Review' && !step.checked,
                      'active-step': step.title === 'Draft Review' && !step.checked
                    }]"
                    @click="step.title === 'Draft Review' && !step.checked ? showReviewModal = true : null"
                  >
                  <div class="step-check">
                    <Check v-if="step.checked" :size="14" />
                    <span v-else class="text-[10px]">{{ idx + 1 }}</span>
                  </div>
                  <div class="step-label">
                    <p class="font-bold text-sm">{{ step.title }}</p>
                    <p class="text-xs text-muted">{{ step.desc }}</p>
                    <button v-if="step.title === 'Draft Review' && !step.checked" class="text-[10px] text-primary font-bold mt-1 underline">
                      Click to Review
                    </button>
                  </div>
                </div>
              </div>

              <div class="compliance-score-box mt-8">
                 <div class="score-circle">
                    <span class="score-num">{{ compliancePercentage }}%</span>
                 </div>
                 <div class="score-info">
                   <p class="font-bold text-sm">Status: {{ complianceStatus }}</p>
                   <p class="text-xs text-muted">{{ complianceAdvice }}</p>
                 </div>
              </div>
            </UiCard>
          </div>

          <!-- Download & Export Center -->
          <div class="col-right">
            <div class="export-options-grid">
              <UiCard hoverable class="export-card">
                <div class="flex items-start gap-4">
                  <div class="icon-box-primary">
                    <FileSpreadsheet :size="24" />
                  </div>
                  <div class="flex-1">
                    <h4 class="font-bold text-main">Purchases Report</h4>
                    <p class="text-xs text-muted mb-4">Formatted for KRA Offline Filler Section B (Inputs).</p>
                    <UiButton block variant="outline" size="sm" @click="handleExport('purchases')">
                      <Download :size="14" /> Download CSV
                    </UiButton>
                  </div>
                </div>
              </UiCard>

              <UiCard hoverable class="export-card">
                <div class="flex items-start gap-4">
                  <div class="icon-box-success">
                    <FileSpreadsheet :size="24" />
                  </div>
                  <div class="flex-1">
                    <h4 class="font-bold text-main">Sales Report</h4>
                    <p class="text-xs text-muted mb-4">Formatted for KRA Offline Filler Section A (Outputs).</p>
                    <UiButton block variant="outline" size="sm" @click="handleExport('sales')">
                      <Download :size="14" /> Download CSV
                    </UiButton>
                  </div>
                </div>
              </UiCard>
            </div>

            <!-- Filing Actions -->
            <div class="mt-8">
              <UiCard glass class="filing-box">
                <div class="flex items-center justify-between gap-6">
                  <div class="flex gap-4 items-center">
                    <ShieldCheck :size="40" class="text-primary opacity-40" />
                    <div>
                      <h4 class="font-bold text-main">KRA Sandbox Filing</h4>
                      <p class="text-xs text-muted max-w-sm">
                        Automatically transmit Nil returns or push reconciled totals to your iTax draft through our secure bridge.
                      </p>
                    </div>
                  </div>
                  <div class="flex gap-3">
                     <UiButton variant="ghost" @click="fileNil" :disabled="summary?.totals?.Income?.amount > 0">
                       {{ isMonthlyFiler ? 'File NIL' : 'Already Filed' }}
                     </UiButton>
                     <UiButton variant="primary" @click="showFilingModal = true" :disabled="compliancePercentage < 80 || !isMonthlyFiler">
                       Submit to iTax
                     </UiButton>
                  </div>
                </div>
              </UiCard>
            </div>

            <!-- Filing Guide -->
            <div class="mt-8">
               <h4 class="text-xs font-bold text-muted uppercase tracking-widest mb-4">Manual Filing Steps</h4>
               <div class="guide-steps">
                  <div class="g-step">
                    <div class="g-num">1</div>
                    <p class="text-sm">Download your categorized CSV from here and import it into your KRA Excel Macro file.</p>
                  </div>
                  <div class="g-step">
                    <div class="g-num">2</div>
                    <p class="text-sm">Click the "Validate" button within the Excel workbook to check for errors.</p>
                  </div>
                  <div class="g-step">
                    <div class="g-num">3</div>
                    <p class="text-sm">Upload the generated ZIP archive to the iTax portal under the Returns menu.</p>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filing Confirmation Modal -->
      <UiModal 
        :is-open="showFilingModal" 
        title="Ready to File?" 
        confirm-text="Push to iTax"
        @close="showFilingModal = false"
        @confirm="handleFinalSubmission"
        :loading="submitting"
      >
        <div class="text-center py-4">
          <div class="flex justify-center mb-6">
            <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
               <Zap :size="40" class="text-primary" />
            </div>
          </div>
          <h3 class="text-xl font-bold text-main mb-2">Transmit Data?</h3>
          <p class="text-sm text-muted px-6">
            You are about to push your reconciled totals for {{ selectedMonthName }} {{ selectedYear }} to the KRA iTax Sandbox.
            This will create a draft return on your portal.
          </p>
          <div class="mt-6 p-4 bg-bg-main rounded-xl border border-border-color text-left">
             <div class="flex justify-between text-sm mb-1">
               <span class="text-muted">Net VAT {{ netVatPayable >= 0 ? 'Payable' : 'Credit' }}:</span>
               <span class="font-bold">KES {{ Math.abs(netVatPayable).toLocaleString() }}</span>
             </div>
             <div class="flex justify-between text-sm">
               <span class="text-muted">Filing Readiness:</span>
               <span :class="compliancePercentage >= 80 ? 'text-success font-bold' : 'text-warning font-bold'">{{ compliancePercentage }}% Complete</span>
             </div>
          </div>
        </div>
      </UiModal>

      <!-- Step 4: Draft Review Modal -->
      <UiModal
        :is-open="showReviewModal"
        title="Tax Draft Reconcilation Review"
        confirm-text="Approve & Finalize Draft"
        size="lg"
        @close="showReviewModal = false"
        @confirm="handleReviewComplete"
      >
        <div class="review-modal-content">
          <div class="p-4 bg-primary/5 rounded-xl border border-primary/10 mb-6">
            <h4 class="font-bold text-primary text-sm flex items-center gap-2">
              <ShieldCheck :size="16" /> Audit Confirmation
            </h4>
            <p class="text-xs text-slate-600 mt-1">
              Please verify that the following totals match your expected figures for this period before we generate the KRA submission payload.
            </p>
          </div>

          <div class="review-grid grid grid-cols-2 gap-6">
            <div class="review-col">
              <h5 class="text-[11px] font-black uppercase text-muted mb-3">Output VAT (Sales)</h5>
              <div class="space-y-2">
                <div v-for="(data, cat) in categorySummary?.Income" :key="cat" class="flex justify-between text-xs p-2 bg-bg-main rounded border border-border-color">
                  <span>{{ cat }}</span>
                  <span class="font-bold">KES {{ data.vat.toLocaleString() }}</span>
                </div>
                <div class="flex justify-between text-xs p-2 font-black border-t-2 border-border-color pt-3">
                  <span>Total Output VAT</span>
                  <span class="text-success">KES {{ (categorySummary?.grand_totals?.output_vat || 0).toLocaleString() }}</span>
                </div>
              </div>
            </div>

            <div class="review-col">
              <h5 class="text-[11px] font-black uppercase text-muted mb-3">Input VAT (Purchases)</h5>
              <div class="space-y-2">
                <div v-for="(data, cat) in categorySummary?.Expense" :key="cat" class="flex justify-between text-xs p-2 bg-bg-main rounded border border-border-color">
                  <span>{{ cat }}</span>
                  <span class="font-bold">KES {{ data.vat.toLocaleString() }}</span>
                </div>
                <div class="flex justify-between text-xs p-2 font-black border-t-2 border-border-color pt-3">
                  <span>Total Input VAT</span>
                  <span class="text-danger">KES {{ (categorySummary?.grand_totals?.input_vat || 0).toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8 p-6 bg-slate-900 rounded-2xl text-white">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-bold text-white/60 uppercase tracking-widest">Net VAT {{ netVatPayable >= 0 ? 'Payable' : 'Credit' }}</p>
                <h3 class="text-3xl font-black mt-1">KES {{ Math.abs(netVatPayable).toLocaleString() }}</h3>
              </div>
              <div class="text-right">
                <p class="text-xs font-bold text-white/60 uppercase tracking-widest">Period</p>
                <p class="text-lg font-black">{{ selectedMonthName }} {{ selectedYear }}</p>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex items-start gap-3 p-4 bg-orange-50 rounded-xl border border-orange-100">
             <AlertTriangle :size="20" class="text-orange-500 flex-shrink-0" />
             <p class="text-xs text-orange-800 leading-relaxed">
               By finalizing this draft, you confirm that all expense transactions are backed by valid eTIMS invoices as per KRA Finance Act 2023 regulations.
             </p>
          </div>
        </div>
      </UiModal>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { 
  Download, RefreshCw, Check, FileSpreadsheet, 
  ShieldCheck, Zap, TrendingUp, TrendingDown,
  UserCircle, AlertTriangle
} from 'lucide-vue-next'

const api = useApi()
const toast = useToast()

const selectedMonth = ref(new Date().getMonth() + 1) // getMonth() is 0-indexed, +1 gives current month
const selectedYear = ref(2026)
const showFilingModal = ref(false)
const showReviewModal = ref(false)
const submitting = ref(false)
const syncing = ref(false)
const draftReviewed = ref(false)

const { data: userFetch, refresh: refreshUser } = await useAsyncData('user-details', () => api.get('/users/me'))
const userData = computed(() => userFetch.value?.dataPayload?.data)

const obligationsList = computed(() => {
  const obs = userData.value?.tax_obligations || 'Income Tax'
  return obs.split(',').map(o => o.trim())
})

const isVatRegistered = computed(() => obligationsList.value.some(o => o.toUpperCase().includes('VAT')))
const isTotRegistered = computed(() => obligationsList.value.some(o => o.toUpperCase().includes('TURNOVER') || o.toUpperCase().includes('TOT')))
const isMonthlyFiler = computed(() => isVatRegistered.value || isTotRegistered.value)

const syncObligations = async () => {
  syncing.value = true
  try {
    await api.post('/users/refresh-obligations')
    await refreshUser()
    toast.success('KRA Obligations synchronized!')
  } catch (err) {
    toast.error('Failed to sync with KRA Sandbox')
  } finally {
    syncing.value = false
  }
}

const months = [
  'January', 'February', 'March', 'April', 'May', 'June', 
  'July', 'August', 'September', 'October', 'November', 'December'
]

const selectedMonthName = computed(() => months[selectedMonth.value - 1])
const nextMonthName = computed(() => months[selectedMonth.value % 12])

const { data: summary, pending, refresh: refreshSummary } = await useAsyncData('period-summary', async () => {
  try {
    const res = await api.get(`/transactions/dashboard-summary?month=${selectedMonth.value}&year=${selectedYear.value}`)
    return res?.dataPayload?.data
  } catch (e) {
    return null
  }
}, { watch: [selectedMonth, selectedYear] })

const { data: categorySummary, refresh: refreshCatSummary } = await useAsyncData('category-summary', async () => {
  try {
    const res = await api.get(`/transactions/category-summary?month=${selectedMonth.value}&year=${selectedYear.value}`)
    return res?.dataPayload?.data
  } catch (e) {
    return null
  }
}, { watch: [selectedMonth, selectedYear] })

const netVat = computed(() => {
  const salesVat = summary.value?.totals?.Income?.tax || 0
  const purchaseVat = summary.value?.totals?.Expense?.tax || 0
  return Math.max(0, salesVat - purchaseVat)
})

const netVatPayable = computed(() => categorySummary.value?.grand_totals?.net_vat_payable ?? 0)

const filingSteps = computed(() => {
  const incomes = summary.value?.totals?.Income?.amount || 0
  const expenses = summary.value?.totals?.Expense?.amount || 0
  const riskCount = summary.value?.compliance_risk_count || 0
  
  const steps = [
    { title: 'Data Ingestion', desc: 'Upload M-Pesa or Bank CSV', checked: incomes > 0 || expenses > 0 },
    { title: 'AI Reconciliation', desc: 'Categorize all items', checked: incomes > 0 || expenses > 0 }
  ]

  // eTIMS Verification is mostly critical for VAT Input claims
  if (isVatRegistered.value) {
    steps.push({ 
      title: 'eTIMS Verification', 
      desc: 'Verify expense receipts', 
      checked: riskCount === 0 && (incomes > 0 || expenses > 0) 
    })
  }

  steps.push({ title: 'Draft Review', desc: 'Check VAT totals', checked: draftReviewed.value })
  
  return steps
})

const compliancePercentage = computed(() => {
  const steps = filingSteps.value
  const done = steps.filter(s => s.checked).length
  return Math.round((done / steps.length) * 100)
})

const complianceStatus = computed(() => {
  if (compliancePercentage.value < 50) return 'Incomplete'
  if (compliancePercentage.value < 85) return 'Review Needed'
  return 'Ready to File'
})

const complianceAdvice = computed(() => {
  if (compliancePercentage.value < 50) return 'Please upload more transaction data.'
  if (compliancePercentage.value < 85) return 'Verify items marked "At Risk".'
  return 'Your reconciliation looks clean.'
})

const refreshData = () => {
  refreshSummary()
  refreshCatSummary()
}

const handleExport = async (type) => {
  try {
    const res = await api.get(`/transactions/export-itax?type=${type}&month=${selectedMonth.value}&year=${selectedYear.value}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `itax_${type}_${selectedMonthName.value}_${selectedYear.value}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} export complete!`)
  } catch (err) {
    console.error('Export error:', err)
    toast.error('Failed to generate report')
  }
}

const fileNil = async () => {
  const pin = prompt("Confirm KRA PIN (Sandbox Demo):", "A521040203F")
  if (!pin) return

  const obligation = prompt("Obligation Code (1=Income Tax, 5=VAT):", "1")
  if (!obligation) return

  if (!confirm(`Are you sure you want to file a NIL return for ${pin} (Obligation ${obligation}) for ${selectedMonthName.value} ${selectedYear.value}?`)) return
  
  try {
    await api.post('/tax-periods/file-nil', {
      month: selectedMonth.value,
      year: selectedYear.value,
      obligation_code: obligation
    })
    toast.success('NIL Return filed successfully with KRA Sandbox!')
    refreshSummary()
  } catch (err) {
    toast.error('Filing failed: ' + (err.response?.data?.alertifyPayload?.message || 'Check PIN/Period details'))
  }
}

const handleReviewComplete = () => {
  draftReviewed.value = true
  showReviewModal.value = false
  toast.success('Draft review finalized! Figures approved for KRA transmission.')
  
  // Confetti effect or animation would go here for premium feel
}

const handleFinalSubmission = async () => {
  submitting.value = true
  try {
    await new Promise(r => setTimeout(r, 2000)) // Mock delay
    toast.success(`Data pushed to iTax Sandbox for ${selectedMonthName.value}!`)
    showFilingModal.value = false
  } finally {
     submitting.value = false
  }
}
</script>

<style scoped>
.returns-container {
  width: 100%;
}

.section-glass {
  background: white;
  padding: 1.5rem 2rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.select-premium {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-main);
  font-weight: 600;
  font-size: 0.9rem;
  outline: none;
  transition: var(--transition);
}

.select-premium:focus { border-color: var(--primary); }

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.summary-card {
  height: auto;
  border-left: 4px solid var(--primary);
  min-width: 0;
  overflow: hidden;
}

.summary-card .flex-col {
  min-width: 0;
}

.summary-card.highlight {
  background: linear-gradient(135deg, var(--primary), #1d4ed8);
  border-left: none;
}

/* Main Layout */
.main-returns-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  align-items: flex-start;
}

/* Checklist Styling */
.checklist {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.step-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  opacity: 0.5;
  transition: var(--transition);
}

.step-item.done { opacity: 1; }

.step-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1.5px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  transition: var(--transition);
}

.step-item.done .step-check {
  background: var(--success-light);
  border-color: var(--success);
  color: var(--success);
}

.compliance-score-box {
  background: var(--bg-main);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  border: 1px solid var(--border-color);
}

.score-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 4px solid var(--primary);
  border-top-color: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-num { font-weight: 800; font-size: 0.9rem; }

/* Exports */
.export-options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.export-card { height: auto; }

.icon-box-primary, .icon-box-success {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-box-primary { background: var(--primary-light); color: var(--primary); }
.icon-box-success { background: var(--success-light); color: var(--success); }

/* Filing Guide */
.guide-steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.g-step {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.g-num {
  width: 24px;
  height: 24px;
  background: var(--text-main);
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
}

.card-title { font-size: 1.1rem; font-weight: 800; }

/* Breakdown Section */
.breakdown-section {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem 2rem;
  box-shadow: var(--shadow-sm);
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.breakdown-col-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.breakdown-col-header.income { background: var(--success-light); color: var(--success); }
.breakdown-col-header.expense { background: var(--danger-light); color: var(--danger); }

.breakdown-table { border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden; }

.bt-row {
  display: grid;
  grid-template-columns: 1.8fr 0.5fr 1fr 1fr;
  padding: 0.7rem 1rem;
  font-size: 0.82rem;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
  transition: background 0.15s;
}
.bt-row:last-child { border-bottom: none; }
.bt-row:not(.bt-head):not(.bt-total):hover { background: var(--bg-main); }

.bt-head {
  background: #f8fafc;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.bt-total {
  background: #f1f5f9;
  font-weight: 800;
  font-size: 0.85rem;
  border-top: 2px solid var(--border-color);
}

.bt-empty {
  padding: 1.5rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.cat-name { font-weight: 600; color: var(--text-main); }
.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.1rem 0.5rem;
  width: fit-content;
}

.breakdown-net-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.25rem;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: 0.9rem;
}
.breakdown-net-footer.payable { background: var(--danger-light); color: var(--danger); }
.breakdown-net-footer.credit { background: var(--success-light); color: var(--success); }
.net-amt { font-size: 1.3rem; font-weight: 900; }

@media (max-width: 900px) {
  .breakdown-grid { grid-template-columns: 1fr; }
}
.obligation-alert {
  animation: slideIn 0.5s ease;
}

.badge-ob {
  background: var(--primary-light);
  color: var(--primary);
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  border: 1px solid rgba(37, 99, 235, 0.1);
}

@keyframes slideIn {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
