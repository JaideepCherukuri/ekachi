<template>
  <SimpleBar ref="simpleBarRef" @scroll="handleScroll">
    <div class="relative flex flex-col h-full flex-1 min-w-0 px-3 sm:px-5">
      <div
        class="ek-sticky-glass sm:min-w-[390px] flex flex-row items-center justify-between pt-3 pb-2 gap-1 sticky top-0 z-10 flex-shrink-0">
        <div class="flex items-center flex-1">
          <div class="relative flex items-center">
            <div @click="toggleLeftPanel" v-if="!isLeftPanelShow"
              class="flex h-7 w-7 items-center justify-center cursor-pointer rounded-md hover:bg-[var(--fill-tsp-gray-main)]">
              <PanelLeft class="size-5 text-[var(--icon-secondary)]" />
            </div>
          </div>
        </div>
        <div class="max-w-full sm:max-w-[768px] sm:min-w-[390px] flex w-full flex-col gap-[4px] overflow-hidden">
          <div
            class="text-[var(--text-primary)] text-lg font-medium w-full flex flex-row items-center justify-between flex-1 min-w-0 gap-2">
            <div class="flex flex-row items-center gap-[6px] flex-1 min-w-0">
              <span class="whitespace-nowrap text-ellipsis overflow-hidden">
                {{ title }}
              </span>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="relative flex-shrink-0" aria-expanded="false" aria-haspopup="dialog">
                <Popover>
                  <PopoverTrigger>
                    <button
                      class="h-8 px-3 rounded-[100px] inline-flex items-center gap-1 clickable outline outline-1 outline-offset-[-1px] outline-[var(--border-btn-main)] hover:bg-[var(--fill-tsp-white-light)] me-1.5">
                      <ShareIcon color="var(--icon-secondary)" />
                      <span class="text-[var(--text-secondary)] text-sm font-medium">{{ t('Share') }}</span>
                    </button>
                  </PopoverTrigger>
                  <PopoverContent>
                    <div
                      class="w-[min(400px,calc(100vw-16px))] flex flex-col rounded-2xl bg-[var(--background-menu-white)] shadow-[0px_8px_32px_0px_var(--shadow-S),0px_0px_0px_1px_var(--border-light)]">
                      <div class="flex flex-col pt-[12px] px-[16px] pb-[16px]">
                        <!-- Private mode option -->
                        <div @click="handleShareModeChange('private')"
                          :class="{'pointer-events-none opacity-50': sharingLoading}"
                          class="flex items-center gap-[10px] px-[8px] -mx-[8px] py-[8px] rounded-[8px] clickable hover:bg-[var(--fill-tsp-white-main)]">
                          <div
                            :class="shareMode === 'private' ? 'bg-[var(--Button-primary-black)]' : 'bg-[var(--fill-tsp-white-dark)]'"
                            class="w-[32px] h-[32px] rounded-[8px] flex items-center justify-center">
                            <Lock :size="16" :stroke="shareMode === 'private' ? 'var(--text-onblack)' : 'var(--icon-primary)'" :stroke-width="2" /></div>
                          <div class="flex flex-col flex-1 min-w-0">
                            <div class="text-sm font-medium text-[var(--text-primary)]">{{ t('Private Only') }}</div>
                            <div class="text-[13px] text-[var(--text-tertiary)]">{{ t('Only visible to you') }}</div>
                          </div><Check :size="20" :class="shareMode === 'private' ? 'ml-auto' : 'ml-auto invisible'" :color="shareMode === 'private' ? 'var(--icon-primary)' : 'var(--icon-tertiary)'" />
                        </div>
                        <!-- Public mode option -->
                        <div @click="handleShareModeChange('public')"
                          :class="{'pointer-events-none opacity-50': sharingLoading}"
                          class="flex items-center gap-[10px] px-[8px] -mx-[8px] py-[8px] rounded-[8px] clickable hover:bg-[var(--fill-tsp-white-main)]">
                          <div
                            :class="shareMode === 'public' ? 'bg-[var(--Button-primary-black)]' : 'bg-[var(--fill-tsp-white-dark)]'"
                            class="w-[32px] h-[32px] rounded-[8px] flex items-center justify-center">
                            <Globe :size="16" :stroke="shareMode === 'public' ? 'var(--text-onblack)' : 'var(--icon-primary)'" :stroke-width="2" /></div>
                          <div class="flex flex-col flex-1 min-w-0">
                            <div class="text-sm font-medium text-[var(--text-primary)]">{{ t('Public Access') }}</div>
                            <div class="text-[13px] text-[var(--text-tertiary)]">{{ t('Anyone with the link can view') }}</div>
                          </div><Check :size="20" :class="shareMode === 'public' ? 'ml-auto' : 'ml-auto invisible'" :color="shareMode === 'public' ? 'var(--icon-primary)' : 'var(--icon-tertiary)'" />
                        </div>
                        <div class="border-t border-[var(--border-main)] mt-[4px]"></div>
                        
                        <!-- Show instant share button when in private mode -->
                        <div v-if="shareMode === 'private'">
                          <button @click.stop="handleInstantShare"
                            :disabled="sharingLoading"
                            class="inline-flex items-center justify-center whitespace-nowrap font-medium transition-colors hover:opacity-90 active:opacity-80 bg-[var(--Button-primary-black)] text-[var(--text-onblack)] h-[36px] px-[12px] rounded-[10px] gap-[6px] text-sm min-w-16 mt-[16px] w-full disabled:opacity-50 disabled:cursor-not-allowed"
                            data-tabindex="" tabindex="-1">
                            <div v-if="sharingLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <Link v-else :size="16" stroke="currentColor" :stroke-width="2" />
                            {{ sharingLoading ? t('Sharing...') : t('Share Instantly') }}
                          </button>
                        </div>
                        
                        <!-- Show copy link button when in public mode -->
                        <div v-else>
                          <button @click.stop="handleCopyLink"
                            :class="linkCopied ? 'inline-flex items-center justify-center whitespace-nowrap font-medium transition-colors active:opacity-80 bg-[var(--Button-primary-white)] text-[var(--text-primary)] hover:opacity-70 active:hover-60 h-[36px] px-[12px] rounded-[10px] gap-[6px] text-sm min-w-16 mt-[16px] w-full border border-[var(--border-btn-main)] shadow-none' : 'inline-flex items-center justify-center whitespace-nowrap font-medium transition-colors hover:opacity-90 active:opacity-80 bg-[var(--Button-primary-black)] text-[var(--text-onblack)] h-[36px] px-[12px] rounded-[10px] gap-[6px] text-sm min-w-16 mt-[16px] w-full'"
                            data-tabindex="" tabindex="-1">
                            <Link v-if="!linkCopied" :size="16" stroke="currentColor" :stroke-width="2" />
                            <Check v-else :size="16" color="var(--text-primary)" />
                            {{ linkCopied ? t('Link Copied') : t('Copy Link') }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
              </span>
              <button @click="handleFileListShow"
                class="p-[5px] flex items-center justify-center hover:bg-[var(--fill-tsp-white-dark)] rounded-lg cursor-pointer">
                <FileSearch class="text-[var(--icon-secondary)]" :size="18" />
              </button>
            </div>
          </div>
          <div class="w-full flex justify-between items-center gap-3 flex-wrap">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] text-xs text-[var(--text-secondary)]">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: currentProject.color }"></span>
                <span>{{ currentProject.name }}</span>
              </span>
              <span class="text-xs text-[var(--text-tertiary)]">
                Workspace
              </span>
            </div>
            <div class="flex items-center gap-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] p-1">
              <button
                v-for="tab in workspaceTabs"
                :key="tab.id"
                @click="handleWorkspaceChange(tab.id)"
                class="px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
                :class="workspaceView === tab.id
                  ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--glass-surface)]'"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>
        </div>
        <div class="flex-1"></div>
      </div>
      <div class="mx-auto w-full max-w-full sm:max-w-[768px] sm:min-w-[390px] flex flex-col flex-1">
        <div
          v-if="workspaceView !== 'chat'"
          class="ek-glass-card rounded-[20px] p-4 mb-3"
        >
          <template v-if="workspaceView === 'plan'">
            <div class="flex items-center justify-between gap-3">
              <div>
                <div class="text-base font-semibold text-[var(--text-primary)]">Plan Workspace</div>
                <div class="text-sm text-[var(--text-secondary)] mt-1">
                  {{ completedPlanSteps }} of {{ totalPlanSteps }} steps completed.
                </div>
              </div>
            </div>
            <div class="flex flex-col gap-2 mt-4">
              <div
                v-for="step in plan?.steps || []"
                :key="step.id"
                class="flex items-center gap-3 rounded-[14px] px-3 py-2 border border-[var(--glass-border)] bg-[var(--glass-surface-soft)]"
              >
                <span
                  class="w-2.5 h-2.5 rounded-full"
                  :class="step.status === 'completed'
                    ? 'bg-[var(--function-success)]'
                    : step.status === 'running'
                      ? 'bg-[var(--text-brand)]'
                      : step.status === 'failed'
                        ? 'bg-[var(--function-error)]'
                        : 'bg-[var(--text-disable)]'"
                />
                <span class="text-sm text-[var(--text-primary)]">{{ step.description }}</span>
              </div>
              <div v-if="!plan || plan.steps.length === 0" class="text-sm text-[var(--text-tertiary)]">
                No plan has been emitted for this session yet.
              </div>
            </div>
          </template>

          <template v-else-if="workspaceView === 'workflow'">
            <div class="flex items-center justify-between gap-3">
              <div>
                <div class="text-base font-semibold text-[var(--text-primary)]">Workflow Workspace</div>
                <div class="text-sm text-[var(--text-secondary)] mt-1">
                  Execution timeline across messages, steps, and tools.
                </div>
              </div>
              <div class="text-xs text-[var(--text-tertiary)]">
                {{ workflowItems.length }} events
              </div>
            </div>
            <div class="flex flex-col gap-2 mt-4">
              <div
                v-for="item in workflowItems"
                :key="item.id"
                class="rounded-[14px] px-3 py-3 border border-[var(--glass-border)] bg-[var(--glass-surface-soft)]"
              >
                <div class="flex items-center justify-between gap-3">
                  <div class="flex items-center gap-2 min-w-0">
                    <span
                      class="w-2.5 h-2.5 rounded-full shrink-0"
                      :class="item.tone"
                    />
                    <span class="text-sm font-medium text-[var(--text-primary)]">{{ item.title }}</span>
                  </div>
                  <span class="text-[11px] text-[var(--text-tertiary)] uppercase tracking-[0.08em]">{{ item.kind }}</span>
                </div>
                <div class="text-sm text-[var(--text-secondary)] mt-2 break-words">
                  {{ item.description }}
                </div>
              </div>
              <div v-if="workflowItems.length === 0" class="text-sm text-[var(--text-tertiary)]">
                No execution activity has been recorded in this session yet.
              </div>
            </div>
          </template>

          <template v-else-if="workspaceView === 'workers'">
            <div class="flex items-center justify-between gap-3">
              <div>
                <div class="text-base font-semibold text-[var(--text-primary)]">Workers Workspace</div>
                <div class="text-sm text-[var(--text-secondary)] mt-1">
                  Specialist views derived from the current session runtime.
                </div>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
              <div
                v-for="worker in workerCards"
                :key="worker.id"
                class="rounded-[18px] px-4 py-4 border border-[var(--glass-border)] bg-[var(--glass-surface-soft)]"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <div class="text-sm font-semibold text-[var(--text-primary)]">{{ worker.name }}</div>
                    <div class="text-sm text-[var(--text-secondary)] mt-1">{{ worker.description }}</div>
                  </div>
                  <span
                    class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-[11px] font-medium border"
                    :class="worker.statusClass"
                  >
                    <span class="w-2 h-2 rounded-full" :class="worker.dotClass" />
                    {{ worker.status }}
                  </span>
                </div>
                <div class="grid grid-cols-2 gap-2 mt-4">
                  <div class="rounded-[14px] bg-[var(--glass-surface)] px-3 py-2">
                    <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Activity</div>
                    <div class="text-lg font-semibold text-[var(--text-primary)] mt-1">{{ worker.activityCount }}</div>
                  </div>
                  <div class="rounded-[14px] bg-[var(--glass-surface)] px-3 py-2">
                    <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Latest</div>
                    <div class="text-sm font-medium text-[var(--text-primary)] mt-1 truncate">{{ worker.latestLabel }}</div>
                  </div>
                </div>
                <button
                  v-if="worker.lastTool"
                  @click="handleToolClick(worker.lastTool)"
                  class="mt-4 px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                >
                  Open Latest Tool
                </button>
              </div>
            </div>
          </template>

          <template v-else-if="workspaceView === 'files'">
            <div class="flex items-center justify-between gap-3 flex-wrap">
              <div>
                <div class="text-base font-semibold text-[var(--text-primary)]">Files Workspace</div>
                <div class="text-sm text-[var(--text-secondary)] mt-1">
                  Session files and generated artifacts for this run.
                </div>
              </div>
              <button
                @click="showSessionFileList()"
                class="px-3 py-2 rounded-[12px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90"
              >
                Open File Browser
              </button>
            </div>
            <div class="flex flex-col gap-2 mt-4">
              <div
                v-for="file in sessionFiles"
                :key="file.file_id"
                class="flex items-center justify-between gap-3 rounded-[14px] px-3 py-2 border border-[var(--glass-border)] bg-[var(--glass-surface-soft)]"
              >
                <div class="min-w-0">
                  <div class="text-sm font-medium text-[var(--text-primary)] truncate">{{ file.filename }}</div>
                  <div class="text-xs text-[var(--text-tertiary)]">{{ file.content_type || 'File' }}</div>
                </div>
              </div>
              <div v-if="sessionFiles.length === 0" class="text-sm text-[var(--text-tertiary)]">
                No session files available yet.
              </div>
            </div>
          </template>

          <template v-else-if="workspaceView === 'browser'">
            <div class="flex items-center justify-between gap-3 flex-wrap">
              <div>
                <div class="text-base font-semibold text-[var(--text-primary)]">Browser Workspace</div>
                <div class="text-sm text-[var(--text-secondary)] mt-1">
                  Live browser context and most recent browser tool activity.
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="openBrowserWorkspace"
                  :disabled="!browserTool"
                  class="px-3 py-2 rounded-[12px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
                >
                  Open Browser
                </button>
                <button
                  @click="triggerTakeOver"
                  :disabled="!browserTool"
                  class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
                >
                  Take Over
                </button>
              </div>
            </div>
            <div class="mt-4 rounded-[14px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-3">
              <div v-if="browserTool" class="flex flex-col gap-1">
                <div class="text-sm font-medium text-[var(--text-primary)]">{{ browserTool.function }}</div>
                <div class="text-sm text-[var(--text-secondary)] break-all">
                  {{ browserTool.args?.url || browserTool.args?.page || browserTool.args?.element || 'Browser interaction available in tool panel' }}
                </div>
              </div>
              <div v-else class="text-sm text-[var(--text-tertiary)]">
                No browser activity has been recorded in this session yet.
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
              <div class="rounded-[14px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-3">
                <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Engine</div>
                <div class="text-sm font-medium text-[var(--text-primary)] mt-2">
                  {{ sessionBrowserProfile.engine || 'System default' }}
                </div>
              </div>
              <div class="rounded-[14px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-3">
                <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">CDP Endpoint</div>
                <div class="text-sm font-medium text-[var(--text-primary)] mt-2 break-all">
                  {{ sessionBrowserProfile.cdpUrl || 'Sandbox managed browser' }}
                </div>
              </div>
              <div class="rounded-[14px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-3">
                <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Cookie Profile</div>
                <div class="text-sm font-medium text-[var(--text-primary)] mt-2">
                  {{ sessionBrowserProfile.cookieProfile ? 'Configured' : 'Not configured' }}
                </div>
              </div>
              <div class="rounded-[14px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-3">
                <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Extensions</div>
                <div class="text-sm font-medium text-[var(--text-primary)] mt-2">
                  {{ sessionBrowserProfile.extensionPaths.length }} configured
                </div>
              </div>
              <div class="rounded-[14px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-3">
                <div class="text-[11px] uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Cookie Jar</div>
                <div class="text-sm font-medium text-[var(--text-primary)] mt-2">
                  {{ sessionBrowserProfile.cookieCount }} persisted
                </div>
              </div>
            </div>
          </template>
        </div>
        <div class="flex flex-col w-full gap-[12px] pb-[80px] pt-[12px] flex-1 overflow-y-auto">
          <ChatMessage v-for="(message, index) in messages" :key="index" :message="message"
            :hideHeader="isConsecutiveAssistant(messages, index)"
            @toolClick="handleToolClick" />

          <!-- Loading indicator -->
          <LoadingIndicator v-if="isLoading" :text="$t('Thinking')" />
        </div>

        <div class="ek-sticky-glass flex flex-col sticky bottom-0 pb-1">
          <button @click="handleFollow" v-if="!follow"
            class="ek-glass-card flex items-center justify-center w-[36px] h-[36px] rounded-full clickable absolute -top-20 left-1/2 -translate-x-1/2">
            <ArrowDown class="text-[var(--icon-primary)]" :size="20" />
          </button>
          <PlanPanel v-if="plan && plan.steps.length > 0" :plan="plan" />
          <ChatBox v-model="inputMessage" :rows="1" @submit="handleSubmit" :isRunning="isLoading" @stop="handleStop"
            :attachments="attachments" />
        </div>
      </div>
    </div>
    <ToolPanel ref="toolPanel" :size="toolPanelSize" :sessionId="sessionId" :realTime="realTime" 
      :isShare="false"
      @jumpToRealTime="jumpToRealTime" />
  </SimpleBar>
