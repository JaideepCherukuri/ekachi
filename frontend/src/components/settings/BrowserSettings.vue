<template>
  <div class="flex flex-col gap-4 w-full">
    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Browser Runtime
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            {{ activeProject.name }}
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            @click="runConnectionTest"
            :disabled="connectionLoading || activeProject.system || !browserCdpUrl.trim()"
            class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
          >
            {{ connectionLoading ? 'Testing...' : 'Test Connection' }}
          </button>
          <button
            @click="saveBrowserProfile"
            :disabled="saving || activeProject.system"
            class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : 'Save Browser Profile' }}
          </button>
        </div>
      </div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        Configure how new sessions in this project should attach to browser infrastructure. Ekachi now persists the browser cookie jar with the project and applies those cookies when a new session starts.
      </div>
    </section>

    <section v-if="connectionStatus" class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">Remote Browser Health</div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mt-4">
        <div class="rounded-[16px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
          <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Browser</div>
          <div class="text-sm font-semibold text-[var(--text-primary)] mt-2 break-words">{{ connectionStatus.browser || 'Unknown' }}</div>
        </div>
        <div class="rounded-[16px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
          <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Pages</div>
          <div class="text-sm font-semibold text-[var(--text-primary)] mt-2">{{ connectionStatus.page_count }}</div>
        </div>
        <div class="rounded-[16px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
          <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Contexts</div>
          <div class="text-sm font-semibold text-[var(--text-primary)] mt-2">{{ connectionStatus.context_count }}</div>
        </div>
        <div class="rounded-[16px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
          <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Live Cookies</div>
          <div class="text-sm font-semibold text-[var(--text-primary)] mt-2">{{ connectionStatus.total_cookie_count }}</div>
        </div>
      </div>
      <div class="text-xs text-[var(--text-tertiary)] mt-4 break-all">
        {{ connectionStatus.user_agent || connectionStatus.ws_url }}
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">Browser Engine</div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        Select the automation layer Ekachi should use when it connects to Chrome.
      </div>
      <div class="mt-4">
        <Select v-model="selectedBrowserEngine">
          <SelectTrigger class="w-full md:w-[320px] h-[42px]">
            <SelectValue placeholder="System default" />
          </SelectTrigger>
          <SelectContent :side-offset="6">
            <SelectItem :value="SYSTEM_DEFAULT_VALUE">System default</SelectItem>
            <SelectItem
              v-for="engine in controlPlaneConfig?.supported_browser_engines || []"
              :key="engine"
              :value="engine"
            >
              {{ engine }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="text-xs text-[var(--text-tertiary)] mt-3">
        Runtime default: {{ controlPlaneConfig?.browser_engine || 'Unavailable' }}
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">Remote CDP Endpoint</div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        Optional. Point a project at an already-running Chromium instance via HTTP or WebSocket CDP.
      </div>
      <input
        v-model="browserCdpUrl"
        class="mt-4 w-full h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
        placeholder="ws://127.0.0.1:9222/devtools/browser/..."
      />
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Browser Pool</div>
          <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
            Track multiple named CDP browsers, inspect their health, and promote one to the active project browser without retyping endpoints.
          </div>
        </div>
        <button
          @click="refreshBrowserPool"
          :disabled="poolLoading || activeProject.system"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
        >
          {{ poolLoading ? 'Refreshing...' : 'Refresh Pool' }}
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-[1fr_1.4fr_auto] gap-3 mt-4">
        <input
          v-model="poolForm.label"
          class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
          placeholder="Local Login Browser"
        />
        <input
          v-model="poolForm.cdp_url"
          class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
          placeholder="http://127.0.0.1:9222"
        />
        <button
          @click="addBrowserToPool"
          :disabled="poolLoading || activeProject.system"
          class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          Add Browser
        </button>
      </div>

      <div class="flex flex-col gap-3 mt-4">
        <article
          v-for="browser in browserPool.browsers"
          :key="browser.browser_id"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
        >
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <div class="text-sm font-semibold text-[var(--text-primary)]">{{ browser.label }}</div>
                <span class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)] uppercase tracking-[0.08em]">
                  {{ browser.source }}
                </span>
                <span
                  class="px-2.5 py-1 rounded-full text-[11px] border"
                  :class="browser.active ? 'border-[var(--function-success)] text-[var(--function-success)]' : 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]'"
                >
                  {{ browser.active ? 'Active' : 'Standby' }}
                </span>
                <span
                  class="px-2.5 py-1 rounded-full text-[11px] border"
                  :class="browser.healthy ? 'border-sky-400/50 text-sky-700' : 'border-rose-300/60 text-rose-700'"
                >
                  {{ browser.healthy ? 'Healthy' : 'Unavailable' }}
                </span>
              </div>
              <div class="text-xs text-[var(--text-tertiary)] mt-2 break-all">{{ browser.cdp_url }}</div>
              <div class="flex flex-wrap gap-3 mt-3 text-xs text-[var(--text-tertiary)]">
                <span v-if="browser.browser">{{ browser.browser }}</span>
                <span>Pages: {{ browser.page_count }}</span>
                <span>Cookies: {{ browser.total_cookie_count }}</span>
              </div>
              <div v-if="browser.error" class="text-xs text-[var(--function-error)] mt-2 break-all">
                {{ browser.error }}
              </div>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                @click="activatePoolBrowser(browser.browser_id)"
                :disabled="poolLoading || browser.active || activeProject.system"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
              >
                {{ browser.active ? 'Active' : 'Set Active' }}
              </button>
              <button
                @click="removePoolBrowser(browser.browser_id)"
                :disabled="poolLoading || activeProject.system"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
              >
                Remove
              </button>
            </div>
          </div>
        </article>
        <div v-if="browserPool.browsers.length === 0" class="rounded-[16px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
          No browsers have been registered for this project yet.
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <article class="ek-glass-card rounded-[20px] p-5">
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <div class="text-base font-semibold text-[var(--text-primary)]">Saved Project Cookies</div>
            <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
              This cookie jar is versioned with the project and applied to new sessions automatically.
            </div>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <button
              @click="applySavedCookies"
              :disabled="cookieActionLoading || activeProject.system || !browserCdpUrl.trim() || projectCookieInventory.total_cookie_count === 0"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Apply To Live Browser
            </button>
            <button
              @click="clearAllProjectCookies"
              :disabled="cookieActionLoading || activeProject.system || projectCookieInventory.total_cookie_count === 0"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Clear Saved
            </button>
          </div>
        </div>
        <div class="text-xs text-[var(--text-tertiary)] mt-4">
          {{ projectCookieInventory.total_cookie_count }} cookies across {{ projectCookieInventory.domains.length }} domains.
        </div>
        <div class="flex flex-col gap-3 mt-4">
          <div
            v-for="domain in projectCookieInventory.domains"
            :key="`project-${domain.domain}`"
            class="rounded-[16px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="text-sm font-semibold text-[var(--text-primary)] break-all">{{ domain.domain }}</div>
                <div class="text-xs text-[var(--text-tertiary)] mt-1">
                  {{ domain.cookie_count }} cookies · {{ domain.http_only_count }} httpOnly · {{ domain.secure_count }} secure
                </div>
              </div>
              <button
                @click="clearProjectDomainCookies(domain.domain)"
                :disabled="cookieActionLoading || activeProject.system"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-xs font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
              >
                Remove
              </button>
            </div>
          </div>
          <div v-if="projectCookieInventory.domains.length === 0" class="rounded-[16px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
            No saved project cookies yet. Capture them from a live CDP browser first.
          </div>
        </div>
      </article>

      <article class="ek-glass-card rounded-[20px] p-5">
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <div class="text-base font-semibold text-[var(--text-primary)]">Live Browser Cookies</div>
            <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
              Inspect and mutate the currently attached remote browser profile over CDP.
            </div>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <button
              @click="refreshLiveCookies"
              :disabled="cookieActionLoading || activeProject.system || !browserCdpUrl.trim()"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Refresh
            </button>
            <button
              @click="captureLiveCookies"
              :disabled="cookieActionLoading || activeProject.system || !browserCdpUrl.trim()"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Capture To Project
            </button>
            <button
              @click="clearAllLiveCookies"
              :disabled="cookieActionLoading || activeProject.system || !browserCdpUrl.trim() || liveCookieInventory.total_cookie_count === 0"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Clear Live
            </button>
          </div>
        </div>
        <div class="text-xs text-[var(--text-tertiary)] mt-4">
          {{ liveCookieInventory.total_cookie_count }} cookies across {{ liveCookieInventory.domains.length }} domains.
        </div>
        <div class="flex flex-col gap-3 mt-4">
          <div
            v-for="domain in liveCookieInventory.domains"
            :key="`live-${domain.domain}`"
            class="rounded-[16px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="text-sm font-semibold text-[var(--text-primary)] break-all">{{ domain.domain }}</div>
                <div class="text-xs text-[var(--text-tertiary)] mt-1">
                  {{ domain.cookie_count }} cookies · {{ domain.http_only_count }} httpOnly · {{ domain.secure_count }} secure
                </div>
              </div>
              <button
                @click="clearLiveDomainCookies(domain.domain)"
                :disabled="cookieActionLoading || activeProject.system || !browserCdpUrl.trim()"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-xs font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
              >
                Remove
              </button>
            </div>
          </div>
          <div v-if="liveCookieInventory.domains.length === 0" class="rounded-[16px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
            {{ browserCdpUrl.trim() ? 'No live cookies are present on the connected browser.' : 'Configure a remote CDP endpoint to inspect live cookies.' }}
          </div>
        </div>
      </article>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">Cookie Profile Notes</div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        Store operator notes about login assumptions or auth-state usage alongside the concrete cookie jar.
      </div>
      <textarea
        v-model="browserCookieProfile"
        rows="7"
        class="mt-4 w-full rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[160px]"
        placeholder="Example: Reuse the already logged-in workspace browser. Keep cookies for app.example.com and do not sign out."
      />
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">Extension Paths</div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        One path per line. Use this to document or preconfigure extensions that should be present in the browser profile for this project.
      </div>
      <textarea
        v-model="browserExtensionPathsText"
        rows="6"
        class="mt-4 w-full rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[140px]"
        placeholder="/opt/extensions/react-devtools&#10;/opt/extensions/ublock-origin"
      />
      <div class="text-xs text-[var(--text-tertiary)] mt-3">
        {{ parsedExtensionPaths.length }} extension path{{ parsedExtensionPaths.length === 1 ? '' : 's' }} configured.
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import type { ControlPlaneConfigResponse } from '@/api/config'
import { updateProject } from '@/api/projects'
import {
  activateBrowserPoolEntry,
  addBrowserPoolEntry,
  applyProjectBrowserCookies,
  captureLiveBrowserCookies,
  clearLiveBrowserCookies,
  clearProjectBrowserCookies,
  deleteBrowserPoolEntry,
  getBrowserPool,
  getLiveBrowserCookies,
  getProjectBrowserCookies,
  testBrowserConnection,
} from '@/api/browser'
import type { BrowserConnectionResponse, BrowserCookieInventoryResponse, BrowserPoolResponse } from '@/types/response'
import { useProjects } from '@/composables/useProjects'
import { showErrorToast, showSuccessToast } from '@/utils/toast'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

