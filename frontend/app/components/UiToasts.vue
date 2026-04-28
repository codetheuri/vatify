<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div 
        v-for="toast in toastState.toasts" 
        :key="toast.id" 
      >
        <div v-if="toast" :class="['toast', toast.type]">
          <div class="toast-icon">
            <CheckCircle2 v-if="toast.type === 'success'" :size="18" />
            <AlertCircle v-else-if="toast.type === 'error'" :size="18" />
            <Info v-else-if="toast.type === 'info'" :size="18" />
            <AlertTriangle v-else-if="toast.type === 'warning'" :size="18" />
          </div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-vue-next'
const toastState = useToast()

watch(() => toastState.toasts, (newValues) => {
  // Silent watch
}, { deep: true })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
}

.toast {
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  background: white;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 300px;
  max-width: 450px;
  pointer-events: auto;
  border-left: 4px solid #cbd5e1;
}

.toast-message {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-main);
}

.toast.success { border-left-color: var(--success); }
.toast.success .toast-icon { color: var(--success); }

.toast.error { border-left-color: var(--danger); }
.toast.error .toast-icon { color: var(--danger); }

.toast.info { border-left-color: var(--info); }
.toast.info .toast-icon { color: var(--info); }

.toast.warning { border-left-color: var(--warning); }
.toast.warning .toast-icon { color: var(--warning); }

/* Transition animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