</template>

<script setup lang="ts">
import SimpleBar from '../components/SimpleBar.vue';
import { ref, onMounted, watch, nextTick, onUnmounted, reactive, toRefs, computed } from 'vue';
import { useRouter, onBeforeRouteUpdate } from 'vue-router';
import { useI18n } from 'vue-i18n';
import ChatBox from '../components/ChatBox.vue';
import ChatMessage from '../components/ChatMessage.vue';
import * as agentApi from '../api/agent';
import { Message, MessageContent, ToolContent, StepContent, AttachmentsContent, isConsecutiveAssistant } from '../types/message';
import {
  StepEventData,
  ToolEventData,
  MessageEventData,
  ErrorEventData,
  TitleEventData,
  PlanEventData,
  AgentSSEEvent,
} from '../types/event';
import ToolPanel from '../components/ToolPanel.vue'
import PlanPanel from '../components/PlanPanel.vue';
import { ArrowDown, FileSearch, PanelLeft, Lock, Globe, Link, Check } from 'lucide-vue-next';
import ShareIcon from '@/components/icons/ShareIcon.vue';
import { showErrorToast, showSuccessToast } from '../utils/toast';
import type { FileInfo } from '../api/file';
import { useLeftPanel } from '../composables/useLeftPanel'
import { useSessionFileList } from '../composables/useSessionFileList'
import { useFilePanel } from '../composables/useFilePanel'
import { copyToClipboard } from '../utils/dom'
import { SessionStatus } from '../types/response';
import type { WorkerResponse } from '../types/response';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import LoadingIndicator from '@/components/ui/LoadingIndicator.vue';
import type { ProjectItem } from '@/composables/useProjects';
import { useProjects } from '@/composables/useProjects';
import { getWorkers } from '@/api/capabilities';