defineProps<{
  controlPlaneConfig: ControlPlaneConfigResponse | null
}>()

const SYSTEM_DEFAULT_VALUE = '__system_default__'
const saving = ref(false)
const connectionLoading = ref(false)
const cookieActionLoading = ref(false)
const poolLoading = ref(false)

const EMPTY_COOKIE_INVENTORY: BrowserCookieInventoryResponse = {
  source: 'project',
  total_cookie_count: 0,
  domains: [],
}

const { activeProjectId, getProjectById, hydrateProjects } = useProjects()

const activeProject = computed(() => getProjectById(activeProjectId.value))
const selectedBrowserEngine = ref<string>(SYSTEM_DEFAULT_VALUE)
const browserCdpUrl = ref('')
const browserCookieProfile = ref('')
const browserExtensionPathsText = ref('')
const connectionStatus = ref<BrowserConnectionResponse | null>(null)
const projectCookieInventory = reactive<BrowserCookieInventoryResponse>({ ...EMPTY_COOKIE_INVENTORY })
const liveCookieInventory = reactive<BrowserCookieInventoryResponse>({ source: 'live', total_cookie_count: 0, domains: [] })
const browserPool = reactive<BrowserPoolResponse>({ active_browser_id: null, browsers: [] })
const poolForm = reactive({
  label: '',
  cdp_url: '',
})

