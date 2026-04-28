<template>
  <NuxtLayout>
      <div class="transactions-grid">
        <!-- Sidebar context -->
        <aside class="statements-sidebar">
          <div class="sidebar-header flex justify-between items-center mb-4">
            <h3 class="text-sm font-semibold">Statement History</h3>
            <UiButton variant="ghost" size="xs" @click="refreshStatements" :loading="statementsPending">
              <RefreshCw :size="12" />
            </UiButton>
          </div>
          
          <div v-if="statementsPending" class="py-4 text-center">
            <Loader2 class="animate-spin text-muted mx-auto" :size="20" />
          </div>
          <div v-else-if="statements?.length === 0" class="text-xs text-muted py-4 text-center">
            No statements uploaded yet.
          </div>
          <div v-else class="statement-list">
            <div 
              v-for="stmt in statements" 
              :key="stmt.id" 
              :class="['statement-item group', { active: filters.documentId === stmt.id }]"
              @click="toggleBatch(stmt.id)"
            >
              <div class="flex items-center justify-between gap-2 mb-1">
                <div class="flex items-center gap-2 truncate">
                  <FileSpreadsheet :size="14" class="text-primary" />
                  <span class="stmt-name truncate">{{ stmt.filename }}</span>
                </div>
                <button 
                  class="delete-btn opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-danger/10 hover:text-danger rounded"
                  @click.stop="confirmDelete(stmt)"
                >
                  <Trash2 :size="12" />
                </button>
              </div>
              <div class="flex justify-between items-center">
                 <span class="text-[10px] text-muted">{{ formatDateShort(stmt.created_at) }}</span>
                 <span class="badge badge-success-light text-[10px]">Categorized</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- Main Content -->
        <div class="main-table-view">
          <div class="header-actions mb-6 flex justify-between items-center">
            <div>
                <div class="flex items-center gap-2 mb-1">
                  <h2 class="text-xl font-bold">Financial Activity</h2>
                  <span v-if="totalItems > 0" class="text-xs bg-bg-main px-2 py-0.5 rounded-full border border-border-color">
                    {{ totalItems }} items
                  </span>
                </div>
                <p class="text-muted text-sm" v-if="activeStatement">
                 Showing results for <strong>{{ activeStatement.filename }}</strong>
                </p>
                <p class="text-muted text-sm" v-else>
                 Reviewing all reconciled M-Pesa activity.
                </p>
            </div>
            <div class="flex gap-3">
              <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" accept=".csv,.pdf" />
              <UiButton variant="outline" @click="fileInput.click()" :loading="uploading">
                <FileUp :size="16" /> Upload Statement
              </UiButton>
              <UiButton variant="outline" @click="handleAiCategorize" :loading="categorizing" class="border-sparkle">
                <Sparkles :size="16" class="text-primary" /> Run AI Categorize
              </UiButton>
            </div>
          </div>

      <!-- Filters -->
      <div class="filters-row mb-6 flex gap-4 items-end">
        <div class="filter-group">
          <label class="text-xs text-muted mb-1 block">Transaction Type</label>
          <select v-model="filters.type" class="filter-select">
            <option value="all">All Types</option>
            <option value="Income">Income</option>
            <option value="Expense">Expense</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="text-xs text-muted mb-1 block">Compliance Status</label>
          <select v-model="filters.status" class="filter-select">
            <option value="all">All Status</option>
            <option value="verified">Verified</option>
            <option value="missing">No Invoice</option>
            <option value="excluded">Excluded</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="text-xs text-muted mb-1 block">Quick Date</label>
          <select v-model="filters.dateRange" class="filter-select">
            <option value="all">All Periods</option>
            <option value="this-month">This Month</option>
            <option value="last-month">Last Month</option>
          </select>
        </div>
        <UiButton variant="ghost" size="sm" @click="resetFilters">
          Reset Filters
        </UiButton>
      </div>

          <UiCard>
            <div v-if="pending" class="loading-state py-20 text-center">
              <div class="spinner mb-4"></div>
              <p class="text-muted">Fetching transactions...</p>
            </div>
            <div v-else>
               <TransactionTable 
                  :transactions="transactions" 
                  :current-page="currentPage"
                  :total-items="totalItems"
                  :page-size="pageSize"
                  @update:current-page="currentPage = $event"
                  @update:page-size="pageSize = $event; currentPage = 1"
                  @upload-click="fileInput.click()"
                  @verify="handleVerifyRow"
               />
               <div v-if="transactions.length === 0" class="text-center py-20 text-muted">
                  <p>No transactions found. Upload a statement to get started.</p>
               </div>
            </div>
          </UiCard>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <UiModal 
        :is-open="deleteModal.isOpen"
        title="Remove Statement Batch"
        confirm-text="Delete Everything"
        confirm-variant="danger"
        :loading="deleteModal.loading"
        @close="deleteModal.isOpen = false"
        @confirm="handleDeleteBatch"
      >
        <div class="delete-confirmation">
          <div class="confirm-icon-wrapper">
             <Trash2 :size="32" />
          </div>
          <h4 class="confirm-title">Are you absolutely sure?</h4>
          <p class="confirm-text">
            You are about to delete <strong>{{ deleteModal.statement?.filename }}</strong>. 
            This will permanently remove all categorized transactions linked to this statement from your tax records.
          </p>
        </div>
      </UiModal>
  </NuxtLayout>
</template>

<script setup>
import { FileUp, Sparkles, Loader2, FileSpreadsheet, RefreshCw, Trash2 } from 'lucide-vue-next'