const router = useRouter()
const { t } = useI18n()
const { toggleLeftPanel, isLeftPanelShow } = useLeftPanel()
const { showSessionFileList } = useSessionFileList()
const { hideFilePanel } = useFilePanel()
const { getProjectForSession, syncSession } = useProjects()

// Create initial state factory
const createInitialState = () => ({
  inputMessage: '',
  isLoading: false,
  sessionId: undefined as string | undefined,
  messages: [] as Message[],
  toolPanelSize: 0,
  realTime: true,
  follow: true,
  title: t('New Chat'),
  plan: undefined as PlanEventData | undefined,
  lastNoMessageTool: undefined as ToolContent | undefined,
  lastMessageTool: undefined as ToolContent | undefined,
  lastTool: undefined as ToolContent | undefined,
  lastEventId: undefined as string | undefined,
  cancelCurrentChat: null as (() => void) | null,
  attachments: [] as FileInfo[],
  shareMode: 'private' as 'private' | 'public', // Default to private mode
  linkCopied: false,
  sharingLoading: false // Loading state for share operations
});

// Create reactive state
const state = reactive(createInitialState());

// Destructure refs from reactive state
const {
  inputMessage,
  isLoading,
  sessionId,
  messages,
  toolPanelSize,
  realTime,
  follow,
  title,
  plan,
  lastNoMessageTool,
  lastTool,
  lastEventId,
  cancelCurrentChat,
  attachments,
  shareMode,
  linkCopied,
  sharingLoading
} = toRefs(state);

