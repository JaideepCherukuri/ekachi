import { computed, ref, watch } from 'vue'
import type { ListSessionItem } from '@/types/response'
import {
  createProject as createProjectRequest,
  deleteProject as deleteProjectRequest,
  getProjects,
  updateProject as updateProjectRequest,
} from '@/api/projects'

export interface ProjectItem {
  id: string
  name: string
  color: string
  created_at: number
  system?: boolean
  default_provider_id?: string | null
  default_model_name?: string | null
  preferred_search_provider?: string | null
  preferred_browser_engine?: string | null
  browser_cdp_url?: string | null
  browser_pool?: {
    browser_id: string
    label: string
    cdp_url: string
    source: string
    created_at: string
    updated_at: string
  }[]
  browser_cookie_profile?: string | null
  browser_extension_paths?: string[]
  browser_cookies?: Record<string, unknown>[]
}

const PROJECTS_STORAGE_KEY = 'ekachi-projects'
const PROJECT_SESSION_MAP_STORAGE_KEY = 'ekachi-project-session-map'
const ACTIVE_PROJECT_STORAGE_KEY = 'ekachi-active-project'

const DEFAULT_PROJECT_ID = 'project-inbox'

const DEFAULT_PROJECT: ProjectItem = {
  id: DEFAULT_PROJECT_ID,
  name: 'Inbox',
  color: '#3b82f6',
  created_at: 0,
  system: true,
  default_provider_id: null,
  default_model_name: null,
  preferred_search_provider: null,
  preferred_browser_engine: null,
  browser_cdp_url: null,
  browser_pool: [],
  browser_cookie_profile: null,
  browser_extension_paths: [],
  browser_cookies: [],
}

const PROJECT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']

const canUseStorage = () => typeof window !== 'undefined' && typeof localStorage !== 'undefined'

const loadProjects = (): ProjectItem[] => {
  if (!canUseStorage()) return [DEFAULT_PROJECT]
  try {
    const raw = localStorage.getItem(PROJECTS_STORAGE_KEY)
    if (!raw) return [DEFAULT_PROJECT]
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return [DEFAULT_PROJECT]
    const projects = parsed.filter((item): item is ProjectItem => !!item?.id && !!item?.name)
    const hasDefault = projects.some((project) => project.id === DEFAULT_PROJECT_ID)
    return hasDefault ? projects : [DEFAULT_PROJECT, ...projects]
  } catch (error) {
    console.error('Failed to load projects:', error)
    return [DEFAULT_PROJECT]
  }
}

const loadProjectSessionMap = (): Record<string, string> => {
  if (!canUseStorage()) return {}
  try {
    const raw = localStorage.getItem(PROJECT_SESSION_MAP_STORAGE_KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw)
    return parsed && typeof parsed === 'object' ? parsed : {}
  } catch (error) {
    console.error('Failed to load project session map:', error)
    return {}
  }
}

const loadActiveProjectId = (): string => {
  if (!canUseStorage()) return DEFAULT_PROJECT_ID
  try {
    return localStorage.getItem(ACTIVE_PROJECT_STORAGE_KEY) || DEFAULT_PROJECT_ID
  } catch (error) {
    console.error('Failed to load active project id:', error)
    return DEFAULT_PROJECT_ID
  }
}

const projects = ref<ProjectItem[]>(loadProjects())
const projectSessionMap = ref<Record<string, string>>(loadProjectSessionMap())
const activeProjectId = ref<string>(loadActiveProjectId())
const projectsHydrated = ref(false)
const hydratingProjects = ref(false)

const persistProjects = (value: ProjectItem[]) => {
  if (!canUseStorage()) return
  localStorage.setItem(PROJECTS_STORAGE_KEY, JSON.stringify(value))
}

const persistProjectSessionMap = (value: Record<string, string>) => {
  if (!canUseStorage()) return
  localStorage.setItem(PROJECT_SESSION_MAP_STORAGE_KEY, JSON.stringify(value))
}

const persistActiveProjectId = (value: string) => {
  if (!canUseStorage()) return
  localStorage.setItem(ACTIVE_PROJECT_STORAGE_KEY, value)
}

watch(projects, (value) => {
  persistProjects(value)
}, { deep: true })

watch(projectSessionMap, (value) => {
  persistProjectSessionMap(value)
}, { deep: true })

watch(activeProjectId, (value) => {
  persistActiveProjectId(value)
})

const ensureActiveProject = () => {
  if (!projects.value.some((project) => project.id === activeProjectId.value)) {
    activeProjectId.value = DEFAULT_PROJECT_ID
  }
}

const generateProjectId = () => `project-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`