const parsedExtensionPaths = computed(() => {
  return browserExtensionPathsText.value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
})

watch(activeProject, async (project) => {
  selectedBrowserEngine.value = project.preferred_browser_engine || SYSTEM_DEFAULT_VALUE
  browserCdpUrl.value = project.browser_cdp_url || ''
  browserCookieProfile.value = project.browser_cookie_profile || ''
  browserExtensionPathsText.value = (project.browser_extension_paths || []).join('\n')
  connectionStatus.value = null
  browserPool.active_browser_id = null
  browserPool.browsers = []
  liveCookieInventory.source = 'live'
  liveCookieInventory.total_cookie_count = 0
  liveCookieInventory.domains = []
  if (!project.system) {
    await refreshProjectCookies()
    await refreshBrowserPool()
  } else {
    projectCookieInventory.source = 'project'
    projectCookieInventory.total_cookie_count = 0
    projectCookieInventory.domains = []
    browserPool.active_browser_id = null
    browserPool.browsers = []
  }
}, { immediate: true })

const refreshBrowserPool = async () => {
  if (activeProject.value.system) return
  poolLoading.value = true
  try {
    const pool = await getBrowserPool(activeProject.value.id)
    browserPool.active_browser_id = pool.active_browser_id || null
    browserPool.browsers = pool.browsers
  } catch (error) {
    console.error('Failed to load browser pool:', error)
    browserPool.active_browser_id = null
    browserPool.browsers = []
    showErrorToast('Failed to load browser pool')
  } finally {
    poolLoading.value = false
  }
}