// Non-state refs that don't need reset
const toolPanel = ref<InstanceType<typeof ToolPanel>>()
const simpleBarRef = ref<InstanceType<typeof SimpleBar>>();
type WorkspaceView = 'chat' | 'plan' | 'workflow' | 'workers' | 'files' | 'browser'

const workspaceView = ref<WorkspaceView>('chat')
const sessionFiles = ref<FileInfo[]>([])
const sessionProjectMeta = ref<ProjectItem | null>(null)
const configuredWorkers = ref<WorkerResponse[]>([])
const sessionBrowserProfile = ref({
  engine: null as string | null,
  cdpUrl: null as string | null,
  cookieProfile: null as string | null,
  extensionPaths: [] as string[],
  cookieCount: 0,
})

const workspaceTabs = [
  { id: 'chat' as const, label: 'Chat' },
  { id: 'plan' as const, label: 'Plan' },
  { id: 'workflow' as const, label: 'Workflow' },
  { id: 'workers' as const, label: 'Workers' },
  { id: 'files' as const, label: 'Files' },
  { id: 'browser' as const, label: 'Browser' },
]

const currentProject = computed(() => {
  if (sessionProjectMeta.value) {
    return sessionProjectMeta.value
  }
  return getProjectForSession(sessionId.value || '')
})
const totalPlanSteps = computed(() => plan.value?.steps.length || 0)
const completedPlanSteps = computed(() => plan.value?.steps.filter((step) => step.status === 'completed').length || 0)
const browserTool = computed(() => {
  const tools = messages.value.filter((message) => message.type === 'tool')
  const lastBrowserTool = [...tools].reverse().find((message) => (message.content as ToolContent).name === 'browser')
  return lastBrowserTool?.content as ToolContent | undefined
})

