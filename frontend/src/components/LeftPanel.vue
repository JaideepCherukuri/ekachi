<template>
  <div :class="isLeftPanelShow ?
    'h-full flex flex-col' :
    'h-full flex flex-col fixed top-0 start-0 bottom-0 z-[1]'" :style="isLeftPanelShow ?
      'width: 300px; transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);' :
      'width: 24px; transition: width 0.36s cubic-bezier(0.4, 0, 0.2, 1);'">
    <div
      :class="isLeftPanelShow ?
        'ek-glass-panel flex flex-col overflow-hidden h-full opacity-100 translate-x-0 rounded-[28px]' :
        'ek-glass-panel flex flex-col overflow-hidden fixed top-1 start-1 bottom-1 z-[1] rounded-xl opacity-0 pointer-events-none -translate-x-10'"
      :style="(isLeftPanelShow ? 'width: 300px;' : 'width: 0px;') + ' transition: opacity 0.2s, transform 0.2s, width 0.2s;'">

      <!-- 顶部折叠按钮 -->
      <div class="flex items-center px-3 h-[52px] flex-shrink-0">
        <div class="flex justify-between w-full px-1 pt-2">
          <div class="relative flex">
            <div
              class="flex h-7 w-7 items-center justify-center cursor-pointer hover:bg-[var(--fill-tsp-gray-main)] rounded-md"
              @click="toggleLeftPanel">
              <PanelLeft class="h-5 w-5 text-[var(--icon-secondary)]" />
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷入口区域 -->
      <div class="flex flex-col flex-1 min-h-0 px-[8px] pb-0 gap-px">
        <div class="px-[2px] pb-2">
          <div class="ek-glass-soft rounded-[16px] p-2 flex flex-col gap-2">
            <div class="flex items-center justify-between gap-2 px-1">
              <div class="text-[13px] font-medium text-[var(--text-tertiary)] tracking-[-0.091px]">
                Projects
              </div>
              <div
                @click="toggleCreateProject"
                class="flex h-7 w-7 items-center justify-center cursor-pointer hover:bg-[var(--glass-surface-soft)] rounded-md"
              >
                <FolderPlus class="h-4 w-4 text-[var(--icon-secondary)]" />
              </div>
            </div>

            <div v-if="isCreatingProject" class="px-1">
              <input
                v-model="newProjectName"
                @keydown.enter.prevent="handleCreateProject"
                @keydown.esc="cancelCreateProject"
                class="w-full h-9 rounded-[10px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-disable)]"
                placeholder="New project name"
              />
            </div>

            <div class="flex flex-col gap-1">
              <div
                v-for="project in projects"
                :key="project.id"
                class="group flex items-center gap-2 rounded-[12px] px-2 py-2 cursor-pointer transition-colors"
                :class="activeProjectId === project.id ? 'bg-[var(--glass-surface)]' : 'hover:bg-[var(--glass-surface-soft)]'"
                @click="handleProjectSelect(project.id)"
              >
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: project.color }"></span>
                <span class="flex-1 min-w-0 truncate text-[13px] text-[var(--text-primary)] font-medium">
                  {{ project.name }}
                </span>
                <span class="text-[11px] text-[var(--text-tertiary)]">
                  {{ getProjectSessionCount(project.id) }}
                </span>
                <div
                  v-if="!project.system"
                  @click.stop="handleProjectMenuClick($event, project.id)"
                  class="group-hover:flex hidden size-7 rounded-[8px] cursor-pointer items-center justify-center hover:bg-[var(--glass-surface-soft)]"
                  :class="projectMenuOpenId === project.id ? '!flex bg-[var(--glass-surface-soft)]' : ''"
                >
                  <Ellipsis :size="16" class="text-[var(--icon-tertiary)]" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 新建任务 -->
        <div
          @click="handleNewTaskClick"
          class="flex items-center rounded-[10px] cursor-pointer transition-colors w-full gap-[12px] h-[36px] ps-[9px] pe-[2px]"
          :class="route.path === '/' ? 'bg-[var(--glass-surface-soft)]' : 'hover:bg-[var(--glass-surface-soft)]'">
          <div class="shrink-0 size-[18px] flex items-center justify-center">
            <SquarePen :size="18" class="text-[var(--text-primary)]" />
          </div>
          <div class="flex-1 min-w-0 flex gap-[4px] items-center text-[14px] text-[var(--text-primary)]">
            <span class="truncate">{{ t('New Task') }}</span>
          </div>
          <div class="shrink-0 flex items-center gap-1 pe-[6px]">
            <span class="flex text-[var(--text-tertiary)] justify-center items-center h-5 px-1 rounded-[4px] bg-[var(--fill-tsp-white-light)] border border-[var(--border-light)]">
              <Command :size="12" />
            </span>
            <span class="flex justify-center items-center w-5 h-5 px-1 rounded-[4px] bg-[var(--fill-tsp-white-light)] border border-[var(--border-light)] text-xs text-[var(--text-tertiary)]">
              K
            </span>
          </div>
        </div>

        <!-- Claw 入口 -->
        <div
          v-if="clawEnabled"
          @click="handleClawClick"
          class="flex items-center rounded-[10px] cursor-pointer transition-colors w-full gap-[12px] h-[36px] ps-[9px] pe-[2px]"
          :class="route.path === '/chat/claw' ? 'bg-[var(--glass-surface-soft)]' : 'hover:bg-[var(--glass-surface-soft)]'">
          <div class="shrink-0 size-[18px] flex items-center justify-center">
            <div class="claw-nav-icon w-[18px] h-[18px]" />
          </div>
          <div class="flex-1 min-w-0 flex gap-[4px] items-center text-[14px] text-[var(--text-primary)]">
            <span class="truncate">Ekachi Claw</span>
          </div>
        </div>

        <div
          @click="handleAutomationClick"
          class="flex items-center rounded-[10px] cursor-pointer transition-colors w-full gap-[12px] h-[36px] ps-[9px] pe-[2px]"
          :class="route.path === '/chat/automation' ? 'bg-[var(--glass-surface-soft)]' : 'hover:bg-[var(--glass-surface-soft)]'">
          <div class="shrink-0 size-[18px] flex items-center justify-center">
            <Zap :size="18" class="text-[var(--text-primary)]" />
          </div>
          <div class="flex-1 min-w-0 flex gap-[4px] items-center text-[14px] text-[var(--text-primary)]">
            <span class="truncate">Automation</span>
          </div>
        </div>

        <div
          @click="handleControlCenterClick"
          class="flex items-center rounded-[10px] cursor-pointer transition-colors w-full gap-[12px] h-[36px] ps-[9px] pe-[2px]"
          :class="route.path === '/chat/control' || route.path === '/chat/history'
            ? 'bg-[var(--glass-surface-soft)]'
            : 'hover:bg-[var(--glass-surface-soft)]'">
          <div class="shrink-0 size-[18px] flex items-center justify-center">
            <LayoutGrid :size="18" class="text-[var(--text-primary)]" />
          </div>
          <div class="flex-1 min-w-0 flex gap-[4px] items-center text-[14px] text-[var(--text-primary)]">
            <span class="truncate">Control Center</span>
          </div>
        </div>

        <!-- 所有任务分组标题 + 会话列表 -->
        <div class="flex flex-col flex-1 min-h-0 -mx-[8px] mt-[4px] overflow-hidden">
          <div class="w-full border-t border-[var(--border-main)] transition-opacity duration-200" :class="isListScrolled ? 'opacity-100' : 'opacity-0'"></div>

          <!-- 滚动容器：标题 + 列表一起滚动 -->
          <div ref="scrollContainerRef" class="flex flex-col flex-1 min-h-0 overflow-y-auto overflow-x-hidden pb-5 px-[8px]" @scroll="handleListScroll">

            <!-- 分组标题 -->
            <div
              class="group flex items-center justify-between ps-[10px] pe-[2px] py-[2px] h-[36px] gap-[12px] flex-shrink-0 cursor-pointer hover:bg-[var(--fill-tsp-white-light)] transition-colors rounded-[10px]"
              :class="isListScrolled ? 'bg-[var(--glass-surface-soft)]' : ''"
              @click="isAllTasksCollapsed = !isAllTasksCollapsed">
              <div class="flex items-center flex-1 min-w-0 gap-0.5">
                <span class="text-[13px] leading-[18px] text-[var(--text-tertiary)] font-medium min-w-0 truncate tracking-[-0.091px]">
                  {{ activeProject.name }} · {{ t('All Tasks') }}
                </span>
                <ChevronUp
                  :size="14"
                  class="shrink-0 transition-all opacity-0 group-hover:opacity-100"
                  :class="isAllTasksCollapsed ? 'rotate-180' : 'rotate-90'"
                  stroke="var(--icon-tertiary)" />
              </div>
            </div>

            <!-- 会话列表 -->
            <template v-if="!isAllTasksCollapsed">
              <div v-if="filteredSessions.length > 0" class="flex flex-col gap-px">
                <SessionItem
                  v-for="session in filteredSessions"
                  :key="session.session_id"
                  :session="session"
                  @deleted="handleSessionDeleted" />
              </div>
              <div v-else class="flex flex-col items-center justify-center gap-4 py-8">
                <div class="flex flex-col items-center gap-2 text-[var(--text-tertiary)]">
                  <MessageSquareDashed :size="38" />
                  <span class="text-sm font-medium">{{ t('Create a task to get started') }}</span>
                </div>
              </div>
            </template>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, onUnmounted } from 'vue';
