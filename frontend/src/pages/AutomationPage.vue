<template>
  <SimpleBar>
    <div class="flex flex-col h-full flex-1 min-w-0 px-3 sm:px-5 py-4">
      <div class="mx-auto w-full max-w-full sm:max-w-[1180px] flex flex-col gap-4">
        <div class="ek-sticky-glass rounded-[24px] px-4 py-4">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div class="min-w-0">
              <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] text-xs text-[var(--text-secondary)]">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: activeProject.color }"></span>
                <span>Automation</span>
                <span class="font-medium text-[var(--text-primary)]">{{ activeProject.name }}</span>
              </div>
              <h1 class="text-[28px] leading-[34px] font-semibold text-[var(--text-primary)] mt-4">Trigger Control Plane</h1>
              <p class="text-sm text-[var(--text-secondary)] mt-2 max-w-[760px]">
                Create project-scoped automations, inspect execution health, retry failed runs, and cancel in-flight work without leaving the operations surface.
              </p>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                @click="reload"
                class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
              >
                Refresh
              </button>
              <button
                @click="toggleComposer"
                class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90"
              >
                {{ isComposerOpen ? 'Close Composer' : 'New Trigger' }}
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <div class="ek-glass-card rounded-[20px] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Configured Triggers</div>
            <div class="text-[24px] leading-[28px] font-semibold text-[var(--text-primary)] mt-3">{{ triggers.length }}</div>
          </div>
          <div class="ek-glass-card rounded-[20px] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Active Triggers</div>
            <div class="text-[24px] leading-[28px] font-semibold text-[var(--text-primary)] mt-3">{{ activeTriggerCount }}</div>
          </div>
          <div class="ek-glass-card rounded-[20px] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Running Executions</div>
            <div class="text-[24px] leading-[28px] font-semibold text-[var(--text-primary)] mt-3">{{ runningRunCount }}</div>
          </div>
          <div class="ek-glass-card rounded-[20px] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Success Rate</div>
            <div class="text-[24px] leading-[28px] font-semibold text-[var(--text-primary)] mt-3">{{ successRateLabel }}</div>
          </div>
        </div>

        <div v-if="isComposerOpen" class="ek-glass-card rounded-[24px] p-4">
          <div class="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <div class="text-base font-semibold text-[var(--text-primary)]">
                {{ editingTriggerId ? 'Edit Trigger' : 'Create Trigger' }}
              </div>
              <div class="text-sm text-[var(--text-secondary)] mt-1">
                Manual triggers run on demand. Webhooks expose a signed endpoint. Schedules use 5-field UTC cron.
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
            <label class="flex flex-col gap-2">
              <span class="text-sm font-medium text-[var(--text-primary)]">Name</span>
              <input
                v-model="form.name"
                class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
                placeholder="Daily Inbox Review"
              />
            </label>
            <label class="flex flex-col gap-2">
              <span class="text-sm font-medium text-[var(--text-primary)]">Type</span>
              <Select v-model="form.trigger_type">
                <SelectTrigger class="h-11">
                  <SelectValue placeholder="Select trigger type" />
                </SelectTrigger>
                <SelectContent :side-offset="6">
                  <SelectItem :value="TriggerType.MANUAL">Manual</SelectItem>
                  <SelectItem :value="TriggerType.WEBHOOK">Webhook</SelectItem>
                  <SelectItem :value="TriggerType.SCHEDULE">Schedule</SelectItem>
                </SelectContent>
              </Select>
            </label>
          </div>
          <label class="flex flex-col gap-2 mt-3">
            <span class="text-sm font-medium text-[var(--text-primary)]">Prompt</span>
            <textarea
              v-model="form.prompt"
              rows="6"
              class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[140px]"
              placeholder="Check the latest project context, search for new signals, and prepare a concise update."
            />
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
            <label v-if="form.trigger_type === TriggerType.SCHEDULE" class="flex flex-col gap-2">
              <span class="text-sm font-medium text-[var(--text-primary)]">Cron (UTC)</span>
              <input
                v-model="form.schedule_cron"
                class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
                placeholder="0 9 * * 1-5"
              />
            </label>
            <label class="flex flex-col gap-2">
              <span class="text-sm font-medium text-[var(--text-primary)]">Status</span>
              <Select v-model="form.status">
                <SelectTrigger class="h-11">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent :side-offset="6">
                  <SelectItem :value="TriggerStatus.ACTIVE">Active</SelectItem>
                  <SelectItem :value="TriggerStatus.INACTIVE">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </label>
          </div>
          <div class="flex items-center gap-2 mt-4">
            <button
              @click="handleSaveTrigger"
              :disabled="saving"
              class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : editingTriggerId ? 'Save Changes' : 'Create Trigger' }}
            </button>
            <button
              @click="resetComposer"
              class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
            >
              Cancel
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-[1.05fr_0.95fr] gap-4">
          <div class="flex flex-col gap-4 min-w-0">
            <section class="ek-glass-card rounded-[24px] p-4">
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <div class="text-base font-semibold text-[var(--text-primary)]">Triggers</div>
                  <div class="text-sm text-[var(--text-secondary)] mt-1">
                    {{ triggers.length }} configured for {{ activeProject.name }}.
                  </div>
                </div>
              </div>
              <div class="flex flex-col gap-3 mt-4">
                <div
                  v-for="trigger in triggers"
                  :key="trigger.trigger_id"
                  class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
                >
                  <div class="flex items-start justify-between gap-3 flex-wrap">
                    <div class="min-w-0">
                      <div class="flex items-center gap-2 flex-wrap">
                        <span class="text-sm font-semibold text-[var(--text-primary)]">{{ trigger.name }}</span>
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)] uppercase tracking-[0.08em]">
                          {{ trigger.trigger_type }}
                        </span>
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border" :class="statusBadgeClass(trigger.status)">
                          {{ trigger.status }}
                        </span>
                      </div>
                      <div class="text-sm text-[var(--text-secondary)] mt-2 whitespace-pre-wrap break-words">{{ trigger.prompt }}</div>
                      <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4 text-xs">
                        <div class="rounded-[12px] border border-[var(--glass-border)] px-3 py-2 text-[var(--text-secondary)]">
                          Runs <span class="font-semibold text-[var(--text-primary)]">{{ trigger.execution_count }}</span>
                        </div>
                        <div class="rounded-[12px] border border-[var(--glass-border)] px-3 py-2 text-[var(--text-secondary)]">
                          Success <span class="font-semibold text-[var(--function-success)]">{{ trigger.success_count }}</span>
                        </div>
                        <div class="rounded-[12px] border border-[var(--glass-border)] px-3 py-2 text-[var(--text-secondary)]">
                          Failed <span class="font-semibold text-[var(--function-error)]">{{ trigger.failure_count }}</span>
                        </div>
                        <div class="rounded-[12px] border border-[var(--glass-border)] px-3 py-2 text-[var(--text-secondary)]">
                          Cancelled <span class="font-semibold text-[var(--text-tertiary)]">{{ trigger.cancelled_count }}</span>
                        </div>
                      </div>
                      <div class="flex items-center gap-4 flex-wrap mt-3 text-xs text-[var(--text-tertiary)]">
                        <span v-if="trigger.schedule_cron">Cron: {{ trigger.schedule_cron }}</span>
                        <span v-if="trigger.next_run_at">Next run: {{ formatDate(trigger.next_run_at) }}</span>
                        <span v-if="trigger.last_run_at">Last run: {{ formatDate(trigger.last_run_at) }}</span>
                      </div>
                      <div v-if="trigger.trigger_type === TriggerType.WEBHOOK && trigger.webhook_secret" class="mt-3">
                        <button
                          @click="copyWebhookUrl(trigger)"
                          class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                        >
                          Copy Webhook URL
                        </button>
                      </div>
                    </div>
                    <div class="flex items-center gap-2 flex-wrap">
                      <button
                        @click="handleExecuteTrigger(trigger.trigger_id)"
                        class="px-3 py-2 rounded-[12px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90"
                      >
                        Run Now
                      </button>
                      <button
                        @click="handleToggleStatus(trigger)"
                        class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                      >
                        {{ trigger.status === TriggerStatus.ACTIVE ? 'Pause' : 'Activate' }}
                      </button>
                      <button
                        @click="startEditing(trigger)"
                        class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                      >
                        Edit
                      </button>
                      <button
                        @click="handleDeleteTrigger(trigger.trigger_id)"
                        class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="triggers.length === 0" class="rounded-[18px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
                  No triggers configured for this project yet.
                </div>
              </div>
            </section>

            <section class="ek-glass-card rounded-[24px] p-4">
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <div class="text-base font-semibold text-[var(--text-primary)]">Execution Feed</div>
                  <div class="text-sm text-[var(--text-secondary)] mt-1">
                    {{ anyRunningRuns ? 'Auto-refreshing while runs are active.' : 'Recent automated and manual trigger runs.' }}
                  </div>
                </div>
              </div>
              <div class="flex flex-col gap-3 mt-4">
                <button
                  v-for="run in runs"
                  :key="run.run_id"
                  @click="selectedRunId = run.run_id"
                  class="rounded-[18px] border px-4 py-4 text-left transition-colors"
                  :class="selectedRunId === run.run_id ? 'border-[var(--glass-border-strong)] bg-[var(--glass-surface)]' : 'border-[var(--glass-border)] bg-[var(--glass-surface-soft)] hover:bg-[var(--glass-surface)]'"
                >
                  <div class="flex items-center justify-between gap-3 flex-wrap">
                    <div>
                      <div class="text-sm font-semibold text-[var(--text-primary)]">{{ getTriggerName(run.trigger_id) }}</div>
                      <div class="text-xs text-[var(--text-tertiary)] mt-1">
                        {{ run.source }} · {{ formatDate(run.started_at) }} · Attempt {{ run.attempt_number }}
                      </div>
                    </div>
                    <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border" :class="runBadgeClass(run.status)">
                      {{ run.status }}
                    </span>
                  </div>
                  <div class="text-sm text-[var(--text-secondary)] mt-3">
                    {{ run.output_summary || run.error_message || summarizeInputPayload(run.input_payload) }}
                  </div>
                  <div class="flex items-center gap-3 flex-wrap mt-3 text-xs text-[var(--text-tertiary)]">
                    <span v-if="run.duration_seconds != null">Duration: {{ formatDuration(run.duration_seconds) }}</span>
                    <span v-if="run.session_id">Session: {{ run.session_id }}</span>
                  </div>
                </button>
                <div v-if="runs.length === 0" class="rounded-[18px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
                  No trigger runs recorded for this project yet.
                </div>
              </div>
            </section>
          </div>

          <section class="ek-glass-card rounded-[24px] p-4 min-w-0">
            <div class="flex items-center justify-between gap-3 flex-wrap">
              <div>
                <div class="text-base font-semibold text-[var(--text-primary)]">Execution Detail</div>
                <div class="text-sm text-[var(--text-secondary)] mt-1">
                  Deep state for the selected execution, including retry and cancellation controls.
                </div>
              </div>
            </div>
            <div v-if="selectedRun" class="flex flex-col gap-4 mt-4">
              <div class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
                <div class="flex items-center justify-between gap-3 flex-wrap">
                  <div>
                    <div class="text-sm font-semibold text-[var(--text-primary)]">{{ getTriggerName(selectedRun.trigger_id) }}</div>
                    <div class="text-xs text-[var(--text-tertiary)] mt-1">
                      {{ selectedRun.source }} · {{ formatDate(selectedRun.started_at) }}
                    </div>
                  </div>
                  <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border" :class="runBadgeClass(selectedRun.status)">
                    {{ selectedRun.status }}
                  </span>
                </div>
                <div class="grid grid-cols-2 gap-3 mt-4 text-sm">
                  <div class="rounded-[14px] border border-[var(--glass-border)] px-3 py-3">
                    <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Attempt</div>
                    <div class="text-[var(--text-primary)] font-semibold mt-2">{{ selectedRun.attempt_number }}</div>
                  </div>
                  <div class="rounded-[14px] border border-[var(--glass-border)] px-3 py-3">
                    <div class="text-xs uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Duration</div>
                    <div class="text-[var(--text-primary)] font-semibold mt-2">{{ formatDuration(selectedRun.duration_seconds) }}</div>
                  </div>
                </div>
                <div class="flex items-center gap-2 flex-wrap mt-4">
                  <button
                    v-if="selectedRun.status === TriggerRunStatus.RUNNING"
                    @click="handleCancelRun(selectedRun.run_id)"
                    class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                  >
                    Cancel Execution
                  </button>
                  <button
                    v-else
                    @click="handleRetryRun(selectedRun.run_id)"
                    class="px-3 py-2 rounded-[12px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90"
                  >
                    Retry Execution
                  </button>
                  <button
                    v-if="selectedRun.session_id"
                    @click="openSession(selectedRun.session_id)"
                    class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                  >
                    Open Session
                  </button>
                </div>
              </div>

              <div v-if="selectedRun.input_payload" class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
                <div class="text-sm font-semibold text-[var(--text-primary)]">Input Payload</div>
                <pre class="mt-3 text-xs leading-6 whitespace-pre-wrap break-words text-[var(--text-secondary)]">{{ formatJson(selectedRun.input_payload) }}</pre>
              </div>

              <div v-if="selectedRun.output_summary" class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
                <div class="text-sm font-semibold text-[var(--text-primary)]">Output Summary</div>
                <div class="mt-3 text-sm leading-6 whitespace-pre-wrap break-words text-[var(--text-secondary)]">{{ selectedRun.output_summary }}</div>
              </div>

              <div v-if="selectedRun.error_message" class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
                <div class="text-sm font-semibold text-[var(--function-error)]">Failure Detail</div>
                <div class="mt-3 text-sm leading-6 whitespace-pre-wrap break-words text-[var(--function-error)]">{{ selectedRun.error_message }}</div>
              </div>
            </div>
            <div v-else class="rounded-[18px] border border-dashed border-[var(--glass-border-strong)] px-4 py-12 text-center text-sm text-[var(--text-tertiary)] mt-4">
              Select an execution to inspect run details.
            </div>
          </section>
        </div>
      </div>
    </div>
  </SimpleBar>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import SimpleBar from '@/components/SimpleBar.vue'