const workflowItems = computed(() => {
  return messages.value.map((message, index) => {
    if (message.type === 'step') {
      const step = message.content as StepContent
      return {
        id: `step-${index}-${step.id}`,
        kind: 'step',
        title: step.description,
        description: `Step ${step.status}`,
        tone: step.status === 'completed'
          ? 'bg-[var(--function-success)]'
          : step.status === 'failed'
            ? 'bg-[var(--function-error)]'
            : 'bg-[var(--text-brand)]',
      }
    }
    if (message.type === 'tool') {
      const tool = message.content as ToolContent
      return {
        id: `tool-${index}-${tool.tool_call_id}`,
        kind: 'tool',
        title: `${tool.name} tool`,
        description: tool.args?.url || tool.args?.command || tool.args?.file || tool.function || tool.status,
        tone: tool.status === 'called' ? 'bg-[var(--function-success)]' : 'bg-[var(--text-brand)]',
      }
    }
    if (message.type === 'user' || message.type === 'assistant') {
      const content = message.content as MessageContent
      return {
        id: `message-${index}-${message.type}`,
        kind: message.type,
        title: message.type === 'user' ? 'User message' : 'Assistant response',
        description: content.content,
        tone: message.type === 'user' ? 'bg-[var(--text-brand)]' : 'bg-[var(--text-primary)]',
      }
    }
    if (message.type === 'attachments') {
      const content = message.content as AttachmentsContent
      return {
        id: `attachments-${index}`,
        kind: 'files',
        title: 'Attachments',
        description: `${content.attachments.length} file attachment${content.attachments.length === 1 ? '' : 's'}`,
        tone: 'bg-[var(--function-warning)]',
      }
    }
    return {
      id: `activity-${index}`,
      kind: message.type,
      title: message.type,
      description: '',
      tone: 'bg-[var(--text-tertiary)]',
    }
  })
})

const roleToolDefaults: Record<string, string[]> = {
  coordinator: [],
  research: ['search'],
  developer: ['shell', 'file'],
  browser: ['browser'],
  document: ['file'],
  automation: ['browser', 'shell', 'file'],
  custom: [],
}

const roleDescriptions: Record<string, string> = {
  coordinator: 'Owns plan generation, orchestration, and final responses.',
  research: 'Handles evidence gathering and source validation.',
  developer: 'Handles shell execution, file operations, and implementation work.',
  browser: 'Handles browsing, navigation, and interactive page work.',
  document: 'Handles artifacts, structured outputs, and document workflows.',
  automation: 'Handles recurring operations, scheduled actions, and runtime follow-through.',
  custom: 'Custom worker instructions for this project.',
}