const refreshProjectCookies = async () => {
  if (activeProject.value.system) return
  try {
    const inventory = await getProjectBrowserCookies(activeProject.value.id)
    projectCookieInventory.source = inventory.source
    projectCookieInventory.total_cookie_count = inventory.total_cookie_count
    projectCookieInventory.domains = inventory.domains
  } catch (error) {
    console.error('Failed to load project cookie inventory:', error)
    projectCookieInventory.source = 'project'
    projectCookieInventory.total_cookie_count = 0
    projectCookieInventory.domains = []
  }
}

const refreshLiveCookies = async () => {
  if (activeProject.value.system || !browserCdpUrl.value.trim()) return
  cookieActionLoading.value = true
  try {
    const inventory = await getLiveBrowserCookies(activeProject.value.id)
    liveCookieInventory.source = inventory.source
    liveCookieInventory.total_cookie_count = inventory.total_cookie_count
    liveCookieInventory.domains = inventory.domains
    showSuccessToast('Live browser cookies refreshed')
  } catch (error) {
    console.error('Failed to load live browser cookies:', error)
    showErrorToast('Failed to load live browser cookies')
  } finally {
    cookieActionLoading.value = false
  }
}

const saveBrowserProfile = async () => {
  if (activeProject.value.system) return
  saving.value = true
  try {
    await updateProject(activeProject.value.id, {
      preferred_browser_engine: selectedBrowserEngine.value === SYSTEM_DEFAULT_VALUE ? '' : selectedBrowserEngine.value,
      browser_cdp_url: browserCdpUrl.value.trim() || '',
      browser_cookie_profile: browserCookieProfile.value.trim() || '',
      browser_extension_paths: parsedExtensionPaths.value,
    })
    await hydrateProjects(true)
    await refreshProjectCookies()
    showSuccessToast('Project browser profile saved')
  } catch (error) {
    console.error('Failed to save project browser profile:', error)
    showErrorToast('Failed to save project browser profile')
  } finally {
    saving.value = false
  }
}

