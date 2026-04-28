import { reactive } from 'vue'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration?: number
}

const state = reactive({
  toasts: [] as Toast[]
})

let nextId = 1

export const useToast = () => {
  const add = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    const id = nextId++
    state.toasts.push({ id, message, type, duration })

    setTimeout(() => {
      remove(id)
    }, duration)
  }

  const remove = (id: number) => {
    const index = state.toasts.findIndex(t => t.id === id)
    if (index !== -1) {
      state.toasts.splice(index, 1)
    }
  }

  return {
    toasts: state.toasts,
    success: (msg: string) => add(msg, 'success'),
    error: (msg: string) => add(msg, 'error'),
    info: (msg: string) => add(msg, 'info'),
    warning: (msg: string) => add(msg, 'warning')
  }
}