const workerCards = computed(() => {
  const toolMessages = messages.value
    .filter((message) => message.type === 'tool')
    .map((message) => message.content as ToolContent)
  const latestPlanStep = plan.value?.steps[plan.value.steps.length - 1]

  const workerDefinitions = configuredWorkers.value.length > 0
    ? configuredWorkers.value.map((worker) => ({
        id: worker.worker_id,
        name: worker.name,
        description: worker.description || roleDescriptions[worker.role] || roleDescriptions.custom,
        role: worker.role,
        lane: worker.lane,
        tools: worker.tool_names.length > 0 ? worker.tool_names : (roleToolDefaults[worker.role] || []),
        activityCount: 0,
        latestLabel: worker.instructions,
        status: worker.enabled ? 'Ready' : 'Disabled',
        lastTool: undefined as ToolContent | undefined,
        enabled: worker.enabled,
      }))
    : [
        {
          id: 'coordinator',
          name: 'Coordinator',
          description: roleDescriptions.coordinator,
          role: 'coordinator',
          lane: 'intake',
          tools: [] as string[],
          activityCount: (plan.value?.steps.length || 0) + messages.value.filter((message) => message.type === 'assistant').length,
          latestLabel: latestPlanStep?.description || 'No plan activity yet',
          status: isLoading.value ? 'Active' : totalPlanSteps.value > 0 ? 'Ready' : 'Idle',
          lastTool: undefined as ToolContent | undefined,
          enabled: true,
        },
        {
          id: 'research',
          name: 'Research Worker',
          description: roleDescriptions.research,
          role: 'research',
          lane: 'research',
          tools: ['search'],
          enabled: true,
        },
        {
          id: 'developer',
          name: 'Developer Worker',
          description: roleDescriptions.developer,
          role: 'developer',
          lane: 'execution',
          tools: ['shell', 'file'],
          enabled: true,
        },
        {
          id: 'browser',
          name: 'Browser Worker',
          description: roleDescriptions.browser,
          role: 'browser',
          lane: 'execution',
          tools: ['browser'],
          enabled: true,
        },
      ]

  return workerDefinitions.map((worker) => {
    if (worker.role === 'coordinator') {
      return {
        ...worker,
        statusClass: worker.status === 'Active'
          ? 'border-[var(--glass-border-strong)] text-[var(--text-primary)]'
          : worker.status === 'Disabled'
            ? 'border-[var(--glass-border)] text-[var(--text-tertiary)]'
          : 'border-[var(--glass-border)] text-[var(--text-secondary)]',
        dotClass: worker.status === 'Active'
          ? 'bg-[var(--text-brand)]'
          : worker.status === 'Disabled'
            ? 'bg-[var(--text-disable)]'
            : 'bg-[var(--function-success)]',
      }
    }

    const matchingTools = toolMessages.filter((tool) => worker.tools.includes(tool.name))
    const lastTool = matchingTools[matchingTools.length - 1]
    const status = !worker.enabled
      ? 'Disabled'
      : matchingTools.length > 0
        ? (lastTool?.status === 'calling' ? 'Active' : 'Ready')
        : 'Idle'
    return {
      ...worker,
      activityCount: matchingTools.length,
      latestLabel: lastTool?.function || lastTool?.name || 'No activity yet',
      status,
      lastTool,
      statusClass: status === 'Active'
        ? 'border-[var(--glass-border-strong)] text-[var(--text-primary)]'
        : status === 'Ready'
          ? 'border-[var(--glass-border)] text-[var(--text-secondary)]'
          : status === 'Disabled'
            ? 'border-[var(--glass-border)] text-[var(--text-tertiary)]'
          : 'border-[var(--glass-border)] text-[var(--text-tertiary)]',
      dotClass: status === 'Active'
        ? 'bg-[var(--text-brand)]'
        : status === 'Ready'
          ? 'bg-[var(--function-success)]'
          : 'bg-[var(--text-disable)]',
    }
  })
})

const loadSessionFiles = async () => {
  if (!sessionId.value) return
  try {
    sessionFiles.value = await agentApi.getSessionFiles(sessionId.value)
  } catch (error) {
    console.error('Failed to load session files:', error)
    sessionFiles.value = []
  }
}

const openBrowserWorkspace = () => {
  if (!browserTool.value) return
  toolPanel.value?.showToolPanel(browserTool.value, true)
}

const triggerTakeOver = () => {
  if (!sessionId.value || !browserTool.value) return
  openBrowserWorkspace()
  window.dispatchEvent(new CustomEvent('takeover', {
    detail: {
      sessionId: sessionId.value,
      active: true,
    }
  }))
}

const handleWorkspaceChange = (workspace: WorkspaceView) => {
  workspaceView.value = workspace
  if (workspace === 'files') {
    loadSessionFiles()
  }
  if (workspace === 'browser') {
    openBrowserWorkspace()
  }
}

// Reset all refs to their initial values
const resetState = () => {
  // Cancel any existing chat connection
  if (cancelCurrentChat.value) {
    cancelCurrentChat.value();
  }

  // Reset reactive state to initial values
  Object.assign(state, createInitialState());
  workspaceView.value = 'chat'
  sessionFiles.value = []
  sessionProjectMeta.value = null
  configuredWorkers.value = []
  sessionBrowserProfile.value = {
    engine: null,
    cdpUrl: null,
    cookieProfile: null,
    extensionPaths: [],
    cookieCount: 0,
  }
};

const loadConfiguredWorkers = async (projectId?: string | null) => {
  try {
    const response = await getWorkers(projectId ?? undefined)
    configuredWorkers.value = response.workers
  } catch (error) {
    console.error('Failed to load configured workers:', error)
    configuredWorkers.value = []
  }
}

// Watch message changes and automatically scroll to bottom
watch(messages, async () => {
  await nextTick();
  if (follow.value) {
    simpleBarRef.value?.scrollToBottom();
  }
}, { deep: true });