const addBrowserToPool = async () => {
  if (activeProject.value.system) return
  if (!poolForm.label.trim() || !poolForm.cdp_url.trim()) {
    showErrorToast('Browser label and CDP URL are required')
    return
  }
  poolLoading.value = true
  try {
    const pool = await addBrowserPoolEntry(activeProject.value.id, {
      label: poolForm.label.trim(),
      cdp_url: poolForm.cdp_url.trim(),
      source: 'manual',
      set_active: !browserCdpUrl.value.trim(),
    })
    browserPool.active_browser_id = pool.active_browser_id || null
    browserPool.browsers = pool.browsers
    if (!browserCdpUrl.value.trim()) {
      const activeBrowser = pool.browsers.find((browser) => browser.active)
      browserCdpUrl.value = activeBrowser?.cdp_url || browserCdpUrl.value
    }
    await hydrateProjects(true)
    poolForm.label = ''
    poolForm.cdp_url = ''
    showSuccessToast('Browser added to pool')
  } catch (error) {
    console.error('Failed to add browser to pool:', error)
    showErrorToast('Failed to add browser to pool')
  } finally {
    poolLoading.value = false
  }
}

const activatePoolBrowser = async (browserId: string) => {
  if (activeProject.value.system) return
  poolLoading.value = true
  try {
    const pool = await activateBrowserPoolEntry(activeProject.value.id, browserId)
    browserPool.active_browser_id = pool.active_browser_id || null
    browserPool.browsers = pool.browsers
    const activeBrowser = pool.browsers.find((browser) => browser.active)
    browserCdpUrl.value = activeBrowser?.cdp_url || ''
    await hydrateProjects(true)
    showSuccessToast('Project browser updated')
  } catch (error) {
    console.error('Failed to activate browser pool entry:', error)
    showErrorToast('Failed to activate browser')
  } finally {
    poolLoading.value = false
  }
}

const removePoolBrowser = async (browserId: string) => {
  if (activeProject.value.system) return
  poolLoading.value = true
  try {
    const pool = await deleteBrowserPoolEntry(activeProject.value.id, browserId)
    browserPool.active_browser_id = pool.active_browser_id || null
    browserPool.browsers = pool.browsers
    const activeBrowser = pool.browsers.find((browser) => browser.active)
    browserCdpUrl.value = activeBrowser?.cdp_url || ''
    await hydrateProjects(true)
    showSuccessToast('Browser removed from pool')
  } catch (error) {
    console.error('Failed to remove browser pool entry:', error)
    showErrorToast('Failed to remove browser from pool')
  } finally {
    poolLoading.value = false
  }
}

const runConnectionTest = async () => {
  if (activeProject.value.system || !browserCdpUrl.value.trim()) return
  connectionLoading.value = true
  try {
    connectionStatus.value = await testBrowserConnection(activeProject.value.id)
    showSuccessToast('Remote browser connection succeeded')
  } catch (error) {
    console.error('Failed to connect to remote browser:', error)
    connectionStatus.value = null
    showErrorToast('Failed to connect to remote browser')
  } finally {
    connectionLoading.value = false
  }
}

