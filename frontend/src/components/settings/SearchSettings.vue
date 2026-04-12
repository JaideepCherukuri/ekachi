<template>
  <div class="flex flex-col gap-4 w-full">
    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Active Search
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            {{ activeSearchProvider }}
          </div>
        </div>
        <div class="px-3 py-1.5 rounded-full text-xs border border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] text-[var(--text-secondary)]">
          Environment-managed
        </div>
      </div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        The backend is already capable of switching search providers. This surface exposes what is live today and what the runtime supports, without exposing secrets.
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">Supported Providers</div>
      <div class="text-sm text-[var(--text-secondary)] mt-1">
        Ekachi currently supports these search backends in code.
      </div>
      <div class="flex flex-wrap gap-2 mt-4">
        <span
          v-for="provider in controlPlaneConfig?.supported_search_providers || []"
          :key="provider"
          class="px-3 py-1.5 rounded-full text-sm border"
          :class="provider === controlPlaneConfig?.search_provider
            ? 'border-[var(--text-brand)] bg-[var(--fill-blue)] text-[var(--text-primary)]'
            : 'border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] text-[var(--text-secondary)]'"
        >
          {{ provider }}
        </span>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Active Project Search Preference</div>
          <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
            Choose which search backend new sessions in the current project should use.
          </div>
        </div>
        <button
          @click="saveSearchPreference"
          :disabled="saving || activeProject.system"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
        >
          {{ saving ? 'Saving...' : 'Save Preference' }}
        </button>
      </div>
      <div class="mt-4">
        <Select v-model="selectedSearchProvider">
          <SelectTrigger class="w-full md:w-[320px] h-[42px]">
            <SelectValue placeholder="System default" />
          </SelectTrigger>
          <SelectContent :side-offset="6">
            <SelectItem :value="SYSTEM_DEFAULT_VALUE">System default</SelectItem>
            <SelectItem
              v-for="provider in controlPlaneConfig?.supported_search_providers || []"
              :key="provider"
              :value="provider"
            >
              {{ provider }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="text-xs text-[var(--text-tertiary)] mt-3">
        {{ activeProject.system ? 'Inbox uses the environment default search provider.' : `Editing ${activeProject.name}.` }}
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { ControlPlaneConfigResponse } from '@/api/config'
import { updateProject } from '@/api/projects'
import { useProjects } from '@/composables/useProjects'
import { showErrorToast, showSuccessToast } from '@/utils/toast'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const props = defineProps<{
  controlPlaneConfig: ControlPlaneConfigResponse | null
}>()

const activeSearchProvider = computed(() => props.controlPlaneConfig?.search_provider || 'Unavailable')
const SYSTEM_DEFAULT_VALUE = '__system_default__'
const saving = ref(false)

const { activeProjectId, getProjectById, hydrateProjects } = useProjects()

const activeProject = computed(() => getProjectById(activeProjectId.value))
const selectedSearchProvider = ref<string>(SYSTEM_DEFAULT_VALUE)

watch(activeProject, (project) => {
  selectedSearchProvider.value = project.preferred_search_provider || SYSTEM_DEFAULT_VALUE
}, { immediate: true })

const saveSearchPreference = async () => {
  if (activeProject.value.system) return
  saving.value = true
  try {
    await updateProject(activeProject.value.id, {
      preferred_search_provider: selectedSearchProvider.value === SYSTEM_DEFAULT_VALUE ? '' : selectedSearchProvider.value,
    })
    await hydrateProjects(true)
    showSuccessToast('Project search preference saved')
  } catch (error) {
    console.error('Failed to save project search preference:', error)
    showErrorToast('Failed to save project search preference')
  } finally {
    saving.value = false
  }
}
</script>