const getLastStep = (): StepContent | undefined => {
  return messages.value.filter(message => message.type === 'step').pop()?.content as StepContent;
}

// Handle message event
const handleMessageEvent = (messageData: MessageEventData) => {
  messages.value.push({
    type: messageData.role,
    content: {
      ...messageData
    } as MessageContent,
  });

  if (messageData.attachments?.length > 0) {
    messages.value.push({
      type: 'attachments',
      content: {
        ...messageData
      } as AttachmentsContent,
    });
  }
}

// Handle tool event
const handleToolEvent = (toolData: ToolEventData) => {
  const lastStep = getLastStep();
  let toolContent: ToolContent = {
    ...toolData
  }
  if (lastTool.value && lastTool.value.tool_call_id === toolContent.tool_call_id) {
    Object.assign(lastTool.value, toolContent);
  } else {
    if (lastStep?.status === 'running') {
      lastStep.tools.push(toolContent);
    } else {
      messages.value.push({
        type: 'tool',
        content: toolContent,
      });
    }
    lastTool.value = toolContent;
  }
  if (toolContent.name !== 'message') {
    lastNoMessageTool.value = toolContent;
    if (realTime.value) {
      toolPanel.value?.showToolPanel(toolContent, true);
    }
  }
}

// Handle step event
const handleStepEvent = (stepData: StepEventData) => {
  const lastStep = getLastStep();
  if (stepData.status === 'running') {
    messages.value.push({
      type: 'step',
      content: {
        ...stepData,
        tools: []
      } as StepContent,
    });
  } else if (stepData.status === 'completed') {
    if (lastStep) {
      lastStep.status = stepData.status;
    }
  } else if (stepData.status === 'failed') {
    isLoading.value = false;
  }
}

// Handle error event
const handleErrorEvent = (errorData: ErrorEventData) => {
  isLoading.value = false;
  messages.value.push({
    type: 'assistant',
    content: {
      content: errorData.error,
      timestamp: errorData.timestamp
    } as MessageContent,
  });
}

// Handle title event
const handleTitleEvent = (titleData: TitleEventData) => {
  title.value = titleData.title;
}

// Handle plan event
const handlePlanEvent = (planData: PlanEventData) => {
  plan.value = planData;
}

// Main event handler function
const handleEvent = (event: AgentSSEEvent) => {
  if (event.event === 'message') {
    handleMessageEvent(event.data as MessageEventData);
  } else if (event.event === 'tool') {
    handleToolEvent(event.data as ToolEventData);
  } else if (event.event === 'step') {
    handleStepEvent(event.data as StepEventData);
  } else if (event.event === 'done') {
    //isLoading.value = false;
  } else if (event.event === 'wait') {
    // TODO: handle wait event
  } else if (event.event === 'error') {
    handleErrorEvent(event.data as ErrorEventData);
  } else if (event.event === 'title') {
    handleTitleEvent(event.data as TitleEventData);
  } else if (event.event === 'plan') {
    handlePlanEvent(event.data as PlanEventData);
  }
  lastEventId.value = event.data.event_id;
}

const handleSubmit = () => {
  chat(inputMessage.value, attachments.value);
}

const chat = async (message: string = '', files: FileInfo[] = []) => {
  if (!sessionId.value) return;

  // Cancel any existing chat connection before starting a new one
  if (cancelCurrentChat.value) {
    cancelCurrentChat.value();
    cancelCurrentChat.value = null;
  }

  if (message.trim()) {
    // Add user message to conversation list
    messages.value.push({
      type: 'user',
      content: {
        content: message,
        timestamp: Math.floor(Date.now() / 1000)
      } as MessageContent,
    });
  }

  if (files.length > 0) {
    messages.value.push({
      type: 'attachments',
      content: {
        role: 'user',
        attachments: files
      } as AttachmentsContent,
    });
  }

  // Automatically enable follow mode when sending message
  follow.value = true;

  // Clear input field and attachments
  inputMessage.value = '';
  attachments.value = [];
  isLoading.value = true;

  try {
    // Use the split event handler function and store the cancel function
    cancelCurrentChat.value = await agentApi.chatWithSession(
      sessionId.value,
      message,
      lastEventId.value,
      files.map((file: FileInfo) => ({file_id : file.file_id, 
                                        filename : file.filename})),
      {
        onOpen: () => {
          console.log('Chat opened');
          isLoading.value = true;
        },
        onMessage: ({ event, data }) => {
          handleEvent({
            event: event as AgentSSEEvent['event'],
            data: data as AgentSSEEvent['data']
          });
        },
        onClose: () => {
          console.log('Chat closed');
          isLoading.value = false;
          loadSessionFiles();
          // Clear the cancel function when connection is closed normally
          if (cancelCurrentChat.value) {
            cancelCurrentChat.value = null;
          }
        },
        onError: (error) => {
          console.error('Chat error:', error);
          isLoading.value = false;
          // Clear the cancel function when there's an error
          if (cancelCurrentChat.value) {
            cancelCurrentChat.value = null;
          }
        }
      }
    );
  } catch (error) {
    console.error('Chat error:', error);
    isLoading.value = false;
    cancelCurrentChat.value = null;
  }
}