import { copyToClipboard } from '@/utils/dom'
import { showErrorToast, showSuccessToast } from '@/utils/toast'
import {
  cancelTriggerRun,
  createTrigger,
  deleteTrigger,
  executeTrigger,
  getTriggerRuns,
  getTriggers,
  retryTriggerRun,
  updateTrigger,
} from '@/api/triggers'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useProjects } from '@/composables/useProjects'
import type { TriggerResponse, TriggerRunResponse } from '@/types/response'
import { TriggerRunStatus, TriggerStatus, TriggerType } from '@/types/response'

const router = useRouter()
const { activeProjectId, getProjectById, hydrateProjects } = useProjects()

const triggers = ref<TriggerResponse[]>([])
const runs = ref<TriggerRunResponse[]>([])
const saving = ref(false)
const isComposerOpen = ref(false)
const editingTriggerId = ref<string | null>(null)
const selectedRunId = ref<string | null>(null)
let autoRefreshHandle: number | null = null

const form = reactive({
  name: '',
  prompt: '',
  trigger_type: TriggerType.MANUAL,
  status: TriggerStatus.ACTIVE,
  schedule_cron: '',
})

const activeProject = computed(() => getProjectById(activeProjectId.value))
const currentProjectId = computed(() => activeProject.value.system ? null : activeProject.value.id)
const selectedRun = computed(() => runs.value.find((run) => run.run_id === selectedRunId.value) || null)
const activeTriggerCount = computed(() => triggers.value.filter((trigger) => trigger.status === TriggerStatus.ACTIVE).length)
const runningRunCount = computed(() => runs.value.filter((run) => run.status === TriggerRunStatus.RUNNING).length)
const anyRunningRuns = computed(() => runningRunCount.value > 0)
const terminalRuns = computed(() => runs.value.filter((run) => run.status !== TriggerRunStatus.PENDING && run.status !== TriggerRunStatus.RUNNING))
const successfulRuns = computed(() => terminalRuns.value.filter((run) => run.status === TriggerRunStatus.COMPLETED).length)
const successRateLabel = computed(() => {
  if (terminalRuns.value.length === 0) return 'N/A'
  return `${Math.round((successfulRuns.value / terminalRuns.value.length) * 100)}%`
})

