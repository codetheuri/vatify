<template>
  <div class="transaction-list">
    <div class="table-actions mb-4 flex justify-between items-center">
      <div class="filters flex gap-2">
        <UiButton variant="outline" size="sm">All</UiButton>
        <UiButton variant="outline" size="sm">Verified</UiButton>
        <UiButton variant="outline" size="sm">At Risk</UiButton>
      </div>
      <div class="search">
        <input type="text" placeholder="Search transactions..." class="search-input" />
      </div>
    </div>

    <div class="data-table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Description</th>
            <th>Category</th>
            <th>Amount</th>
            <th>VAT</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactions" :key="tx.id" :class="{ 'is-new': tx.is_new }">
            <td class="whitespace-nowrap text-xs">{{ formatDate(tx.date) }}</td>
            <td>
              <span :class="['badge', tx.transaction_type === 'Income' ? 'badge-success' : 'badge-primary']">
                {{ tx.transaction_type }}
              </span>
            </td>
            <td class="font-medium">
              {{ tx.description }}
              <span v-if="tx.is_new" class="new-tag">NEW</span>
            </td>
            <td>
              <span class="category-pill">{{ tx.category || 'Uncategorized' }}</span>
            </td>
            <td class="text-right font-mono text-sm">KES {{ tx.amount?.toLocaleString() }}</td>
            <td class="text-right font-mono text-xs text-muted">{{ tx.tax_amount > 0 ? 'KES ' + tx.tax_amount.toLocaleString() : '-' }}</td>
            <td>
              <div v-if="tx.transaction_type === 'Expense'" class="flex">
                <span v-if="tx.etims_validated" class="badge badge-success items-center gap-1">
                  <CheckCircle2 :size="12" /> eTIMS Verified
                </span>
                <span v-else-if="tx.is_excluded_from_etims" class="badge badge-info items-center gap-1">
                  <Info :size="12" /> Excluded
                </span>
                <span v-else class="badge badge-warning items-center gap-1" title="Missing eTIMS Invoice">
                  <AlertTriangle :size="12" /> At Risk
                </span>
              </div>
              <span v-else class="badge badge-success-light">Standard Income</span>
            </td>
            <td>
              <div class="flex gap-2 items-center">
                <UiButton v-if="tx.transaction_type === 'Expense' && !tx.etims_validated && !tx.is_excluded_from_etims" 
                  variant="success-light" size="xs" @click="$emit('verify', tx)" class="row-verify-btn">
                   <ShieldCheck :size="12" /> Verify
                </UiButton>
                <UiButton variant="ghost" size="sm" icon-only @click="$emit('edit', tx)">
                   <Edit3 :size="14" />
                </UiButton>
              </div>
            </td>
          </tr>
          
          <!-- Empty State -->
          <tr v-if="transactions.length === 0">
            <td colspan="8" class="empty-state-cell">
              <div class="empty-state-content">
                <div class="empty-icon-box">
                   <FileSpreadsheet :size="48" class="text-muted opacity-20" />
                </div>
                <h4 class="text-lg font-semibold text-main mb-1">No transactions found</h4>
                <p class="text-muted text-sm max-w-xs mx-auto">
                  Upload an M-Pesa CSV or sync from your bank to see your financial activity and tax obligations.
                </p>
                <div class="mt-4 flex justify-center gap-3">
                   <UiButton variant="outline" size="sm" @click="$emit('upload-click')">
                      Upload Statement
                   </UiButton>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Footer -->
    <UiPagination 
      v-if="totalItems > pageSize"
      :current-page="currentPage" 
      :total-items="totalItems" 
      :page-size="pageSize"
      @update:current-page="$emit('update:currentPage', $event)"
      @update:page-size="$emit('update:pageSize', $event)"
    />
  </div>
</template>

<script setup>
import { CheckCircle2, Info, AlertTriangle, Edit3, FileSpreadsheet, ChevronLeft, ChevronRight, ShieldCheck } from 'lucide-vue-next'
import UiPagination from '~/components/ui/UiPagination.vue'
import UiButton from '~/components/ui/UiButton.vue'

const props = defineProps({
  transactions: {
    type: Array,
    required: true
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalItems: {
    type: Number,
    default: 0
  },
  pageSize: {
    type: Number,
    default: 10
  }
})

defineEmits(['view', 'edit', 'verify', 'update:currentPage', 'update:pageSize', 'upload-click'])

const formatDate = (dateString) => {
  if (!dateString) return '---'
  try {
    return new Date(dateString).toLocaleDateString('en-KE', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  } catch (e) {
    return 'Invalid Date'
  }
}
</script>

<style scoped>
.search-input {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  font-size: 0.875rem;
  width: 240px;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
}

.text-right { text-align: right; }
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
.font-medium { font-weight: 500; }
.is-new {
  background-color: #f0f9ff;
}

.new-tag {
  background: var(--primary);
  color: white;
  font-size: 0.6rem;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  vertical-align: middle;
  margin-left: 0.5rem;
}

.category-pill {
  font-size: 0.75rem;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  color: var(--text-muted);
}

.badge-success-light {
  background: var(--success-light);
  color: var(--success);
}

.empty-state-cell {
  padding: 5rem 0;
  background: #fafafa;
}

.empty-state-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.empty-icon-box {
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}
</style>