const { user } = useAuth()
const obligations = computed(() => user.value?.tax_obligations || 'Income Tax')
const isVatRegistered = computed(() => obligations.value.toUpperCase().includes('VAT'))
const api = useApi()
const toast = useToast()
const fileInput = ref(null)
const uploading = ref(false)
const categorizing = ref(false)

const deleteModal = reactive({
  isOpen: false,
  loading: false,
  statement: null
})

const filters = reactive({
  type: 'all',
  status: 'all',
  dateRange: 'all',
  documentId: null
})

const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)

const { data: fetchResult, pending, refresh } = await useAsyncData(
  'transactions',
  () => {
    let url = `/transactions/?page=${currentPage.value}&per_page=${pageSize.value}`
    if (filters.documentId) url += `&document_id=${filters.documentId}`
    if (filters.type !== 'all') url += `&transaction_type=${filters.type}`
    
    if (filters.status === 'verified') url += '&etims_validated=true'
    else if (filters.status === 'missing') url += '&etims_validated=false'
    else if (filters.status === 'excluded') url += '&is_excluded=true'
    
    return api.get(url)
  },
  {
    watch: [currentPage, pageSize, filters]
  }
)

const transactions = computed(() => {
  return Array.isArray(fetchResult.value?.dataPayload?.data) 
    ? fetchResult.value.dataPayload.data 
    : []
})

watch(fetchResult, (newVal) => {
  if (newVal?.dataPayload) {
    totalItems.value = newVal.dataPayload.totalCount
  }
}, { immediate: true })

const { data: allDocuments, pending: statementsPending, refresh: refreshStatements } = await useAsyncData('statement-docs', async () => {
  try {
    const res = await api.get('/documents/')
    return res?.dataPayload?.data || []
  } catch (e) {
    return []
  }
})

const statements = computed(() => {
  if (!Array.isArray(allDocuments.value)) return []
  // For documents page, allDocuments.value is already documented as having items/total structure if paginated
  // But documents list in sidebar might be smaller so we might not paginate it or just show all
  const list = allDocuments.value?.items || allDocuments.value || []
  return list.filter(d => d.document_type === 'Statement')
})

const activeStatement = computed(() => {
  if (!filters.documentId) return null
  return statements.value.find(s => s.id === filters.documentId)
})

const handleFileUpload = async (event) => {
  if (uploading.value) return
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.upload('/transactions/upload', formData)
    
    await Promise.all([refresh(), refreshStatements()])
    
    if (res?.dataPayload?.data?.document_id) {
       filters.documentId = res.dataPayload.data.document_id
    }

    toast.success(res?.alertifyPayload?.message || 'Statement processed successfully!')
  } catch (err) {
    toast.error('Failed to upload statement.')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const handleAiCategorize = async () => {
  if (categorizing.value) return
  categorizing.value = true
  try {
    const url = filters.documentId 
      ? `/transactions/re-categorize?document_id=${filters.documentId}` 
      : '/transactions/re-categorize'
    
    await api.post(url)
    await refresh()
    toast.success('AI categorization complete!')
  } catch (err) {
    toast.error('AI categorization failed')
  } finally {
    categorizing.value = false
  }
}

const resetFilters = () => {
  filters.type = 'all'
  filters.status = 'all'
  filters.dateRange = 'all'
  filters.documentId = null
}

const toggleBatch = (id) => {
  if (filters.documentId === id) filters.documentId = null
  else filters.documentId = id
  currentPage.value = 1
}

const confirmDelete = (stmt) => {
  deleteModal.statement = stmt
  deleteModal.isOpen = true
}

const handleDeleteBatch = async () => {
  const stmt = deleteModal.statement
  if (!stmt) return
  
  deleteModal.loading = true
  try {
     await api.delete(`/documents/${stmt.id}`)
     toast.success('Batch removed successfully.')
     if (filters.documentId === stmt.id) filters.documentId = null
     await Promise.all([refresh(), refreshStatements()])
  } catch (err) {
     toast.error('Delete failed.')
  } finally {
     deleteModal.loading = false
     deleteModal.isOpen = false
  }
}

const formatDateShort = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-KE', {
    day: '2-digit', month: 'short'
  })
}

// Watch filters to reset page
watch(filters, () => {
  currentPage.value = 1
}, { deep: true })

const handleVerifyRow = async (tx) => {
  const invoiceNum = prompt(`Enter eTIMS Invoice for ${tx.description} (KES ${tx.amount}):`, "KRACU0100058659/5134")
  if (!invoiceNum) return
  
  try {
    await api.post(`/transactions/scan-etims?invoice_number=${encodeURIComponent(invoiceNum)}`)
    toast.success('Transaction Verified!')
    refresh()
  } catch (err) {
    toast.error('Verification failed.')
  }
}

</script>

<style scoped>
.transactions-grid {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 2rem;
  align-items: start;
}

.statements-sidebar {
  background: white;
  padding: 1.25rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  position: sticky;
  top: 90px;
}

.statement-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.statement-item {
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: var(--transition);
}

.statement-item:hover {
  background: var(--bg-main);
  border-color: var(--border-color);
}

.statement-item.active {
  background: var(--primary-light);
  border-color: var(--primary);
}

.stmt-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-main);
}

.delete-btn {
  color: var(--text-muted);
  border: none;
  background: transparent;
}

.filters-row {
  background: white;
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.filter-select {
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  font-size: 0.8rem;
  min-width: 150px;
}

.delete-confirmation {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem 0;
}

.confirm-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--primary-light);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
