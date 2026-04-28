<template>
  <Transition name="modal">
    <div v-if="isOpen" class="modal-overlay" @click.self="closeOnOverlay">
      <div class="modal-container glass" :style="{ maxWidth: maxWidth }">
        <div class="modal-header">
          <slot name="header">
            <h3 class="modal-title">{{ title }}</h3>
          </slot>
          <button class="close-btn" @click="close">
            <X :size="20" />
          </button>
        </div>
        
        <div class="modal-body">
          <slot />
        </div>
        
        <div class="modal-footer" v-if="$slots.footer">
          <slot name="footer" />
        </div>
        <div class="modal-footer" v-else>
          <UiButton variant="ghost" @click="close">{{ cancelText }}</UiButton>
          <UiButton 
            :variant="confirmVariant" 
            @click="confirm" 
            :loading="loading"
          >
            {{ confirmText }}
          </UiButton>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { X } from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean,
  title: {
    type: String,
    default: 'Confirm Action'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  confirmVariant: {
    type: String,
    default: 'primary'
  },
  maxWidth: {
    type: String,
    default: '500px'
  },
  loading: Boolean,
  closeOnOverlayClick: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close', 'confirm'])

const close = () => emit('close')
const confirm = () => emit('confirm')
const closeOnOverlay = () => {
  if (props.closeOnOverlayClick) close()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: grid;
  place-items: center;
  z-index: 10000;
  padding: 1.5rem;
}

.modal-container {
  width: 100%;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  transition: var(--transition);
}

.close-btn:hover {
  background: var(--bg-main);
  color: var(--text-main);
}

.modal-body {
  padding: 1.5rem;
  font-size: 0.95rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.modal-footer {
  padding: 1rem 1.5rem;
  background: var(--bg-main);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid var(--border-color);
}

/* Modal Animations */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container {
  transform: scale(0.95) translateY(10px);
}

.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(10px);
}
</style>