const ensureSelectedRun = () => {
  if (!selectedRunId.value || !runs.value.some((run) => run.run_id === selectedRunId.value)) {
    selectedRunId.value = runs.value[0]?.run_id || null
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  autoRefreshHandle = window.setInterval(() => {
    void reload()
  }, 4000)
}

const stopAutoRefresh = () => {
  if (autoRefreshHandle !== null) {
    window.clearInterval(autoRefreshHandle)
    autoRefreshHandle = null
  }
}

const formatDate = (value?: string | null) => {
  if (!value) return 'Not run yet'
  return new Date(value).toLocaleString()
}

const formatDuration = (value?: number | null) => {
  if (value == null) return 'Not available'
  if (value < 1) return `${Math.round(value * 1000)}ms`
  if (value < 60) return `${value.toFixed(1)}s`
  const minutes = Math.floor(value / 60)
  const seconds = value % 60
  return `${minutes}m ${seconds.toFixed(0)}s`
}

const formatJson = (value: unknown) => JSON.stringify(value, null, 2)

const summarizeInputPayload = (payload?: Record<string, unknown> | null) => {
  if (!payload || Object.keys(payload).length === 0) return 'No explicit payload'
  const compact = JSON.stringify(payload)
  return compact.length > 160 ? `${compact.slice(0, 157)}...` : compact
}

const statusBadgeClass = (status: TriggerStatus) => {
  if (status === TriggerStatus.ACTIVE) return 'border-[var(--function-success)] text-[var(--function-success)]'
  if (status === TriggerStatus.COMPLETED) return 'border-[var(--text-brand)] text-[var(--text-brand)]'
  return 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]'
}