const restoreSession = async () => {
  if (!sessionId.value) {
    showErrorToast(t('Session not found'));
    return;
  }
  const session = await agentApi.getSession(sessionId.value);
  syncSession({
    session_id: session.session_id,
    project_id: session.project_id,
    project_name: session.project_name,
    project_color: session.project_color,
  })
  sessionProjectMeta.value = {
    id: session.project_id || getProjectForSession(session.session_id).id,
    name: session.project_name || getProjectForSession(session.session_id).name,
    color: session.project_color || getProjectForSession(session.session_id).color,
    created_at: 0,
    system: !session.project_id,
  }
  sessionBrowserProfile.value = {
    engine: session.browser_engine || null,
    cdpUrl: session.browser_cdp_url || null,
    cookieProfile: session.browser_cookie_profile || null,
    extensionPaths: session.browser_extension_paths || [],
    cookieCount: session.browser_cookies?.length || 0,
  }
  // Initialize share mode based on session state
  shareMode.value = session.is_shared ? 'public' : 'private';
  realTime.value = false;
  for (const event of session.events) {
    handleEvent(event);
  }
  realTime.value = true;
  if (session.status === SessionStatus.RUNNING || session.status === SessionStatus.PENDING) {
    await chat();
  }
  await loadConfiguredWorkers(session.project_id || null)
  await loadSessionFiles();
  agentApi.clearUnreadMessageCount(sessionId.value);
}



onBeforeRouteUpdate((to, _, next) => {
  toolPanel.value?.hideToolPanel();
  hideFilePanel();
  resetState();
  if (to.params.sessionId) {
    messages.value = [];
    sessionId.value = String(to.params.sessionId) as string;
    restoreSession();
  }
  next();
})

// Initialize active conversation
onMounted(() => {
  hideFilePanel();
  const routeParams = router.currentRoute.value.params;
  if (routeParams.sessionId) {
    // If sessionId is included in URL, use it directly
    sessionId.value = String(routeParams.sessionId) as string;
    // Get initial message from history.state
    const message = history.state?.message;
    const files: FileInfo[] = history.state?.files;
    history.replaceState({}, document.title);
    if (message) {
      chat(message, files);
    } else {
      restoreSession();
    }
  }


});

onUnmounted(() => {
  if (cancelCurrentChat.value) {
    cancelCurrentChat.value();
    cancelCurrentChat.value = null;
  }
})

const isLastNoMessageTool = (tool: ToolContent) => {
  return tool.tool_call_id === lastNoMessageTool.value?.tool_call_id;
}

const isLiveTool = (tool: ToolContent) => {
  if (tool.status === 'calling') {
    return true;
  }
  if (!isLastNoMessageTool(tool)) {
    return false;
  }
  if (tool.timestamp > Date.now() - 5 * 60 * 1000) {
    return true;
  }
  return false;
}

const handleToolClick = (tool: ToolContent) => {
  realTime.value = false;
  if (sessionId.value) {
    toolPanel.value?.showToolPanel(tool, isLiveTool(tool));
  }
}

const jumpToRealTime = () => {
  realTime.value = true;
  if (lastNoMessageTool.value) {
    toolPanel.value?.showToolPanel(lastNoMessageTool.value, isLiveTool(lastNoMessageTool.value));
  }
}

const handleFollow = () => {
  follow.value = true;
  simpleBarRef.value?.scrollToBottom();
}

const handleScroll = (_: Event) => {
  follow.value = simpleBarRef.value?.isScrolledToBottom() ?? false;
}

const handleStop = () => {
  if (sessionId.value) {
    agentApi.stopSession(sessionId.value);
  }
}

const handleFileListShow = () => {
  showSessionFileList()
}

// Share functionality handlers
const handleShareModeChange = async (mode: 'private' | 'public') => {
  if (!sessionId.value || sharingLoading.value) return;
  
  // If mode is same as current, no need to call API
  if (shareMode.value === mode) {
    linkCopied.value = false;
    return;
  }
  
  try {
    sharingLoading.value = true;
    
    if (mode === 'public') {
      await agentApi.shareSession(sessionId.value);
    } else {
      await agentApi.unshareSession(sessionId.value);
    }
    
    shareMode.value = mode;
    linkCopied.value = false;
  } catch (error) {
    console.error('Error changing share mode:', error);
    showErrorToast(t('Failed to change sharing settings'));
  } finally {
    sharingLoading.value = false;
  }
}

const handleInstantShare = async () => {
  if (!sessionId.value) return;
  
  try {
    sharingLoading.value = true;
    await agentApi.shareSession(sessionId.value);
    shareMode.value = 'public';
    linkCopied.value = false;
  } catch (error) {
    console.error('Error sharing session:', error);
    showErrorToast(t('Failed to share session'));
  } finally {
    sharingLoading.value = false;
  }
}

const handleCopyLink = async () => {
  if (!sessionId.value) return;
  
  const shareUrl = `${window.location.origin}/share/${sessionId.value}`;
  
  try {
    const success = await copyToClipboard(shareUrl);
    
    if (success) {
      linkCopied.value = true;
      setTimeout(() => {
        linkCopied.value = false;
      }, 3000);
      showSuccessToast(t('Link copied to clipboard'));
    } else {
      showErrorToast(t('Failed to copy link'));
    }
  } catch (error) {
    console.error('Error copying share link:', error);
    showErrorToast(t('Failed to copy link'));
  }
}
</script>

<style scoped>
</style>
