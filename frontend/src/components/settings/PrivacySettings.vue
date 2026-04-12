<template>
  <div class="flex flex-col gap-4 w-full">
    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Privacy
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            Privacy Controls
          </div>
        </div>
      </div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        Control whether Ekachi may use your product interactions to improve the product experience over time. This does not change task execution behavior.
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-4">
        <div class="flex flex-col gap-2">
          <div class="text-base font-semibold text-[var(--text-primary)]">How We Handle Your Data</div>
          <div class="text-sm text-[var(--text-secondary)] leading-6">
            Ekachi only needs the data required to operate your sessions, projects, browser runs, and files. You can review the product-improvement preference below without changing core agent execution.
          </div>
        </div>
        <button
          type="button"
          class="shrink-0 rounded-[12px] border border-[var(--glass-border-strong)] p-2 text-[var(--text-secondary)] hover:bg-[var(--glass-surface-soft)]"
          @click="isDisclosureOpen = !isDisclosureOpen"
          :aria-expanded="isDisclosureOpen"
          aria-controls="privacy-disclosure"
        >
          <ChevronDown
            class="h-4 w-4 transition-transform"
            :class="isDisclosureOpen ? 'rotate-0' : '-rotate-90'"
          />
        </button>
      </div>

      <div
        v-if="isDisclosureOpen"
        id="privacy-disclosure"
        class="mt-4 border-t border-[var(--glass-border)] pt-4 text-sm text-[var(--text-secondary)] leading-6"
      >
        <ol class="list-decimal pl-5 space-y-2">
          <li>Task messages, browser context, and uploaded files are used to execute the workflows you request.</li>
          <li>The setting below only controls whether Ekachi may use product interactions to improve future product quality.</li>
          <li>Turning the preference off does not disable sessions, automation, browser control, or file operations.</li>
        </ol>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-4">
        <div class="flex flex-col gap-2">
          <div class="text-base font-semibold text-[var(--text-primary)]">Help Improve Ekachi</div>
          <div class="text-sm text-[var(--text-secondary)] leading-6">
            Allow Ekachi to use product interactions to improve future quality and reliability.
          </div>
        </div>
        <button
          type="button"
          role="switch"
          :aria-checked="helpImprove"
          :disabled="loading || saving"
          class="relative inline-flex h-8 w-14 items-center rounded-full border transition-colors disabled:opacity-50"
          :class="helpImprove ? 'border-transparent bg-[var(--Button-primray-black)]' : 'border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)]'"
          @click="toggleHelpImprove"
        >
          <span
            class="inline-block h-6 w-6 transform rounded-full bg-white transition-transform"
            :class="helpImprove ? 'translate-x-7' : 'translate-x-1'"
          />
        </button>
      </div>
      <div class="text-xs text-[var(--text-tertiary)] mt-3">
        {{ saving ? 'Saving privacy preference...' : loading ? 'Loading privacy preference...' : `Current setting: ${helpImprove ? 'Enabled' : 'Disabled'}` }}
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

import { getPrivacySettings, updatePrivacySettings } from '@/api/user'
import { showErrorToast, showSuccessToast } from '@/utils/toast'

const props = defineProps<{
  dialogOpen: boolean
}>()

const loading = ref(false)
const saving = ref(false)
const helpImprove = ref(false)
const isDisclosureOpen = ref(false)

const loadPrivacySettings = async () => {
  loading.value = true
  try {
    const settings = await getPrivacySettings()
    helpImprove.value = settings.help_improve
  } catch (error) {
    console.error('Failed to load privacy settings:', error)
    showErrorToast('Failed to load privacy settings')
  } finally {
    loading.value = false
  }
}

const toggleHelpImprove = async () => {
  const nextValue = !helpImprove.value
  helpImprove.value = nextValue
  saving.value = true
  try {
    const settings = await updatePrivacySettings({ help_improve: nextValue })
    helpImprove.value = settings.help_improve
    showSuccessToast('Privacy preference updated')
  } catch (error) {
    console.error('Failed to update privacy settings:', error)
    helpImprove.value = !nextValue
    showErrorToast('Failed to update privacy settings')
  } finally {
    saving.value = false
  }
}

watch(
  () => props.dialogOpen,
  (isOpen) => {
    if (isOpen) {
      void loadPrivacySettings()
    }
  },
  { immediate: true },
)
</script>
