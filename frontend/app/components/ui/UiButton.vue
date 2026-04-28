<template>
  <component 
    :is="to ? 'NuxtLink' : 'button'"
    :to="to"
    :class="['ui-button', variant, size, { loading, block }]" 
    :disabled="!to && (disabled || loading)"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="loader"></span>
    <slot v-else />
  </component>
</template>

<script setup>
defineProps({
  to: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'primary' // primary, secondary, outline, danger, ghost
  },
  size: {
    type: String,
    default: 'md' // sm, md, lg
  },
  loading: Boolean,
  disabled: Boolean,
  block: Boolean
})
defineEmits(['click'])
</script>

<style scoped>
.ui-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: var(--transition);
  cursor: pointer;
  border: 1px solid transparent;
  white-space: nowrap;
  gap: 0.5rem;
}

.ui-button.block { width: 100%; }

/* Sizes */
.sm { padding: 0.4rem 0.8rem; font-size: 0.75rem; }
.md { padding: 0.6rem 1.2rem; font-size: 0.875rem; }
.lg { padding: 0.8rem 1.6rem; font-size: 1rem; }

/* Variants */
.primary {
  background-color: var(--primary);
  color: white;
}
.primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.secondary {
  background-color: var(--secondary);
  color: white;
}
.secondary:hover:not(:disabled) {
  background-color: #475569;
}

.outline {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--text-main);
}
.outline:hover:not(:disabled) {
  background-color: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary);
}

.danger {
  background-color: var(--danger);
  color: white;
}
.danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.ghost {
  background: transparent;
  color: var(--text-muted);
}
.ghost:hover:not(:disabled) {
  background: var(--primary-light);
  color: var(--primary);
}

.loader {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.primary .loader, .secondary .loader, .danger .loader {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