const runBadgeClass = (status: TriggerRunStatus) => {
  if (status === TriggerRunStatus.COMPLETED) return 'border-[var(--function-success)] text-[var(--function-success)]'
  if (status === TriggerRunStatus.FAILED) return 'border-[var(--function-error)] text-[var(--function-error)]'
  if (status === TriggerRunStatus.RUNNING) return 'border-[var(--text-brand)] text-[var(--text-brand)]'
  if (status === TriggerRunStatus.CANCELLED) return 'border-[var(--text-tertiary)] text-[var(--text-tertiary)]'
  return 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]'
}

const resetComposer = () => {
  isComposerOpen.value = false
  editingTriggerId.value = null
  form.name = ''
  form.prompt = ''
  form.trigger_type = TriggerType.MANUAL
  form.status = TriggerStatus.ACTIVE
  form.schedule_cron = ''
}

const toggleComposer = () => {
  if (isComposerOpen.value) {
    resetComposer()
    return
  }
  isComposerOpen.value = true
}

const reload = async () => {
  const [triggerData, runData] = await Promise.all([
    getTriggers(currentProjectId.value),
    getTriggerRuns(currentProjectId.value),
  ])
  triggers.value = triggerData.triggers
  runs.value = runData.runs
  ensureSelectedRun()
}

