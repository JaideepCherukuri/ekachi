<template>
  <div class="flex flex-col gap-4 w-full">
    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex flex-col gap-2">
        <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
          System Runtime
        </div>
        <div class="text-[22px] font-semibold text-[var(--text-primary)]">
          {{ controlPlaneConfig?.default_model_name || 'Unavailable' }}
        </div>
        <div class="text-sm text-[var(--text-secondary)]">
          Current provider:
          <span class="font-medium text-[var(--text-primary)]">{{ controlPlaneConfig?.model_provider || 'unknown' }}</span>
        </div>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Active Project Default</div>
          <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
            Choose the provider and model new sessions should use inside the current project.
          </div>
        </div>
        <button
          @click="saveProjectModelPreference"
          :disabled="savingProject || activeProject.system || !selectedProjectProviderId"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
        >
          {{ savingProject ? 'Saving...' : 'Save Preference' }}
        </button>
      </div>
      <div class="grid gap-3 mt-4 md:grid-cols-2">
        <div class="flex flex-col gap-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Provider</label>
          <Select v-model="selectedProjectProviderId">
            <SelectTrigger class="w-full h-[42px]">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent :side-offset="6">
              <SelectItem
                v-for="provider in enabledProviders"
                :key="provider.provider_id"
                :value="provider.provider_id"
              >
                {{ provider.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Model</label>
          <Select v-model="selectedProjectModel">
            <SelectTrigger class="w-full h-[42px]">
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent :side-offset="6">
              <SelectItem
                v-for="model in projectProviderModels"
                :key="model"
                :value="model"
              >
                {{ model }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div class="text-xs text-[var(--text-tertiary)] mt-3">
        {{ activeProject.system ? 'Inbox follows the system runtime.' : `Editing ${activeProject.name}.` }}
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Provider Profiles</div>
          <div class="text-sm text-[var(--text-secondary)] mt-2">
            Create provider profiles, test them live, and choose which ones are available for new sessions.
          </div>
        </div>
        <button
          @click="startCreate"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
        >
          New Provider
        </button>
      </div>

      <div class="grid gap-3 mt-4">
        <div
          v-for="provider in providers"
          :key="provider.provider_id"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
        >
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <div class="text-sm font-semibold text-[var(--text-primary)]">{{ provider.label }}</div>
                <span class="px-2 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]">
                  {{ provider.model_provider }}
                </span>
                <span
                  class="px-2 py-1 rounded-full text-[11px] border"
                  :class="provider.enabled ? 'border-emerald-400/40 text-emerald-700' : 'border-[var(--glass-border)] text-[var(--text-tertiary)]'"
                >
                  {{ provider.enabled ? 'Enabled' : 'Disabled' }}
                </span>
                <span
                  v-if="provider.is_system"
                  class="px-2 py-1 rounded-full text-[11px] border border-sky-400/40 text-sky-700"
                >
                  System
                </span>
              </div>
              <div class="text-xs text-[var(--text-tertiary)] mt-2">
                Default model: {{ provider.default_model_name }}
              </div>
              <div class="text-xs text-[var(--text-tertiary)] mt-1 break-all">
                Endpoint: {{ provider.api_base || 'Provider default endpoint' }}
              </div>
              <div class="text-xs text-[var(--text-tertiary)] mt-1">
                API key: {{ provider.has_api_key ? 'configured' : 'not configured' }}
              </div>
              <div class="flex flex-wrap gap-2 mt-3">
                <span
                  v-for="model in provider.available_models"
                  :key="`${provider.provider_id}-${model}`"
                  class="px-3 py-1.5 rounded-full text-xs border border-[var(--glass-border-strong)] bg-white/60 text-[var(--text-primary)]"
                >
                  {{ model }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                @click="runProviderTest(provider)"
                :disabled="testingProviderId === provider.provider_id"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-sm text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
              >
                {{ testingProviderId === provider.provider_id ? 'Testing...' : 'Test' }}
              </button>
              <button
                v-if="!provider.is_system"
                @click="startEdit(provider)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-sm text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
              >
                Edit
              </button>
              <button
                v-if="!provider.is_system"
                @click="removeProvider(provider)"
                :disabled="deletingProviderId === provider.provider_id"
                class="px-3 py-2 rounded-[12px] border border-rose-300/60 text-sm text-rose-700 hover:bg-rose-50 disabled:opacity-50"
              >
                {{ deletingProviderId === provider.provider_id ? 'Deleting...' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">
            {{ editingProviderId ? 'Edit Provider' : 'Create Provider' }}
          </div>
          <div class="text-sm text-[var(--text-secondary)] mt-2">
            Provider profiles are stored server-side and selected at session creation time.
          </div>
        </div>
        <button
          @click="resetForm"
          class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-sm text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
        >
          Reset
        </button>
      </div>

      <div class="grid gap-3 mt-4 md:grid-cols-2">
        <div class="flex flex-col gap-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Label</label>
          <input
            v-model="form.label"
            type="text"
            class="w-full rounded-[14px] border border-[var(--glass-border-strong)] bg-white/70 px-3 py-2 text-sm text-[var(--text-primary)] outline-none"
            placeholder="OpenAI Production"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Provider Type</label>
          <Select v-model="form.model_provider">
            <SelectTrigger class="w-full h-[42px]">
              <SelectValue placeholder="Select provider type" />
            </SelectTrigger>
            <SelectContent :side-offset="6">
              <SelectItem v-for="option in providerTypeOptions" :key="option" :value="option">
                {{ option }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">API Base</label>
          <input
            v-model="form.api_base"
            type="text"
            class="w-full rounded-[14px] border border-[var(--glass-border-strong)] bg-white/70 px-3 py-2 text-sm text-[var(--text-primary)] outline-none"
            placeholder="https://api.openai.com/v1"
          />
        </div>
        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Available Models</label>
          <textarea
            v-model="form.available_models_text"
            rows="5"
            class="w-full rounded-[14px] border border-[var(--glass-border-strong)] bg-white/70 px-3 py-2 text-sm text-[var(--text-primary)] outline-none"
            placeholder="gpt-5.4&#10;gpt-5.4-mini"
          />
          <div class="text-xs text-[var(--text-tertiary)]">One model per line.</div>
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Default Model</label>
          <Select v-model="form.default_model_name">
            <SelectTrigger class="w-full h-[42px]">
              <SelectValue placeholder="Select default model" />
            </SelectTrigger>
            <SelectContent :side-offset="6">
              <SelectItem v-for="model in parsedFormModels" :key="model" :value="model">
                {{ model }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">API Key</label>
          <input
            v-model="form.api_key"
            type="password"
            class="w-full rounded-[14px] border border-[var(--glass-border-strong)] bg-white/70 px-3 py-2 text-sm text-[var(--text-primary)] outline-none"
            :placeholder="editingProviderHasApiKey ? 'Leave blank to keep existing key' : 'sk-...'"
          />
        </div>
      </div>

      <div class="flex items-center gap-5 flex-wrap mt-4">
        <label class="inline-flex items-center gap-2 text-sm text-[var(--text-primary)]">
          <input v-model="form.enabled" type="checkbox" class="rounded border-[var(--glass-border-strong)]" />
          Enabled
        </label>
        <label v-if="editingProviderId && editingProviderHasApiKey" class="inline-flex items-center gap-2 text-sm text-[var(--text-primary)]">
          <input v-model="form.clear_api_key" type="checkbox" class="rounded border-[var(--glass-border-strong)]" />
          Clear stored API key
        </label>
      </div>

      <div class="flex items-center gap-2 flex-wrap mt-5">
        <button
          @click="saveProvider"
          :disabled="savingProvider"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
        >
          {{ savingProvider ? 'Saving...' : editingProviderId ? 'Save Provider' : 'Create Provider' }}
        </button>
        <button
          v-if="editingProviderId"
          @click="runEditorTest"
          :disabled="testingProviderId === editingProviderId"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
        >
          {{ testingProviderId === editingProviderId ? 'Testing...' : 'Test Connection' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import type { ControlPlaneConfigResponse } from '@/api/config'
import {
  createProvider,
  deleteProvider,
  getProviders,
  testProvider,
  updateProvider,
  type ProviderResponse,
} from '@/api/providers'
import { updateProject } from '@/api/projects'
import { useProjects } from '@/composables/useProjects'
import { showErrorToast, showSuccessToast } from '@/utils/toast'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

defineProps<{
  controlPlaneConfig: ControlPlaneConfigResponse | null
}>()

const providerTypeOptions = ['openai', 'anthropic', 'deepseek', 'ollama']
const SYSTEM_PROVIDER_ID = 'system'

const savingProject = ref(false)
const savingProvider = ref(false)
const deletingProviderId = ref<string | null>(null)
const testingProviderId = ref<string | null>(null)
const editingProviderId = ref<string | null>(null)
const editingProviderHasApiKey = ref(false)
const providers = ref<ProviderResponse[]>([])

const form = reactive({
  label: '',
  model_provider: 'openai',
  api_base: '',
  api_key: '',
  available_models_text: '',
  default_model_name: '',
  enabled: true,
  clear_api_key: false,
})

const { activeProjectId, getProjectById, hydrateProjects } = useProjects()
const activeProject = computed(() => getProjectById(activeProjectId.value))
const enabledProviders = computed(() => providers.value.filter((provider) => provider.enabled || provider.is_system))
const selectedProjectProviderId = ref(SYSTEM_PROVIDER_ID)
const selectedProjectModel = ref('')

const parsedFormModels = computed(() => {
  const seen = new Set<string>()
  return form.available_models_text
    .split('\n')
    .map((item) => item.trim())
    .filter((item) => {
      if (!item || seen.has(item)) return false
      seen.add(item)
      return true
    })
})

const projectProviderModels = computed(() => {
  const provider = enabledProviders.value.find((item) => item.provider_id === selectedProjectProviderId.value)
  return provider?.available_models || []
})

const resetForm = () => {
  editingProviderId.value = null
  editingProviderHasApiKey.value = false
  form.label = ''
  form.model_provider = 'openai'
  form.api_base = ''
  form.api_key = ''
  form.available_models_text = ''
  form.default_model_name = ''
  form.enabled = true
  form.clear_api_key = false
}

const startCreate = () => {
  resetForm()
}

const startEdit = (provider: ProviderResponse) => {
  editingProviderId.value = provider.provider_id
  editingProviderHasApiKey.value = provider.has_api_key
  form.label = provider.label
  form.model_provider = provider.model_provider
  form.api_base = provider.api_base || ''
  form.api_key = ''
  form.available_models_text = provider.available_models.join('\n')
  form.default_model_name = provider.default_model_name
  form.enabled = provider.enabled
  form.clear_api_key = false
}

const loadProviders = async () => {
  const response = await getProviders()
  providers.value = response.providers
}

const syncProjectDefaults = () => {
  const project = activeProject.value
  if (!project) return
  const desiredProviderId = project.default_provider_id || SYSTEM_PROVIDER_ID
  const provider = enabledProviders.value.find((item) => item.provider_id === desiredProviderId) || enabledProviders.value[0]
  selectedProjectProviderId.value = provider?.provider_id || SYSTEM_PROVIDER_ID
  selectedProjectModel.value = project.default_model_name || provider?.default_model_name || ''
}

watch(activeProject, syncProjectDefaults, { immediate: true })
watch(enabledProviders, syncProjectDefaults)
watch(parsedFormModels, (models) => {
  if (!models.length) {
    form.default_model_name = ''
    return
  }
  if (!models.includes(form.default_model_name)) {
    form.default_model_name = models[0]
  }
})
watch(selectedProjectProviderId, (providerId) => {
  const provider = enabledProviders.value.find((item) => item.provider_id === providerId)
  if (!provider) return
  if (!provider.available_models.includes(selectedProjectModel.value)) {
    selectedProjectModel.value = provider.default_model_name
  }
})

onMounted(async () => {
  await hydrateProjects()
  await loadProviders()
  syncProjectDefaults()
})

const saveProjectModelPreference = async () => {
  if (activeProject.value.system) return
  savingProject.value = true
  try {
    await updateProject(activeProject.value.id, {
      default_provider_id: selectedProjectProviderId.value || null,
      default_model_name: selectedProjectModel.value || null,
    })
    await hydrateProjects(true)
    syncProjectDefaults()
    showSuccessToast('Project provider preference saved')
  } catch (error) {
    console.error('Failed to save project provider preference:', error)
    showErrorToast('Failed to save project provider preference')
  } finally {
    savingProject.value = false
  }
}

const saveProvider = async () => {
  if (!form.label.trim()) {
    showErrorToast('Provider label is required')
    return
  }
  if (!parsedFormModels.value.length) {
    showErrorToast('Add at least one model')
    return
  }
  savingProvider.value = true
  try {
    const payload = {
      label: form.label.trim(),
      model_provider: form.model_provider,
      api_base: form.api_base.trim() || null,
      api_key: form.api_key.trim() || null,
      available_models: parsedFormModels.value,
      default_model_name: form.default_model_name || parsedFormModels.value[0],
      enabled: form.enabled,
    }
    if (editingProviderId.value) {
      await updateProvider(editingProviderId.value, {
        ...payload,
        clear_api_key: form.clear_api_key,
      })
      showSuccessToast('Provider updated')
    } else {
      await createProvider(payload)
      showSuccessToast('Provider created')
    }
    await loadProviders()
    await hydrateProjects(true)
    syncProjectDefaults()
    resetForm()
  } catch (error) {
    console.error('Failed to save provider:', error)
    showErrorToast('Failed to save provider')
  } finally {
    savingProvider.value = false
  }
}

const runProviderTest = async (provider: ProviderResponse) => {
  testingProviderId.value = provider.provider_id
  try {
    await testProvider(provider.provider_id, provider.default_model_name)
    showSuccessToast(`Connection verified for ${provider.label}`)
  } catch (error) {
    console.error('Provider test failed:', error)
    showErrorToast(`Provider test failed for ${provider.label}`)
  } finally {
    testingProviderId.value = null
  }
}

const runEditorTest = async () => {
  if (!editingProviderId.value) return
  const provider = providers.value.find((item) => item.provider_id === editingProviderId.value)
  if (!provider) return
  await runProviderTest(provider)
}

const removeProvider = async (provider: ProviderResponse) => {
  deletingProviderId.value = provider.provider_id
  try {
    await deleteProvider(provider.provider_id)
    await loadProviders()
    await hydrateProjects(true)
    syncProjectDefaults()
    if (editingProviderId.value === provider.provider_id) {
      resetForm()
    }
    showSuccessToast(`Deleted ${provider.label}`)
  } catch (error) {
    console.error('Failed to delete provider:', error)
    showErrorToast(`Failed to delete ${provider.label}`)
  } finally {
    deletingProviderId.value = null
  }
}
</script>