import { ChevronUp, Command, Ellipsis, FolderPlus, LayoutGrid, MessageSquareDashed, PanelLeft, SquarePen, Pencil, Trash, Zap } from 'lucide-vue-next';
import SessionItem from './SessionItem.vue';
import { useLeftPanel } from '../composables/useLeftPanel';
import { useRoute, useRouter } from 'vue-router';
import { getSessionsSSE, getSessions } from '../api/agent';
import { getCachedClientConfig } from '../api/config';
import { ListSessionItem } from '../types/response';
import { useI18n } from 'vue-i18n';
import { useProjects } from '@/composables/useProjects';
import { useContextMenu, createDangerMenuItem, createMenuItem } from '@/composables/useContextMenu';
import { useDialog } from '@/composables/useDialog';

const { t } = useI18n()
const { isLeftPanelShow, toggleLeftPanel } = useLeftPanel()
const route = useRoute()
const router = useRouter()
const { showContextMenu } = useContextMenu()
const { showConfirmDialog } = useDialog()
const {
  projects,
  activeProjectId,
  getProjectById,
  getProjectIdForSession,
  setActiveProject,
  hydrateProjects,
  createProjectRemote,
  renameProjectRemote,
  deleteProjectRemote,
  removeSessionFromProjects,
  syncSessions
} = useProjects()