const captureLiveCookies = async () => {
  if (activeProject.value.system || !browserCdpUrl.value.trim()) return
  cookieActionLoading.value = true
  try {
    const result = await captureLiveBrowserCookies(activeProject.value.id)
    projectCookieInventory.source = result.inventory.source
    projectCookieInventory.total_cookie_count = result.inventory.total_cookie_count
    projectCookieInventory.domains = result.inventory.domains
    await hydrateProjects(true)
    await refreshLiveCookies()
    showSuccessToast(`Captured ${result.captured_count || 0} cookies into the project`)
  } catch (error) {
    console.error('Failed to capture live browser cookies:', error)
    showErrorToast('Failed to capture live browser cookies')
  } finally {
    cookieActionLoading.value = false
  }
}

const applySavedCookies = async () => {
  if (activeProject.value.system || !browserCdpUrl.value.trim()) return
  cookieActionLoading.value = true
  try {
    const result = await applyProjectBrowserCookies(activeProject.value.id)
    liveCookieInventory.source = result.inventory.source
    liveCookieInventory.total_cookie_count = result.inventory.total_cookie_count
    liveCookieInventory.domains = result.inventory.domains
    showSuccessToast(`Applied ${result.applied_count || 0} cookies to the live browser`)
  } catch (error) {
    console.error('Failed to apply project browser cookies:', error)
    showErrorToast('Failed to apply project browser cookies')
  } finally {
    cookieActionLoading.value = false
  }
}

const clearAllProjectCookies = async () => {
  if (activeProject.value.system) return
  cookieActionLoading.value = true
  try {
    const result = await clearProjectBrowserCookies(activeProject.value.id)
    projectCookieInventory.source = result.inventory.source
    projectCookieInventory.total_cookie_count = result.inventory.total_cookie_count
    projectCookieInventory.domains = result.inventory.domains
    await hydrateProjects(true)
    showSuccessToast(`Removed ${result.removed_count || 0} saved project cookies`)
  } catch (error) {
    console.error('Failed to clear project cookies:', error)
    showErrorToast('Failed to clear project cookies')
  } finally {
    cookieActionLoading.value = false
  }
}

const clearProjectDomainCookies = async (domain: string) => {
  if (activeProject.value.system) return
  cookieActionLoading.value = true
  try {
    const result = await clearProjectBrowserCookies(activeProject.value.id, domain)
    projectCookieInventory.source = result.inventory.source
    projectCookieInventory.total_cookie_count = result.inventory.total_cookie_count
    projectCookieInventory.domains = result.inventory.domains
    await hydrateProjects(true)
    showSuccessToast(`Removed saved cookies for ${domain}`)
  } catch (error) {
    console.error('Failed to clear project domain cookies:', error)
    showErrorToast('Failed to clear saved cookies for that domain')
  } finally {
    cookieActionLoading.value = false
  }
}

const clearAllLiveCookies = async () => {
  if (activeProject.value.system || !browserCdpUrl.value.trim()) return
  cookieActionLoading.value = true
  try {
    const result = await clearLiveBrowserCookies(activeProject.value.id)
    liveCookieInventory.source = result.inventory.source
    liveCookieInventory.total_cookie_count = result.inventory.total_cookie_count
    liveCookieInventory.domains = result.inventory.domains
    showSuccessToast(`Removed ${result.removed_count || 0} live browser cookies`)
  } catch (error) {
    console.error('Failed to clear live cookies:', error)
    showErrorToast('Failed to clear live browser cookies')
  } finally {
    cookieActionLoading.value = false
  }
}

const clearLiveDomainCookies = async (domain: string) => {
  if (activeProject.value.system || !browserCdpUrl.value.trim()) return
  cookieActionLoading.value = true
  try {
    const result = await clearLiveBrowserCookies(activeProject.value.id, domain)
    liveCookieInventory.source = result.inventory.source
    liveCookieInventory.total_cookie_count = result.inventory.total_cookie_count
    liveCookieInventory.domains = result.inventory.domains
    showSuccessToast(`Removed live cookies for ${domain}`)
  } catch (error) {
    console.error('Failed to clear live domain cookies:', error)
    showErrorToast('Failed to clear live cookies for that domain')
  } finally {
    cookieActionLoading.value = false
  }
}
</script>
