<template>
  <div class="ui-input-wrapper">
    <label v-if="label" class="input-label">{{ label }}</label>
    <div class="input-container">
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="['ui-input', { error }]"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <span v-if="error" class="error-msg">{{ error }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  label: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  error: String,
  disabled: Boolean
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.ui-input-wrapper {
  margin-bottom: 1.25rem;
  width: 100%;
}

.input-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 0.5rem;
}

.ui-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: white;
  color: var(--text-main);
  transition: var(--transition);
}

.ui-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.ui-input.error {
  border-color: var(--danger);
}

.error-msg {
  display: block;
  font-size: 0.75rem;
  color: var(--danger);
  margin-top: 0.25rem;
}

.ui-input:disabled {
  background-color: #f8fafc;
  cursor: not-allowed;
}
</style>
