<template>
  <span
    class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs border"
    :class="active
      ? 'border-[rgba(0,129,242,0.22)] bg-[var(--fill-blue)] text-[var(--text-primary)]'
      : 'border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] text-[var(--text-secondary)]'"
  >
    <span
      class="w-2 h-2 rounded-full"
      :class="active ? 'bg-[var(--function-success)]' : 'bg-[var(--text-disable)]'"
    />
    {{ labelText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  active: boolean
  label?: string
}>()

const labelText = computed(() => props.label || (props.active ? 'Configured' : 'Not configured'))
</script>