const sessions = ref<ListSessionItem[]>([])
const cancelGetSessionsSSE = ref<(() => void) | null>(null)
const isAllTasksCollapsed = ref(false)
const isListScrolled = ref(false)
const clawEnabled = ref(false)
const scrollContainerRef = ref<HTMLElement | null>(null)
const isCreatingProject = ref(false)
const newProjectName = ref('')
const projectMenuOpenId = ref<string | null>(null)

const activeProject = computed(() => getProjectById(activeProjectId.value))
const filteredSessions = computed(() => {
  return sessions.value.filter((session) => getProjectIdForSession(session.session_id) === activeProjectId.value)
})

const handleListScroll = () => {
  if (scrollContainerRef.value) {
    isListScrolled.value = scrollContainerRef.value.scrollTop > 0
  }
}

// Function to fetch sessions data
const updateSessions = async () => {
  try {
    const response = await getSessions()
    sessions.value = response.sessions
    syncSessions(response.sessions)
  } catch (error) {
    console.error('Failed to fetch sessions:', error)
  }
}

// Function to fetch sessions data
const fetchSessions = async () => {
  try {
    if (cancelGetSessionsSSE.value) {
      cancelGetSessionsSSE.value()
      cancelGetSessionsSSE.value = null
    }
    cancelGetSessionsSSE.value = await getSessionsSSE({
      onOpen: () => {
        console.log('Sessions SSE opened')
      },
      onMessage: (event) => {
        sessions.value = event.data.sessions
        syncSessions(event.data.sessions)
      },
      onError: (error) => {
        console.error('Failed to fetch sessions:', error)
      },
      onClose: () => {
        console.log('Sessions SSE closed')
      }
    })
  } catch (error) {
    console.error('Failed to fetch sessions:', error)
  }
}

const handleNewTaskClick = () => {
  router.push('/')
}

const getProjectSessionCount = (projectId: string) => {
  return sessions.value.filter((session) => getProjectIdForSession(session.session_id) === projectId).length
}

const toggleCreateProject = () => {
  isCreatingProject.value = !isCreatingProject.value
  if (!isCreatingProject.value) {
    newProjectName.value = ''
  }
}

const cancelCreateProject = () => {
  isCreatingProject.value = false
  newProjectName.value = ''
}

const handleCreateProject = async () => {
  try {
    const created = await createProjectRemote(newProjectName.value)
    if (!created) return
    newProjectName.value = ''
    isCreatingProject.value = false
  } catch (error) {
    console.error('Failed to create project:', error)
  }
}

const handleProjectSelect = (projectId: string) => {
  setActiveProject(projectId)
}

