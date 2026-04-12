<template>
  <div class="flex flex-col gap-4 w-full">
    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Workforce And Memory
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            {{ activeProject.name }}
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            @click="toggleWorkerComposer"
            class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90"
          >
            {{ isWorkerComposerOpen ? 'Close Worker Composer' : 'New Worker' }}
          </button>
          <button
            @click="toggleSkillComposer"
            class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
          >
            {{ isSkillComposerOpen ? 'Close Skill Composer' : 'New Skill' }}
          </button>
        </div>
      </div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        Project memory, specialist workers, and precision skills are all injected into the runtime context for sessions created in this project.
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Project Memory</div>
          <div class="text-sm text-[var(--text-secondary)] mt-1">
            Durable context for this project.
          </div>
        </div>
        <button
          @click="handleSaveMemory"
          :disabled="memorySaving"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
        >
          {{ memorySaving ? 'Saving...' : 'Save Memory' }}
        </button>
      </div>
      <textarea
        v-model="memoryContent"
        rows="8"
        class="w-full mt-4 rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[180px]"
        placeholder="Important project facts, goals, constraints, or preferences that should shape future agent behavior."
      />
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Workflow Lanes</div>
          <div class="text-sm text-[var(--text-secondary)] mt-1">
            Explicit worker ownership across intake, research, execution, and delivery.
          </div>
        </div>
        <button
          @click="reload"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
        >
          Refresh
        </button>
      </div>
      <div class="grid grid-cols-1 xl:grid-cols-4 gap-3 mt-4">
        <div
          v-for="lane in workflowLaneCards"
          :key="lane.id"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="text-sm font-semibold text-[var(--text-primary)]">{{ lane.label }}</div>
            <span class="text-xs text-[var(--text-tertiary)]">{{ lane.workers.length }}</span>
          </div>
          <div class="text-xs text-[var(--text-tertiary)] mt-1">{{ lane.description }}</div>
          <div class="flex flex-col gap-2 mt-4">
            <div
              v-for="worker in lane.workers"
              :key="worker.worker_id"
              class="rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="text-sm font-medium text-[var(--text-primary)]">{{ worker.name }}</div>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border"
                  :class="worker.enabled ? 'border-[var(--function-success)] text-[var(--function-success)]' : 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]'"
                >
                  {{ worker.enabled ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
              <div class="text-xs text-[var(--text-tertiary)] mt-2 uppercase tracking-[0.08em]">{{ worker.role }}</div>
              <div v-if="worker.description" class="text-sm text-[var(--text-secondary)] mt-2">{{ worker.description }}</div>
              <div class="flex flex-wrap gap-2 mt-3">
                <span
                  v-for="tool in worker.tool_names"
                  :key="`${worker.worker_id}-${tool}`"
                  class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-white/60 text-[11px] text-[var(--text-primary)]"
                >
                  {{ tool }}
                </span>
                <span
                  v-if="worker.tool_names.length === 0"
                  class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-white/60 text-[11px] text-[var(--text-tertiary)]"
                >
                  No tool focus
                </span>
              </div>
            </div>
            <div
              v-if="lane.workers.length === 0"
              class="rounded-[14px] border border-dashed border-[var(--glass-border-strong)] px-3 py-6 text-center text-xs text-[var(--text-tertiary)]"
            >
              No workers assigned to this lane.
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="isWorkerComposerOpen" class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">
        {{ editingWorkerId ? 'Edit Worker' : 'Create Worker' }}
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
        <label class="flex flex-col gap-2 md:col-span-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Name</span>
          <input
            v-model="workerForm.name"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="Research Worker"
          />
        </label>
        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Role</span>
          <Select v-model="workerForm.role">
            <SelectTrigger class="h-11">
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent :side-offset="6">
              <SelectItem v-for="role in workerRoleOptions" :key="role.value" :value="role.value">
                {{ role.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </label>
        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Lane</span>
          <Select v-model="workerForm.lane">
            <SelectTrigger class="h-11">
              <SelectValue placeholder="Select lane" />
            </SelectTrigger>
            <SelectContent :side-offset="6">
              <SelectItem v-for="lane in workflowLaneDefinitions" :key="lane.id" :value="lane.id">
                {{ lane.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </label>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Description</span>
          <input
            v-model="workerForm.description"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="Owns evidence gathering and source validation."
          />
        </label>
        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Tool Focus</span>
          <input
            v-model="workerForm.toolsText"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="search, browser, file"
          />
        </label>
      </div>
      <label class="flex flex-col gap-2 mt-3">
        <span class="text-sm font-medium text-[var(--text-primary)]">Instructions</span>
        <textarea
          v-model="workerForm.instructions"
          rows="6"
          class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[140px]"
          placeholder="Prefer primary sources, challenge unsupported claims, and hand off a concise evidence bundle to the next lane."
        />
      </label>
      <label class="flex items-center gap-3 mt-4">
        <input v-model="workerForm.enabled" type="checkbox" class="size-4 rounded border-[var(--glass-border-strong)]" />
        <span class="text-sm text-[var(--text-primary)]">Enable this worker for project sessions</span>
      </label>
      <div class="flex items-center gap-2 mt-4">
        <button
          @click="handleSaveWorker"
          :disabled="workerSaving"
          class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {{ workerSaving ? 'Saving...' : editingWorkerId ? 'Save Worker' : 'Create Worker' }}
        </button>
        <button
          @click="resetWorkerComposer"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
        >
          Cancel
        </button>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Worker Library</div>
          <div class="text-sm text-[var(--text-secondary)] mt-1">
            {{ workers.length }} workers configured for this project.
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-3 mt-4">
        <div
          v-for="worker in workers"
          :key="worker.worker_id"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
        >
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-semibold text-[var(--text-primary)]">{{ worker.name }}</span>
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)] uppercase tracking-[0.08em]">
                  {{ worker.role }}
                </span>
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)] uppercase tracking-[0.08em]">
                  {{ worker.lane }}
                </span>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border"
                  :class="worker.enabled ? 'border-[var(--function-success)] text-[var(--function-success)]' : 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]'"
                >
                  {{ worker.enabled ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
              <div v-if="worker.description" class="text-sm text-[var(--text-secondary)] mt-2">{{ worker.description }}</div>
              <div class="text-sm text-[var(--text-secondary)] mt-2 whitespace-pre-wrap break-words">{{ worker.instructions }}</div>
              <div class="flex flex-wrap gap-2 mt-3">
                <span
                  v-for="tool in worker.tool_names"
                  :key="`${worker.worker_id}-${tool}`"
                  class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-white/60 text-[11px] text-[var(--text-primary)]"
                >
                  {{ tool }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                @click="toggleWorker(worker)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                {{ worker.enabled ? 'Disable' : 'Enable' }}
              </button>
              <button
                @click="startEditingWorker(worker)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                Edit
              </button>
              <button
                @click="handleDeleteWorker(worker.worker_id)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        <div v-if="workers.length === 0" class="rounded-[18px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
          No workers configured for this project yet.
        </div>
      </div>
    </section>

    <section v-if="isSkillComposerOpen" class="ek-glass-card rounded-[20px] p-5">
      <div class="text-base font-semibold text-[var(--text-primary)]">
        {{ editingSkillId ? 'Edit Skill' : 'Skill Composer' }}
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Name</span>
          <input
            v-model="skillForm.name"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="Research Style"
          />
        </label>
        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Description</span>
          <input
            v-model="skillForm.description"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="How this skill should be used"
          />
        </label>
      </div>
      <label class="flex flex-col gap-2 mt-3">
        <span class="text-sm font-medium text-[var(--text-primary)]">Instructions</span>
        <textarea
          v-model="skillForm.instructions"
          rows="6"
          class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[140px]"
          placeholder="When researching, prefer primary sources and provide concise evidence-backed conclusions."
        />
      </label>
      <label class="flex items-center gap-3 mt-4">
        <input v-model="skillForm.enabled" type="checkbox" class="size-4 rounded border-[var(--glass-border-strong)]" />
        <span class="text-sm text-[var(--text-primary)]">Enable this skill for project sessions</span>
      </label>
      <div class="flex items-center gap-2 mt-4">
        <button
          @click="handleSaveSkill"
          :disabled="skillSaving"
          class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {{ skillSaving ? 'Saving...' : editingSkillId ? 'Save Skill' : 'Create Skill' }}
        </button>
        <button
          @click="resetSkillComposer"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
        >
          Cancel
        </button>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <div class="text-base font-semibold text-[var(--text-primary)]">Skill Library</div>
          <div class="text-sm text-[var(--text-secondary)] mt-1">
            Separate reusable templates from project-owned skills.
          </div>
        </div>
        <input
          v-model="skillSearch"
          type="text"
          class="h-11 min-w-[240px] rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
          placeholder="Search skills"
        />
      </div>

      <div class="flex flex-wrap gap-2 mt-4">
        <button
          type="button"
          class="px-4 py-2 rounded-[14px] text-sm font-medium transition-colors"
          :class="skillLibraryTab === 'your-skills'
            ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
            : 'border border-[var(--glass-border-strong)] text-[var(--text-primary)] hover:bg-[var(--glass-surface)]'"
          @click="skillLibraryTab = 'your-skills'"
        >
          Your Skills
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-[14px] text-sm font-medium transition-colors"
          :class="skillLibraryTab === 'example-skills'
            ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
            : 'border border-[var(--glass-border-strong)] text-[var(--text-primary)] hover:bg-[var(--glass-surface)]'"
          @click="skillLibraryTab = 'example-skills'"
        >
          Example Skills
        </button>
      </div>

      <div class="flex flex-col gap-3 mt-4">
        <article
          v-for="skill in visibleSkills"
          :key="skill.skill_id"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
        >
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-semibold text-[var(--text-primary)]">{{ skill.name }}</span>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)] uppercase tracking-[0.08em]"
                >
                  {{ skill.is_example ? 'Example' : 'Project' }}
                </span>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] border"
                  :class="skill.enabled ? 'border-[var(--function-success)] text-[var(--function-success)]' : 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]'"
                >
                  {{ skill.enabled ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
              <div v-if="skill.description" class="text-sm text-[var(--text-secondary)] mt-2">{{ skill.description }}</div>
              <div class="text-sm text-[var(--text-secondary)] mt-2 whitespace-pre-wrap break-words">{{ skill.instructions }}</div>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                v-if="skill.is_example"
                @click="applySkillTemplate(skill)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                Use Template
              </button>
              <button
                v-if="!skill.is_example"
                @click="toggleSkill(skill)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                {{ skill.enabled ? 'Disable' : 'Enable' }}
              </button>
              <button
                v-if="!skill.is_example"
                @click="startEditingSkill(skill)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                Edit
              </button>
              <button
                v-if="!skill.is_example"
                @click="handleDeleteSkill(skill.skill_id)"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)]"
              >
                Delete
              </button>
            </div>
          </div>
        </article>
        <div v-if="visibleSkills.length === 0" class="rounded-[18px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]">
          {{ skillLibraryTab === 'your-skills' ? 'No project skills match this filter yet.' : 'No example skills match this filter.' }}
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import {
  createSkill,
  createWorker,
  deleteSkill,
  deleteWorker,
  getMemory,
  getSkills,
  getWorkers,
  updateMemory,
  updateSkill,
  updateWorker,
} from '@/api/capabilities'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useProjects } from '@/composables/useProjects'
import type { SkillResponse, WorkerLane, WorkerResponse, WorkerRole } from '@/types/response'
import { showErrorToast, showSuccessToast } from '@/utils/toast'

const { activeProjectId, getProjectById, hydrateProjects } = useProjects()

const activeProject = computed(() => getProjectById(activeProjectId.value))
const currentProjectId = computed(() => activeProject.value.system ? null : activeProject.value.id)

const workflowLaneDefinitions = [
  { id: 'intake' as const, label: 'Intake', description: 'Clarify the request, gather constraints, and structure the mission.' },
  { id: 'research' as const, label: 'Research', description: 'Collect evidence, inspect context, and validate assumptions.' },
  { id: 'execution' as const, label: 'Execution', description: 'Write code, operate tools, and produce the main artifacts.' },
  { id: 'delivery' as const, label: 'Delivery', description: 'Polish outputs, verify quality, and prepare the handoff.' },
]

const workerRoleOptions: Array<{ value: WorkerRole; label: string }> = [
  { value: 'coordinator', label: 'Coordinator' },
  { value: 'research', label: 'Research' },
  { value: 'developer', label: 'Developer' },
  { value: 'browser', label: 'Browser' },
  { value: 'document', label: 'Document' },
  { value: 'automation', label: 'Automation' },
  { value: 'custom', label: 'Custom' },
]

const skills = ref<SkillResponse[]>([])
const workers = ref<WorkerResponse[]>([])
const skillSearch = ref('')
const skillLibraryTab = ref<'your-skills' | 'example-skills'>('your-skills')
const memoryContent = ref('')
const memorySaving = ref(false)
const skillSaving = ref(false)
const workerSaving = ref(false)
const isSkillComposerOpen = ref(false)
const isWorkerComposerOpen = ref(false)
const editingSkillId = ref<string | null>(null)
const editingWorkerId = ref<string | null>(null)

const skillForm = reactive({
  name: '',
  description: '',
  instructions: '',
  enabled: true,
})

const workerForm = reactive({
  name: '',
  description: '',
  role: 'custom' as WorkerRole,
  lane: 'execution' as WorkerLane,
  instructions: '',
  toolsText: '',
  enabled: true,
})

const workflowLaneCards = computed(() => {
  return workflowLaneDefinitions.map((lane) => ({
    ...lane,
    workers: workers.value.filter((worker) => worker.lane === lane.id),
  }))
})

const filteredSkills = computed(() => {
  const query = skillSearch.value.trim().toLowerCase()
  if (!query) return skills.value
  return skills.value.filter((skill) =>
    [skill.name, skill.description || '', skill.instructions]
      .join(' ')
      .toLowerCase()
      .includes(query),
  )
})

const userSkills = computed(() => filteredSkills.value.filter((skill) => !skill.is_example))
const exampleSkills = computed(() => filteredSkills.value.filter((skill) => skill.is_example))
const visibleSkills = computed(() => (skillLibraryTab.value === 'your-skills' ? userSkills.value : exampleSkills.value))

const parseToolsText = (toolsText: string) =>
  toolsText
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)

const resetSkillComposer = () => {
  isSkillComposerOpen.value = false
  editingSkillId.value = null
  skillForm.name = ''
  skillForm.description = ''
  skillForm.instructions = ''
  skillForm.enabled = true
}

const resetWorkerComposer = () => {
  isWorkerComposerOpen.value = false
  editingWorkerId.value = null
  workerForm.name = ''
  workerForm.description = ''
  workerForm.role = 'custom'
  workerForm.lane = 'execution'
  workerForm.instructions = ''
  workerForm.toolsText = ''
  workerForm.enabled = true
}

const toggleSkillComposer = () => {
  if (isSkillComposerOpen.value) {
    resetSkillComposer()
    return
  }
  isSkillComposerOpen.value = true
}

const toggleWorkerComposer = () => {
  if (isWorkerComposerOpen.value) {
    resetWorkerComposer()
    return
  }
  isWorkerComposerOpen.value = true
}

const reload = async () => {
  const [skillData, memoryData, workerData] = await Promise.all([
    getSkills(currentProjectId.value),
    getMemory(currentProjectId.value),
    getWorkers(currentProjectId.value),
  ])
  skills.value = skillData.skills
  memoryContent.value = memoryData.content || ''
  workers.value = workerData.workers
}

const handleSaveMemory = async () => {
  memorySaving.value = true
  try {
    await updateMemory(currentProjectId.value, memoryContent.value)
    showSuccessToast('Project memory saved')
  } catch (error) {
    console.error('Failed to save memory:', error)
    showErrorToast('Failed to save project memory')
  } finally {
    memorySaving.value = false
  }
}

const handleSaveWorker = async () => {
  if (!workerForm.name.trim() || !workerForm.instructions.trim()) {
    showErrorToast('Worker name and instructions are required')
    return
  }

  workerSaving.value = true
  try {
    const payload = {
      project_id: currentProjectId.value,
      name: workerForm.name.trim(),
      description: workerForm.description.trim() || null,
      role: workerForm.role,
      lane: workerForm.lane,
      instructions: workerForm.instructions.trim(),
      tool_names: parseToolsText(workerForm.toolsText),
      enabled: workerForm.enabled,
    }
    if (editingWorkerId.value) {
      await updateWorker(editingWorkerId.value, payload)
      showSuccessToast('Worker updated')
    } else {
      await createWorker(payload)
      showSuccessToast('Worker created')
    }
    await reload()
    resetWorkerComposer()
  } catch (error) {
    console.error('Failed to save worker:', error)
    showErrorToast('Failed to save worker')
  } finally {
    workerSaving.value = false
  }
}

const startEditingWorker = (worker: WorkerResponse) => {
  editingWorkerId.value = worker.worker_id
  isWorkerComposerOpen.value = true
  workerForm.name = worker.name
  workerForm.description = worker.description || ''
  workerForm.role = worker.role
  workerForm.lane = worker.lane
  workerForm.instructions = worker.instructions
  workerForm.toolsText = worker.tool_names.join(', ')
  workerForm.enabled = worker.enabled
}

const toggleWorker = async (worker: WorkerResponse) => {
  try {
    await updateWorker(worker.worker_id, { enabled: !worker.enabled })
    showSuccessToast(worker.enabled ? 'Worker disabled' : 'Worker enabled')
    await reload()
  } catch (error) {
    console.error('Failed to toggle worker:', error)
    showErrorToast('Failed to update worker')
  }
}

const handleDeleteWorker = async (workerId: string) => {
  if (!window.confirm('Delete this worker?')) return
  try {
    await deleteWorker(workerId)
    showSuccessToast('Worker deleted')
    await reload()
  } catch (error) {
    console.error('Failed to delete worker:', error)
    showErrorToast('Failed to delete worker')
  }
}

const handleSaveSkill = async () => {
  if (!skillForm.name.trim() || !skillForm.instructions.trim()) {
    showErrorToast('Skill name and instructions are required')
    return
  }

  skillSaving.value = true
  try {
    if (editingSkillId.value) {
      await updateSkill(editingSkillId.value, {
        project_id: currentProjectId.value,
        name: skillForm.name.trim(),
        description: skillForm.description.trim() || null,
        instructions: skillForm.instructions.trim(),
        enabled: skillForm.enabled,
      })
      showSuccessToast('Skill updated')
    } else {
      await createSkill({
        project_id: currentProjectId.value,
        name: skillForm.name.trim(),
        description: skillForm.description.trim() || null,
        instructions: skillForm.instructions.trim(),
        enabled: skillForm.enabled,
      })
      showSuccessToast('Skill created')
    }
    await reload()
    resetSkillComposer()
  } catch (error) {
    console.error('Failed to save skill:', error)
    showErrorToast('Failed to save skill')
  } finally {
    skillSaving.value = false
  }
}

const startEditingSkill = (skill: SkillResponse) => {
  editingSkillId.value = skill.skill_id
  isSkillComposerOpen.value = true
  skillForm.name = skill.name
  skillForm.description = skill.description || ''
  skillForm.instructions = skill.instructions
  skillForm.enabled = skill.enabled
}

const applySkillTemplate = (skill: SkillResponse) => {
  editingSkillId.value = null
  isSkillComposerOpen.value = true
  skillForm.name = skill.name
  skillForm.description = skill.description || ''
  skillForm.instructions = skill.instructions
  skillForm.enabled = true
  skillLibraryTab.value = 'your-skills'
}

const toggleSkill = async (skill: SkillResponse) => {
  try {
    await updateSkill(skill.skill_id, {
      enabled: !skill.enabled,
    })
    showSuccessToast(skill.enabled ? 'Skill disabled' : 'Skill enabled')
    await reload()
  } catch (error) {
    console.error('Failed to toggle skill:', error)
    showErrorToast('Failed to update skill')
  }
}

const handleDeleteSkill = async (skillId: string) => {
  if (!window.confirm('Delete this skill?')) return
  try {
    await deleteSkill(skillId)
    showSuccessToast('Skill deleted')
    await reload()
  } catch (error) {
    console.error('Failed to delete skill:', error)
    showErrorToast('Failed to delete skill')
  }
}

onMounted(async () => {
  try {
    await hydrateProjects()
    await reload()
  } catch (error) {
    console.error('Failed to load workforce settings:', error)
    showErrorToast('Failed to load workforce, skills, and memory')
  }
})

watch(currentProjectId, async () => {
  try {
    await reload()
  } catch (error) {
    console.error('Failed to reload workforce settings:', error)
  }
})
</script>