const handleSaveTrigger = async () => {
  if (!form.name.trim() || !form.prompt.trim()) {
    showErrorToast('Trigger name and prompt are required')
    return
  }
  if (form.trigger_type === TriggerType.SCHEDULE && !form.schedule_cron.trim()) {
    showErrorToast('Schedule triggers require a cron expression')
    return
  }

  saving.value = true
  try {
    if (editingTriggerId.value) {
      await updateTrigger(editingTriggerId.value, {
        project_id: currentProjectId.value,
        name: form.name.trim(),
        prompt: form.prompt.trim(),
        status: form.status,
        schedule_cron: form.trigger_type === TriggerType.SCHEDULE ? form.schedule_cron.trim() : null,
        schedule_timezone: 'UTC',
      })
      showSuccessToast('Trigger updated')
    } else {
      await createTrigger({
        project_id: currentProjectId.value,
        name: form.name.trim(),
        prompt: form.prompt.trim(),
        trigger_type: form.trigger_type,
        status: form.status,
        schedule_cron: form.trigger_type === TriggerType.SCHEDULE ? form.schedule_cron.trim() : null,
        schedule_timezone: 'UTC',
      })
      showSuccessToast('Trigger created')
    }
    await reload()
    resetComposer()
  } catch (error) {
    console.error('Failed to save trigger:', error)
    showErrorToast('Failed to save trigger')
  } finally {
    saving.value = false
  }
}