const handleProjectMenuClick = (event: MouseEvent, projectId: string) => {
  const target = event.currentTarget as HTMLElement
  projectMenuOpenId.value = projectId
  showContextMenu(projectId, target, [
    createMenuItem('rename', 'Rename', { icon: Pencil }),
    createDangerMenuItem('delete', 'Delete', { icon: Trash }),
  ], (itemKey, id) => {
    if (itemKey === 'rename') {
      const project = getProjectById(id)
      const nextName = window.prompt('Rename project', project.name)
      if (nextName) {
        renameProjectRemote(id, nextName).catch((error) => {
          console.error('Failed to rename project:', error)
        })
      }
    }

    if (itemKey === 'delete') {
      showConfirmDialog({
        title: 'Delete project?',
        content: 'Sessions in this project will be moved back to Inbox.',
        confirmText: 'Delete',
        cancelText: 'Cancel',
        confirmType: 'danger',
        onConfirm: async () => {
          await deleteProjectRemote(id)
          await updateSessions()
        }
      })
    }
  }, () => {
    projectMenuOpenId.value = null
  })
}

const handleClawClick = () => {
  router.push('/chat/claw')
}

const handleAutomationClick = () => {
  router.push('/chat/automation')
}

const handleControlCenterClick = () => {
  router.push('/chat/control')
}

const handleSessionDeleted = (sessionId: string) => {
  console.log('handleSessionDeleted', sessionId)
  sessions.value = sessions.value.filter(session => session.session_id !== sessionId);
  removeSessionFromProjects(sessionId)
}

// Handle keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  // Check for Command + K (Mac) or Ctrl + K (Windows/Linux)
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault()
    handleNewTaskClick()
  }
}

onMounted(async () => {
  getCachedClientConfig().then(cfg => {
    clawEnabled.value = cfg?.claw_enabled ?? false
  })

  try {
    await hydrateProjects()
  } catch (error) {
    console.error('Failed to hydrate projects:', error)
  }
  // Initial fetch of sessions
  fetchSessions()

  // Add keyboard event listener
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (cancelGetSessionsSSE.value) {
    cancelGetSessionsSSE.value()
    cancelGetSessionsSSE.value = null
  }

  // Remove keyboard event listener
  window.removeEventListener('keydown', handleKeydown)
})

watch(() => route.path, async () => {
  const currentSessionId = route.params.sessionId as string | undefined
  if (currentSessionId) {
    setActiveProject(getProjectIdForSession(currentSessionId))
  }
  await updateSessions()
})

watch(() => route.params.sessionId, (sessionId) => {
  if (typeof sessionId === 'string') {
    setActiveProject(getProjectIdForSession(sessionId))
  }
}, { immediate: true })
</script>

<style scoped>
.claw-nav-icon {
  background: url("data:image/svg+xml,%3csvg%20xmlns='http://www.w3.org/2000/svg'%20width='20'%20height='20'%20fill='none'%20viewBox='0%200%2020%2020'%20opacity='0.84'%3e%3cpath%20fill='%23333'%20fill-opacity='.9'%20fill-rule='evenodd'%20d='M5.724%204.379c3.934-3.078%207.519-2.009%208.808-.972.675.543%201.05%201.332.97%202.126-.082.823-.64%201.509-1.529%201.805-.463.155-.831.552-.998%201.034-.168.485-.1.942.144%201.24l.027.035a1%201%200%200%201%20.077.018c.265.08.413.122.617.076.202-.046.58-.215%201.13-.88l.127-.136a1.44%201.44%200%200%201%201.082-.402c.418.022.797.215%201.075.482.32.31.466.77.526%201.17.065.43.051.928-.057%201.434-.217%201.017-.837%202.142-2.09%202.82-.402.217-1.098.61-2.146.663a5%205%200%200%201-.376.504c-1.007%201.196-2.394%201.608-3.628%201.57a5.1%205.1%200%200%201-1.6-.312%203.4%203.4%200%200%201-.612.59c-.413.298-.985.518-1.667.347-1.319-.33-2.607-1.6-3.249-3.17-.344-.843-.14-1.573.285-2.087.228-.275.509-.48.777-.624a7.4%207.4%200%200%201-.33-2.307c.037-1.671.705-3.512%202.637-5.024m7.867.197c-.748-.602-3.56-1.662-6.942.985-1.551%201.213-2.034%202.618-2.061%203.874a6.1%206.1%200%200%200%20.805%203.094.75.75%200%200%201-1.29.766q-.05-.09-.103-.188a1%201%200%200%200-.203.182.47.47%200%200%200-.11.22.6.6%200%200%200%20.057.343c.515%201.26%201.491%202.1%202.225%202.285.138.035.262.008.425-.11q.096-.07.188-.167a3%203%200%200%201-.137-.145.75.75%200%200%201%201.136-.98c.294.34%201.034.704%201.948.732.877.027%201.782-.262%202.435-1.037.652-.774.809-1.508.746-2.142-.063-.632-.354-1.218-.711-1.672-.13-.103-.398-.251-.777-.376a4.1%204.1%200%200%200-1.234-.213.75.75%200%200%201%200-1.5c.469%200%20.955.077%201.4.198.017-.29.076-.576.169-.844.297-.856.974-1.644%201.942-1.966.378-.127.492-.348.51-.532.022-.213-.074-.53-.418-.807m2.527%205.25c-.675.81-1.314%201.235-1.947%201.378q-.082.017-.16.027c.093.287.16.591.192.91a4%204%200%200%201-.046%201.116c.299-.098.542-.23.763-.349.79-.428%201.19-1.134%201.336-1.812.073-.341.077-.657.04-.898-.033-.222-.087-.31-.09-.319a.3.3%200%200%200-.067-.046q-.013-.006-.021-.007'%20clip-rule='evenodd'%20/%3e%3c%2fsvg%3e") no-repeat center;
  background-size: contain;
}

