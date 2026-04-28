<template>
  <NuxtLayout>
    <div class="documents-page">
      <div class="header-actions mb-6 flex justify-between items-center">
        <div>
          <p class="text-muted text-sm">Upload eTIMS invoices, receipts, and KRA documents for AI processing.</p>
        </div>
        <div class="flex gap-3">
          <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" />
          <UiButton variant="primary" @click="fileInput.click()" :loading="uploading">
            <Upload :size="16" /> Upload Document
          </UiButton>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <UiCard class="md:col-span-1">
          <template #header>
            <h3>iTax Export Center</h3>
          </template>
          <div class="p-2">
            <p class="text-xs text-muted mb-4">Download KRA-compliant CSV templates for manual iTax portal upload.</p>
            <div class="flex flex-col gap-2">
              <UiButton variant="outline" block size="sm" @click="handleExport('purchases')">
                <FileSpreadsheet :size="16" /> Export Purchases CSV
              </UiButton>
              <UiButton variant="outline" block size="sm" @click="handleExport('sales')">
                <FileSpreadsheet :size="16" /> Export Sales CSV
              </UiButton>
            </div>
          </div>
        </UiCard>

        <UiCard class="md:col-span-2">
          <template #header>
            <div class="flex justify-between items-center">
              <h3>Recent Documents</h3>
              <UiButton variant="ghost" size="sm" @click="refresh">
                <RefreshCcw :size="14" /> Refresh
              </UiButton>
            </div>
          </template>

          <div v-if="pending" class="loading-state py-12 text-center">
            <div class="spinner mb-4"></div>
            <p class="text-muted">Loading documents...</p>
          </div>

          <div v-else-if="documents.length === 0" class="empty-state py-20 text-center">
            <div class="empty-icon mb-4">
               <FolderOpen :size="48" class="text-muted opacity-20" />
            </div>
            <p class="text-muted">No documents uploaded yet.</p>
            <UiButton variant="outline" size="sm" class="mt-4" @click="fileInput.click()">
              Upload your first invoice
            </UiButton>
          </div>

          <div v-else class="data-table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Extracted Vendor</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in documents" :key="doc.id">
                  <td class="font-medium">{{ doc.filename }}</td>
                  <td>
                    <span class="badge badge-info">{{ doc.document_type }}</span>
                  </td>
                  <td>{{ doc.extracted_vendor || (doc.doc_type === 'statement' ? 'M-Pesa Statement' : 'N/A') }}</td>
                  <td class="font-mono">KES {{ (doc.extracted_amount || 0).toLocaleString() }}</td>
                  <td>
                    <span v-if="doc.is_processed" class="badge badge-success">
                      <CheckCircle2 :size="12" /> Processed
                    </span>
                    <span v-else class="badge badge-warning">Processing</span>
                  </td>
                  <td class="text-muted text-sm">{{ formatDate(doc.created_at) }}</td>
                  <td>
                    <div class="flex gap-2">
                       <UiButton variant="ghost" size="xs" title="View Details">
                         <Eye :size="14" />
                       </UiButton>
                       <UiButton v-if="doc.transaction_id" variant="ghost" size="xs" class="text-success" title="Linked to Transaction">
                         <LinkIcon :size="14" />
                       </UiButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <!-- Pagination -->
            <UiPagination 
              :current-page="currentPage" 
              :total-items="totalItems" 
              :page-size="pageSize"
              @update:current-page="currentPage = $event"
              @update:page-size="pageSize = $event; currentPage = 1"
            />
          </div>
        </UiCard>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { 
  Upload, 
  RefreshCcw, 
  FolderOpen, 
  CheckCircle2, 
  Eye, 
  Link as LinkIcon,
  FileSpreadsheet
} from 'lucide-vue-next'

const api = useApi()
const toast = useToast()
const fileInput = ref(null)
const uploading = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)

const { data: fetchResult, pending, refresh } = await useAsyncData(
  'user-documents',
  () => api.get(`/documents/users/1?page=${currentPage.value}&per_page=${pageSize.value}`),
  {
    watch: [currentPage, pageSize]
  }
)

const documents = computed(() => {
  return Array.isArray(fetchResult.value?.dataPayload?.data) 
    ? fetchResult.value.dataPayload.data 
    : []
})

watch(fetchResult, (newVal) => {
  if (newVal?.dataPayload) {
    totalItems.value = newVal.dataPayload.totalCount
  }
}, { immediate: true })

const handleFileUpload = async (event) => {
  if (uploading.value) return
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.upload('/documents/upload', formData)
    await refresh()
    toast.success(res?.alertifyPayload?.message || 'Document uploaded successfully!')
  } catch (err) {
    toast.error('Failed to process document.')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const handleExport = async (type) => {
  try {
    const res = await api.get(`/transactions/export-itax?type=${type}&user_id=1`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `itax_${type}_export.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.info(`iTax ${type} report ready!`)
  } catch (err) {
    toast.error('Export failed')
  }
}

const formatDate = (timestamp) => {
  if (!timestamp) return '---'
  const ms = typeof timestamp === 'number' ? timestamp * 1000 : timestamp
  const date = new Date(ms)
  if (isNaN(date.getTime())) return '---'
  return date.toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.documents-page {
  display: flex;
  flex-direction: column;
}

.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

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

.badge-success {
  background-color: var(--success-light);
  color: var(--success);
}

.badge-info {
  background-color: var(--info-light);
  color: var(--info);
}
</style>