export function useProjects() {
  const orderedProjects = computed(() => {
    const [defaultProject, ...customProjects] = projects.value
    return [
      defaultProject || DEFAULT_PROJECT,
      ...customProjects.sort((a, b) => a.name.localeCompare(b.name)),
    ]
  })

  const getProjectById = (projectId?: string | null) => {
    return orderedProjects.value.find((project) => project.id === (projectId || DEFAULT_PROJECT_ID)) || DEFAULT_PROJECT
  }

  const getProjectForSession = (sessionId: string) => {
    const projectId = projectSessionMap.value[sessionId] || DEFAULT_PROJECT_ID
    return getProjectById(projectId)
  }

  const getProjectIdForSession = (sessionId: string) => {
    return getProjectForSession(sessionId).id
  }

  const ensureProjectExists = (project: Pick<ProjectItem, 'id' | 'name' | 'color'> & Partial<ProjectItem>) => {
    if (!project.id || project.id === DEFAULT_PROJECT_ID) return
    if (projects.value.some((item) => item.id === project.id)) {
      projects.value = projects.value.map((item) =>
        item.id === project.id
          ? {
              ...item,
              name: project.name || item.name,
              color: project.color || item.color,
              default_provider_id: project.default_provider_id ?? item.default_provider_id ?? null,
              default_model_name: project.default_model_name ?? item.default_model_name ?? null,
              preferred_search_provider: project.preferred_search_provider ?? item.preferred_search_provider ?? null,
              preferred_browser_engine: project.preferred_browser_engine ?? item.preferred_browser_engine ?? null,
              browser_cdp_url: project.browser_cdp_url ?? item.browser_cdp_url ?? null,
              browser_pool: project.browser_pool ?? item.browser_pool ?? [],
              browser_cookie_profile: project.browser_cookie_profile ?? item.browser_cookie_profile ?? null,
              browser_extension_paths: project.browser_extension_paths ?? item.browser_extension_paths ?? [],
              browser_cookies: project.browser_cookies ?? item.browser_cookies ?? [],
            }
          : item
      )
      return
    }
    projects.value = [
      ...projects.value,
      {
        id: project.id,
        name: project.name || 'Untitled Project',
        color: project.color || PROJECT_COLORS[projects.value.length % PROJECT_COLORS.length],
        created_at: Date.now(),
        default_provider_id: project.default_provider_id ?? null,
        default_model_name: project.default_model_name ?? null,
        preferred_search_provider: project.preferred_search_provider ?? null,
        preferred_browser_engine: project.preferred_browser_engine ?? null,
        browser_cdp_url: project.browser_cdp_url ?? null,
        browser_pool: project.browser_pool ?? [],
        browser_cookie_profile: project.browser_cookie_profile ?? null,
        browser_extension_paths: project.browser_extension_paths ?? [],
        browser_cookies: project.browser_cookies ?? [],
      },
    ]
  }

  const assignSessionToProject = (sessionId: string, projectId?: string | null) => {
    const safeProjectId = getProjectById(projectId).id
    projectSessionMap.value = {
      ...projectSessionMap.value,
      [sessionId]: safeProjectId,
    }
  }

  const removeSessionFromProjects = (sessionId: string) => {
    const nextMap = { ...projectSessionMap.value }
    delete nextMap[sessionId]
    projectSessionMap.value = nextMap
  }

  const createProject = (name: string) => {
    const trimmed = name.trim()
    if (!trimmed) return null
    const project: ProjectItem = {
      id: generateProjectId(),
      name: trimmed,
      color: PROJECT_COLORS[projects.value.length % PROJECT_COLORS.length],
      created_at: Date.now(),
    }
    projects.value = [...projects.value, project]
    activeProjectId.value = project.id
    return project
  }

  const hydrateProjects = async (force = false) => {
    if (hydratingProjects.value) return
    if (projectsHydrated.value && !force) return

    hydratingProjects.value = true
    try {
      const response = await getProjects()
      projects.value = [
        DEFAULT_PROJECT,
        ...response.projects.map((project) => ({
          id: project.project_id,
          name: project.name,
          color: project.color,
          created_at: new Date(project.created_at).getTime(),
          default_provider_id: project.default_provider_id ?? null,
          default_model_name: project.default_model_name ?? null,
          preferred_search_provider: project.preferred_search_provider ?? null,
          preferred_browser_engine: project.preferred_browser_engine ?? null,
          browser_cdp_url: project.browser_cdp_url ?? null,
          browser_pool: project.browser_pool ?? [],
          browser_cookie_profile: project.browser_cookie_profile ?? null,
          browser_extension_paths: project.browser_extension_paths ?? [],
          browser_cookies: project.browser_cookies ?? [],
        })),
      ]
      projectsHydrated.value = true
      ensureActiveProject()
    } finally {
      hydratingProjects.value = false
    }
  }

  const createProjectRemote = async (name: string) => {
    const trimmed = name.trim()
    if (!trimmed) return null
    const color = PROJECT_COLORS[projects.value.length % PROJECT_COLORS.length]
    const project = await createProjectRequest({ name: trimmed, color })
    ensureProjectExists({
      id: project.project_id,
      name: project.name,
      color: project.color,
      default_provider_id: project.default_provider_id ?? null,
      default_model_name: project.default_model_name ?? null,
      preferred_search_provider: project.preferred_search_provider ?? null,
      preferred_browser_engine: project.preferred_browser_engine ?? null,
      browser_cdp_url: project.browser_cdp_url ?? null,
      browser_pool: project.browser_pool ?? [],
      browser_cookie_profile: project.browser_cookie_profile ?? null,
      browser_extension_paths: project.browser_extension_paths ?? [],
      browser_cookies: project.browser_cookies ?? [],
    })
    activeProjectId.value = project.project_id
    projectsHydrated.value = true
    return getProjectById(project.project_id)
  }

  const renameProject = (projectId: string, name: string) => {
    const trimmed = name.trim()
    if (!trimmed) return
    projects.value = projects.value.map((project) =>
      project.id === projectId ? { ...project, name: trimmed } : project
    )
  }

  const renameProjectRemote = async (projectId: string, name: string) => {
    const trimmed = name.trim()
    if (!trimmed) return
    const project = await updateProjectRequest(projectId, { name: trimmed })
    projects.value = projects.value.map((item) =>
        item.id === project.project_id
        ? {
            ...item,
            name: project.name,
            color: project.color,
            default_provider_id: project.default_provider_id ?? null,
            default_model_name: project.default_model_name ?? null,
            preferred_search_provider: project.preferred_search_provider ?? null,
            preferred_browser_engine: project.preferred_browser_engine ?? null,
            browser_cdp_url: project.browser_cdp_url ?? null,
            browser_pool: project.browser_pool ?? [],
            browser_cookie_profile: project.browser_cookie_profile ?? null,
            browser_extension_paths: project.browser_extension_paths ?? [],
            browser_cookies: project.browser_cookies ?? [],
          }
        : item
    )
    projectsHydrated.value = true
  }

  const deleteProject = (projectId: string) => {
    if (projectId === DEFAULT_PROJECT_ID) return
    const nextMap = { ...projectSessionMap.value }
    for (const [sessionId, mappedProjectId] of Object.entries(nextMap)) {
      if (mappedProjectId === projectId) {
        nextMap[sessionId] = DEFAULT_PROJECT_ID
      }
    }
    projectSessionMap.value = nextMap
    projects.value = projects.value.filter((project) => project.id !== projectId)
    ensureActiveProject()
  }

  const deleteProjectRemote = async (projectId: string) => {
    if (projectId === DEFAULT_PROJECT_ID) return
    await deleteProjectRequest(projectId)
    deleteProject(projectId)
    projectsHydrated.value = true
  }

  const setActiveProject = (projectId: string) => {
    activeProjectId.value = getProjectById(projectId).id
  }

  const groupSessionsByProject = (sessions: ListSessionItem[]) => {
    return orderedProjects.value.map((project) => ({
      project,
      sessions: sessions.filter((session) => getProjectIdForSession(session.session_id) === project.id),
    }))
  }

  const syncSessions = (sessions: ListSessionItem[]) => {
    const nextMap: Record<string, string> = {}

    for (const session of sessions) {
      const projectId = session.project_id || projectSessionMap.value[session.session_id] || DEFAULT_PROJECT_ID
      if (session.project_id && session.project_name) {
        ensureProjectExists({
          id: session.project_id,
          name: session.project_name,
          color: session.project_color || PROJECT_COLORS[projects.value.length % PROJECT_COLORS.length],
        })
      }
      nextMap[session.session_id] = projectId
    }

    projectSessionMap.value = {
      ...projectSessionMap.value,
      ...nextMap,
    }
    ensureActiveProject()
  }

  const syncSession = (session: Pick<ListSessionItem, 'session_id' | 'project_id' | 'project_name' | 'project_color'>) => {
    syncSessions([{
      session_id: session.session_id,
      title: null,
      latest_message: null,
      latest_message_at: null,
      status: 'pending' as ListSessionItem['status'],
      unread_message_count: 0,
      is_shared: false,
      project_id: session.project_id,
      project_name: session.project_name,
      project_color: session.project_color,
    }])
  }

  ensureActiveProject()

  return {
    projects: orderedProjects,
    activeProjectId,
    projectsHydrated,
    getProjectById,
    getProjectForSession,
    getProjectIdForSession,
    hydrateProjects,
    assignSessionToProject,
    removeSessionFromProjects,
    createProject,
    createProjectRemote,
    renameProject,
    renameProjectRemote,
    deleteProject,
    deleteProjectRemote,
    setActiveProject,
    groupSessionsByProject,
    syncSessions,
    syncSession,
  }
}