:global(.dark) .claw-nav-icon {
  background-image: url("data:image/svg+xml,%3csvg%20xmlns='http://www.w3.org/2000/svg'%20width='20'%20height='20'%20fill='none'%20viewBox='0%200%2020%2020'%20opacity='0.84'%3e%3cpath%20fill='%23fff'%20fill-opacity='.9'%20fill-rule='evenodd'%20d='M5.724%204.379c3.934-3.078%207.519-2.009%208.808-.972.675.543%201.05%201.332.97%202.126-.082.823-.64%201.509-1.529%201.805-.463.155-.831.552-.998%201.034-.168.485-.1.942.144%201.24l.027.035a1%201%200%200%201%20.077.018c.265.08.413.122.617.076.202-.046.58-.215%201.13-.88l.127-.136a1.44%201.44%200%200%201%201.082-.402c.418.022.797.215%201.075.482.32.31.466.77.526%201.17.065.43.051.928-.057%201.434-.217%201.017-.837%202.142-2.09%202.82-.402.217-1.098.61-2.146.663a5%205%200%200%201-.376.504c-1.007%201.196-2.394%201.608-3.628%201.57a5.1%205.1%200%200%201-1.6-.312%203.4%203.4%200%200%201-.612.59c-.413.298-.985.518-1.667.347-1.319-.33-2.607-1.6-3.249-3.17-.344-.843-.14-1.573.285-2.087.228-.275.509-.48.777-.624a7.4%207.4%200%200%201-.33-2.307c.037-1.671.705-3.512%202.637-5.024m7.867.197c-.748-.602-3.56-1.662-6.942.985-1.551%201.213-2.034%202.618-2.061%203.874a6.1%206.1%200%200%200%20.805%203.094.75.75%200%200%201-1.29.766q-.05-.09-.103-.188a1%201%200%200%200-.203.182.47.47%200%200%200-.11.22.6.6%200%200%200%20.057.343c.515%201.26%201.491%202.1%202.225%202.285.138.035.262.008.425-.11q.096-.07.188-.167a3%203%200%200%201-.137-.145.75.75%200%200%201%201.136-.98c.294.34%201.034.704%201.948.732.877.027%201.782-.262%202.435-1.037.652-.774.809-1.508.746-2.142-.063-.632-.354-1.218-.711-1.672-.13-.103-.398-.251-.777-.376a4.1%204.1%200%200%200-1.234-.213.75.75%200%200%201%200-1.5c.469%200%20.955.077%201.4.198.017-.29.076-.576.169-.844.297-.856.974-1.644%201.942-1.966.378-.127.492-.348.51-.532.022-.213-.074-.53-.418-.807m2.527%205.25c-.675.81-1.314%201.235-1.947%201.378q-.082.017-.16.027c.093.287.16.591.192.91a4%204%200%200%201-.046%201.116c.299-.098.542-.23.763-.349.79-.428%201.19-1.134%201.336-1.812.073-.341.077-.657.04-.898-.033-.222-.087-.31-.09-.319a.3.3%200%200%200-.067-.046q-.013-.006-.021-.007'%20clip-rule='evenodd'%20/%3e%3c%2fsvg%3e");
}
</style>