const startEditing = (trigger: TriggerResponse) => {
  editingTriggerId.value = trigger.trigger_id
  isComposerOpen.value = true
  form.name = trigger.name
  form.prompt = trigger.prompt
  form.trigger_type = trigger.trigger_type
  form.status = trigger.status
  form.schedule_cron = trigger.schedule_cron || ''
}

const handleDeleteTrigger = async (triggerId: string) => {
  if (!window.confirm('Delete this trigger?')) return
  try {
    await deleteTrigger(triggerId)
    showSuccessToast('Trigger deleted')
    await reload()
  } catch (error) {
    console.error('Failed to delete trigger:', error)
    showErrorToast('Failed to delete trigger')
  }
}

const handleToggleStatus = async (trigger: TriggerResponse) => {
  const nextStatus = trigger.status === TriggerStatus.ACTIVE ? TriggerStatus.INACTIVE : TriggerStatus.ACTIVE
  try {
    await updateTrigger(trigger.trigger_id, { status: nextStatus })
    showSuccessToast(nextStatus === TriggerStatus.ACTIVE ? 'Trigger activated' : 'Trigger paused')
    await reload()
  } catch (error) {
    console.error('Failed to toggle trigger:', error)
    showErrorToast('Failed to update trigger')
  }
}

const handleExecuteTrigger = async (triggerId: string) => {
  try {
    const run = await executeTrigger(triggerId)
    showSuccessToast('Trigger execution started')
    await reload()
    selectedRunId.value = run.run_id
  } catch (error) {
    console.error('Failed to execute trigger:', error)
    showErrorToast('Failed to execute trigger')
  }
}

const handleRetryRun = async (runId: string) => {
  try {
    const run = await retryTriggerRun(runId)
    showSuccessToast('Execution retried')
    await reload()
    selectedRunId.value = run.run_id
  } catch (error) {
    console.error('Failed to retry trigger run:', error)
    showErrorToast('Failed to retry trigger execution')
  }
}

const handleCancelRun = async (runId: string) => {
  try {
    const run = await cancelTriggerRun(runId)
    showSuccessToast('Execution cancelled')
    await reload()
    selectedRunId.value = run.run_id
  } catch (error) {
    console.error('Failed to cancel trigger run:', error)
    showErrorToast('Failed to cancel trigger execution')
  }
}

const getTriggerName = (triggerId: string) => {
  return triggers.value.find((trigger) => trigger.trigger_id === triggerId)?.name || 'Trigger'
}

const copyWebhookUrl = async (trigger: TriggerResponse) => {
  if (!trigger.webhook_secret) return
  const apiBase = import.meta.env.VITE_API_URL || window.location.origin
  const url = `${apiBase}/api/v1/triggers/webhook/${trigger.trigger_id}/${trigger.webhook_secret}`
  const copied = await copyToClipboard(url)
  if (copied) {
    showSuccessToast('Webhook URL copied')
  } else {
    showErrorToast('Failed to copy webhook URL')
  }
}

const openSession = (sessionId: string) => {
  router.push(`/chat/${sessionId}`)
}

watch(anyRunningRuns, (running) => {
  if (running) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}, { immediate: true })

watch(currentProjectId, async () => {
  try {
    await reload()
  } catch (error) {
    console.error('Failed to refresh automation data:', error)
  }
})

onMounted(async () => {
  try {
    await hydrateProjects()
    await reload()
  } catch (error) {
    console.error('Failed to load automation page:', error)
    showErrorToast('Failed to load automation data')
  }
})

onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>
