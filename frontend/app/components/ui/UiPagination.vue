<template>
  <div class="ui-pagination flex items-center justify-between py-4">
    <div class="pagination-info text-xs text-muted">
      Showing <span class="font-bold text-main">{{ totalItems > 0 ? startItem : 0 }}</span> to <span class="font-bold text-main">{{ endItem }}</span> of <span class="font-bold text-main">{{ totalItems }}</span> items
    </div>

    <div class="pagination-actions flex items-center gap-6">
      <div class="per-page-selector flex items-center gap-2">
        <span class="text-[10px] text-muted uppercase font-bold tracking-wider">Per Page:</span>
        <select 
          :value="pageSize" 
          @change="$emit('update:pageSize', parseInt($event.target.value))"
          class="page-select text-xs font-bold"
        >
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
      </div>
      
      <div class="pagination-controls flex items-center gap-1">
        <UiButton 
          variant="outline" 
          size="sm" 
          :disabled="currentPage === 1"
          class="nav-btn"
          @click="$emit('update:currentPage', currentPage - 1)"
        >
          <ChevronLeft :size="14" />
          <span class="ml-1 hidden sm:inline">Prev</span>
        </UiButton>
        
        <div class="page-numbers flex gap-1 mx-1">
          <template v-for="page in pagesToShow" :key="page">
            <span v-if="page === '...'" class="dots">...</span>
            <UiButton 
              v-else
              :variant="currentPage === page ? 'primary' : 'ghost'" 
              size="sm"
              class="page-btn"
              :class="{ 'active': currentPage === page }"
              @click="$emit('update:currentPage', page)"
            >
              {{ page }}
            </UiButton>
          </template>
        </div>
        
        <UiButton 
          variant="outline" 
          size="sm" 
          :disabled="currentPage === totalPages || totalPages === 0"
          class="nav-btn"
          @click="$emit('update:currentPage', currentPage + 1)"
        >
          <span class="mr-1 hidden sm:inline">Next</span>
          <ChevronRight :size="14" />
        </UiButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    default: 10
  }
})

defineEmits(['update:currentPage', 'update:pageSize'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize))
const startItem = computed(() => (props.currentPage - 1) * props.pageSize + 1)
const endItem = computed(() => Math.min(props.currentPage * props.pageSize, props.totalItems))

const pagesToShow = computed(() => {
  const current = props.currentPage
  const total = totalPages.value
  const delta = 1
  const range = []
  const rangeWithDots = []
  let l

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i)
    }
  }

  for (let i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1)
      } else if (i - l !== 1) {
        rangeWithDots.push('...')
      }
    }
    rangeWithDots.push(i)
    l = i
  }

  return rangeWithDots
})
</script>

<script>
export default {
  name: 'UiPagination'
}
</script>

<style scoped>
.ui-pagination {
  border-top: 1px solid var(--border-color);
  margin-top: 1rem;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
}

.page-btn.active {
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.2);
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(var(--main-rgb), 0.08);
  flex-wrap: wrap;
  gap: 1rem;
}

.page-select {
  background: rgba(var(--main-rgb), 0.05);
  border: 1px solid rgba(var(--main-rgb), 0.1);
  color: var(--text-main);
  border-radius: 6px;
  padding: 2px 8px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-select:hover {
  background: rgba(var(--main-rgb), 0.08);
  border-color: rgba(var(--main-rgb), 0.2);
}

.page-select option {
  background: #1a1b1e; /* Matches dark theme card background */
  color: white;
}

.nav-btn {
  height: 32px;
  font-size: 0.8125rem;
}

.dots {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  color: var(--text-muted);
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .pagination-info {
    display: none;
  }
  .ui-pagination {
    justify-content: center;
  }
}
</style>
