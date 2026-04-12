<template>
  <SimpleBar>
    <div class="flex flex-col h-full flex-1 min-w-0 mx-auto w-full max-w-[1280px] px-3 sm:px-5 pt-4 pb-10 gap-4">
      <section class="ek-sticky-glass rounded-[20px] px-3 py-3 sm:px-4 sm:py-4">
        <div class="flex items-center gap-3">
          <button
            v-if="!isLeftPanelShow"
            type="button"
            class="flex h-8 w-8 items-center justify-center rounded-md text-[var(--icon-secondary)] hover:bg-[var(--fill-tsp-gray-main)]"
            @click="toggleLeftPanel"
          >
            <PanelLeft class="size-5" />
          </button>
          <div class="text-sm font-medium text-[var(--text-secondary)]">Control Center</div>
        </div>
      </section>

      <section class="ek-glass-card rounded-[24px] p-5 sm:p-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-3xl">
            <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
              Control Center
            </div>
            <h1 class="text-[28px] leading-[34px] sm:text-[34px] sm:leading-[40px] font-semibold text-[var(--text-primary)] mt-2">
              Eigent-style workspace surfaces, promoted to first-class routes.
            </h1>
            <p class="text-sm text-[var(--text-secondary)] leading-6 mt-3">
              Ekachi now exposes projects, agents, channels, connectors, browser control, and settings from a dedicated command surface instead of hiding them behind modal navigation.
            </p>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
              @click="refreshActiveTab"
            >
              Refresh View
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-sm font-medium text-[var(--text-onblack)] hover:opacity-90"
              @click="router.push('/chat')"
            >
              New Task
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-5">
          <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Projects</div>
            <div class="text-[28px] font-semibold text-[var(--text-primary)] mt-2">{{ projects.length - 1 }}</div>
            <div class="text-sm text-[var(--text-secondary)] mt-1">Custom projects plus the shared Inbox.</div>
          </article>
          <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Sessions</div>
            <div class="text-[28px] font-semibold text-[var(--text-primary)] mt-2">{{ sessions.length }}</div>
            <div class="text-sm text-[var(--text-secondary)] mt-1">Live and historical task runs available in this workspace.</div>
          </article>
          <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
            <div class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Connected Surfaces</div>
            <div class="text-[28px] font-semibold text-[var(--text-primary)] mt-2">{{ configuredSurfaceCount }}</div>
            <div class="text-sm text-[var(--text-secondary)] mt-1">Provider, connector, and browser surfaces with live runtime state.</div>
          </article>
        </div>
      </section>

      <section class="ek-glass-card rounded-[24px] p-2">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tab in topTabs"
            :key="tab.id"
            type="button"
            class="px-4 py-2.5 rounded-[16px] text-sm font-medium transition-colors"
            :class="activeTab === tab.id
              ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
              : 'text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]'"
            @click="setTopTab(tab.id)"
          >
            {{ tab.label }}
          </button>
        </div>
      </section>

      <section v-if="activeTab === 'projects'" class="flex flex-col gap-4">
        <div class="grid grid-cols-1 xl:grid-cols-[1.4fr_0.9fr] gap-4">
          <article class="ek-glass-card rounded-[24px] p-5">
            <div class="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
                  Project Catalog
                </div>
                <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
                  Workspace Projects
                </div>
                <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
                  Select a project, adjust its defaults, and inspect every session already mapped into it.
                </div>
              </div>
              <button
                type="button"
                class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
                @click="loadWorkspaceData"
              >
                Refresh Projects
              </button>
            </div>

            <div class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4 mt-4 flex flex-col gap-3 md:flex-row md:items-center">
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-[var(--text-primary)]">Create Project</div>
                <div class="text-xs text-[var(--text-tertiary)] mt-1">New sessions and automations can then inherit project-specific model, search, browser, and workforce defaults.</div>
              </div>
              <div class="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                <input
                  v-model="newProjectName"
                  type="text"
                  class="h-11 min-w-[240px] rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
                  placeholder="Go-to-market launch"
                  @keydown.enter.prevent="handleCreateProject"
                />
                <button
                  type="button"
                  class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-sm font-medium text-[var(--text-onblack)] hover:opacity-90 disabled:opacity-50"
                  :disabled="projectActionLoading"
                  @click="handleCreateProject"
                >
                  {{ projectActionLoading ? 'Creating...' : 'Create Project' }}
                </button>
              </div>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-3 mt-4">
              <article
                v-for="project in projects"
                :key="project.id"
                class="rounded-[20px] border px-4 py-4 transition-colors"
                :class="activeProjectId === project.id
                  ? 'border-[var(--text-brand)] bg-[var(--fill-blue)]'
                  : 'border-[var(--glass-border)] bg-[var(--glass-surface-soft)]'"
              >
                <div class="flex items-start justify-between gap-3 flex-wrap">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="w-3 h-3 rounded-full shrink-0" :style="{ backgroundColor: project.color }"></span>
                      <div class="text-base font-semibold text-[var(--text-primary)]">{{ project.name }}</div>
                      <span
                        v-if="project.system"
                        class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]"
                      >
                        Inbox
                      </span>
                    </div>
                    <div class="text-xs text-[var(--text-tertiary)] mt-2">
                      {{ getProjectSessionCount(project.id) }} session{{ getProjectSessionCount(project.id) === 1 ? '' : 's' }} mapped
                    </div>
                  </div>

                  <div class="flex items-center gap-2 flex-wrap">
                    <button
                      type="button"
                      class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-sm text-[var(--text-primary)] hover:bg-[var(--glass-surface)]"
                      @click="setActiveProject(project.id)"
                    >
                      {{ activeProjectId === project.id ? 'Active' : 'Select' }}
                    </button>
                    <button
                      v-if="!project.system && editingProjectId !== project.id"
                      type="button"
                      class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-sm text-[var(--text-primary)] hover:bg-[var(--glass-surface)]"
                      @click="startProjectRename(project.id, project.name)"
                    >
                      Rename
                    </button>
                    <button
                      v-if="!project.system"
                      type="button"
                      class="px-3 py-2 rounded-[12px] border border-rose-300/60 text-sm text-rose-700 hover:bg-rose-50"
                      @click="removeProject(project.id)"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                <div v-if="editingProjectId === project.id" class="flex flex-col sm:flex-row gap-2 mt-4">
                  <input
                    v-model="projectRenameDraft"
                    type="text"
                    class="h-11 flex-1 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
                    @keydown.enter.prevent="saveProjectRename"
                  />
                  <button
                    type="button"
                    class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-sm font-medium text-[var(--text-onblack)] hover:opacity-90"
                    @click="saveProjectRename"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface)]"
                    @click="cancelProjectRename"
                  >
                    Cancel
                  </button>
                </div>

                <div class="flex flex-wrap gap-2 mt-4">
                  <span
                    v-if="project.default_provider_id"
                    class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]"
                  >
                    Provider: {{ getProviderLabel(project.default_provider_id) }}
                  </span>
                  <span
                    v-if="project.default_model_name"
                    class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]"
                  >
                    Model: {{ project.default_model_name }}
                  </span>
                  <span
                    v-if="project.preferred_search_provider"
                    class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]"
                  >
                    Search: {{ project.preferred_search_provider }}
                  </span>
                  <span
                    v-if="project.browser_cdp_url"
                    class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]"
                  >
                    Remote browser attached
                  </span>
                  <span
                    v-if="project.browser_cookies?.length"
                    class="px-2.5 py-1 rounded-full text-[11px] border border-[var(--glass-border-strong)] text-[var(--text-secondary)]"
                  >
                    Cookies: {{ project.browser_cookies.length }}
                  </span>
                </div>
              </article>
            </div>
          </article>

          <article class="ek-glass-card rounded-[24px] p-5">
            <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
              Active Project
            </div>
            <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
              {{ activeProject.name }}
            </div>
            <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
              Session inventory and runtime defaults for the selected project.
            </div>

            <div class="grid grid-cols-2 gap-3 mt-4">
              <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
                <div class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Sessions</div>
                <div class="text-[24px] font-semibold text-[var(--text-primary)] mt-2">{{ activeProjectSessions.length }}</div>
              </article>
              <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4">
                <div class="text-xs uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Running</div>
                <div class="text-[24px] font-semibold text-[var(--text-primary)] mt-2">{{ runningProjectSessions }}</div>
              </article>
            </div>

            <div class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4 mt-4">
              <div class="text-sm font-semibold text-[var(--text-primary)]">Recent Sessions</div>
              <div class="flex flex-col gap-3 mt-4">
                <div
                  v-for="session in activeProjectSessions"
                  :key="session.session_id"
                  class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <div class="text-sm font-medium text-[var(--text-primary)] truncate">
                        {{ session.title || session.latest_message || 'Untitled session' }}
                      </div>
                      <div class="text-xs text-[var(--text-tertiary)] mt-1">
                        {{ session.status }}<span v-if="session.latest_message_at"> · {{ formatRelativeSessionTime(session.latest_message_at) }}</span>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <button
                        type="button"
                        class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-xs font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
                        @click="router.push(`/chat/${session.session_id}`)"
                      >
                        Open
                      </button>
                      <button
                        type="button"
                        class="px-3 py-2 rounded-[12px] border border-rose-300/60 text-xs font-medium text-rose-700 hover:bg-rose-50"
                        @click="removeSession(session.session_id)"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
                <div
                  v-if="activeProjectSessions.length === 0"
                  class="rounded-[16px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)]"
                >
                  No sessions mapped to this project yet.
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section v-else-if="activeTab === 'agents'" class="flex flex-col gap-4">
        <div class="ek-glass-card rounded-[24px] p-2">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tab in agentTabs"
              :key="tab.id"
              type="button"
              class="px-4 py-2.5 rounded-[16px] text-sm font-medium transition-colors"
              :class="agentTab === tab.id
                ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
                : 'text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]'"
              @click="agentTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <ModelsSettings v-if="agentTab === 'models'" :control-plane-config="controlPlaneConfig" />
        <SkillsSettings v-else-if="agentTab === 'skills'" />
        <article v-else class="ek-glass-card rounded-[24px] p-5 flex flex-col gap-4">
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
                Project Memory
              </div>
              <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
                {{ activeProject.name }}
              </div>
              <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
                Durable context injected into future sessions for the selected project.
              </div>
            </div>
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
              :disabled="memorySaving || memoryLoading"
              @click="saveAgentMemory"
            >
              {{ memorySaving ? 'Saving...' : memoryLoading ? 'Loading...' : 'Save Memory' }}
            </button>
          </div>

          <textarea
            v-model="agentMemoryContent"
            rows="10"
            class="w-full rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[220px]"
            placeholder="Critical facts, project constraints, stakeholders, or preferences that should persist across future sessions."
            :disabled="memoryLoading"
          />
          <div class="text-xs text-[var(--text-tertiary)]">
            {{ memoryLoading ? 'Loading project memory...' : `Editing memory for ${activeProject.name}.` }}
          </div>
        </article>
      </section>

      <section v-else-if="activeTab === 'channels'" class="flex flex-col gap-4">
        <div class="ek-glass-card rounded-[24px] p-2">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tab in channelTabs"
              :key="tab.id"
              type="button"
              class="px-4 py-2.5 rounded-[16px] text-sm font-medium transition-colors"
              :class="channelTab === tab.id
                ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
                : 'text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]'"
              @click="channelTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <template v-if="channelTab === 'overview'">
          <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
            <article
              v-for="channel in visibleChannels"
              :key="channel.id"
              class="ek-glass-card rounded-[24px] p-5 flex flex-col gap-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
                    {{ channel.category }}
                  </div>
                  <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
                    {{ channel.label }}
                  </div>
                </div>
                <span
                  class="px-2.5 py-1 rounded-full text-[11px] border"
                  :class="channel.stateClass"
                >
                  {{ channel.stateLabel }}
                </span>
              </div>
              <div class="text-sm text-[var(--text-secondary)] leading-6">
                {{ channel.description }}
              </div>
              <div class="text-xs text-[var(--text-tertiary)] leading-5">
                {{ channel.detail }}
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-sm font-medium text-[var(--text-onblack)] hover:opacity-90"
                  @click="channel.primaryAction()"
                >
                  {{ channel.primaryLabel }}
                </button>
                <button
                  v-if="channel.secondaryLabel"
                  type="button"
                  class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
                  @click="channel.secondaryAction?.()"
                >
                  {{ channel.secondaryLabel }}
                </button>
              </div>
            </article>
          </div>
        </template>

        <article v-else class="ek-glass-card rounded-[24px] p-5 flex flex-col gap-4">
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
                Channel Surface
              </div>
              <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
                {{ activeChannel?.label }}
              </div>
            </div>
            <span
              class="px-2.5 py-1 rounded-full text-[11px] border"
              :class="activeChannel?.stateClass"
            >
              {{ activeChannel?.stateLabel }}
            </span>
          </div>
          <div class="text-sm text-[var(--text-secondary)] leading-6">
            {{ activeChannel?.description }}
          </div>
          <div class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4 text-sm text-[var(--text-secondary)] leading-6">
            {{ activeChannel?.detail }}
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-sm font-medium text-[var(--text-onblack)] hover:opacity-90"
              @click="activeChannel?.primaryAction()"
            >
              {{ activeChannel?.primaryLabel }}
            </button>
            <button
              v-if="activeChannel?.secondaryLabel"
              type="button"
              class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]"
              @click="activeChannel?.secondaryAction?.()"
            >
              {{ activeChannel?.secondaryLabel }}
            </button>
          </div>
        </article>
      </section>

      <section v-else-if="activeTab === 'connectors'" class="flex flex-col gap-4">
        <div class="ek-glass-card rounded-[24px] p-2">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tab in connectorTabs"
              :key="tab.id"
              type="button"
              class="px-4 py-2.5 rounded-[16px] text-sm font-medium transition-colors"
              :class="connectorTab === tab.id
                ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
                : 'text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]'"
              @click="connectorTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <SearchSettings v-if="connectorTab === 'search'" :control-plane-config="controlPlaneConfig" />
        <IntegrationsSettings v-else :control-plane-config="controlPlaneConfig" :dialog-open="true" />
      </section>

      <section v-else-if="activeTab === 'browser'" class="flex flex-col gap-4">
        <BrowserSettings :control-plane-config="controlPlaneConfig" />
      </section>

      <section v-else class="flex flex-col gap-4">
        <div class="ek-glass-card rounded-[24px] p-2">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tab in settingsTabs"
              :key="tab.id"
              type="button"
              class="px-4 py-2.5 rounded-[16px] text-sm font-medium transition-colors"
              :class="settingsTab === tab.id
                ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)]'
                : 'text-[var(--text-primary)] hover:bg-[var(--glass-surface-soft)]'"
              @click="settingsTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <ProfileSettings v-if="settingsTab === 'profile'" />
        <GeneralSettings v-else-if="settingsTab === 'general'" />
        <PrivacySettings v-else :dialog-open="true" />
      </section>
    </div>
  </SimpleBar>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { PanelLeft } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'

import BrowserSettings from '@/components/settings/BrowserSettings.vue'
import GeneralSettings from '@/components/settings/GeneralSettings.vue'
import IntegrationsSettings from '@/components/settings/IntegrationsSettings.vue'
import ModelsSettings from '@/components/settings/ModelsSettings.vue'
import PrivacySettings from '@/components/settings/PrivacySettings.vue'
import ProfileSettings from '@/components/settings/ProfileSettings.vue'
import SearchSettings from '@/components/settings/SearchSettings.vue'
import SkillsSettings from '@/components/settings/SkillsSettings.vue'
import SimpleBar from '@/components/SimpleBar.vue'
import { deleteSession, getSessions } from '@/api/agent'
import { getMemory, updateMemory } from '@/api/capabilities'
import { getCachedControlPlaneConfig, type ControlPlaneConfigResponse } from '@/api/config'
import { getMcpConnectors, type MCPConnectorStatus } from '@/api/mcp'
import { type ProviderResponse, getProviders } from '@/api/providers'
import { useProjects } from '@/composables/useProjects'
import { useLeftPanel } from '@/composables/useLeftPanel'
import type { ListSessionItem } from '@/types/response'
import { showErrorToast, showSuccessToast } from '@/utils/toast'

type TopTab = 'projects' | 'agents' | 'channels' | 'connectors' | 'browser' | 'settings'
type AgentTab = 'models' | 'skills' | 'memory'
type ConnectorTab = 'search' | 'integrations'
type SettingsTab = 'profile' | 'general' | 'privacy'
type ChannelTab = 'overview' | 'slack' | 'whatsapp' | 'lark'

const router = useRouter()
const route = useRoute()
const { isLeftPanelShow, toggleLeftPanel } = useLeftPanel()

const topTabs: Array<{ id: TopTab; label: string }> = [
  { id: 'projects', label: 'Projects' },
  { id: 'agents', label: 'Agents' },
  { id: 'channels', label: 'Channels' },
  { id: 'connectors', label: 'Connectors' },
  { id: 'browser', label: 'Browser' },
  { id: 'settings', label: 'Settings' },
]

const agentTabs: Array<{ id: AgentTab; label: string }> = [
  { id: 'models', label: 'Models' },
  { id: 'skills', label: 'Skills' },
  { id: 'memory', label: 'Memory' },
]

const connectorTabs: Array<{ id: ConnectorTab; label: string }> = [
  { id: 'search', label: 'Search' },
  { id: 'integrations', label: 'Integrations' },
]

const settingsTabs: Array<{ id: SettingsTab; label: string }> = [
  { id: 'profile', label: 'Profile' },
  { id: 'general', label: 'General' },
  { id: 'privacy', label: 'Privacy' },
]

const channelTabs: Array<{ id: ChannelTab; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'slack', label: 'Slack' },
  { id: 'whatsapp', label: 'WhatsApp' },
  { id: 'lark', label: 'Lark' },
]

const {
  projects,
  activeProjectId,
  getProjectById,
  getProjectIdForSession,
  hydrateProjects,
  setActiveProject,
  createProjectRemote,
  renameProjectRemote,
  deleteProjectRemote,
  removeSessionFromProjects,
} = useProjects()

const sessions = ref<ListSessionItem[]>([])
const controlPlaneConfig = ref<ControlPlaneConfigResponse | null>(null)
const providers = ref<ProviderResponse[]>([])
const connectorCatalog = ref<MCPConnectorStatus[]>([])

const agentTab = ref<AgentTab>('models')
const connectorTab = ref<ConnectorTab>('integrations')
const settingsTab = ref<SettingsTab>('profile')
const channelTab = ref<ChannelTab>('overview')

const newProjectName = ref('')
const projectActionLoading = ref(false)
const editingProjectId = ref<string | null>(null)
const projectRenameDraft = ref('')

const agentMemoryContent = ref('')
const memoryLoading = ref(false)
const memorySaving = ref(false)

const isValidTopTab = (value: unknown): value is TopTab => topTabs.some((tab) => tab.id === value)

const activeTab = computed<TopTab>(() => {
  const queryTab = route.query.tab
  return isValidTopTab(queryTab) ? queryTab : 'projects'
})

const activeProject = computed(() => getProjectById(activeProjectId.value))

const activeProjectSessions = computed(() =>
  [...sessions.value]
    .filter((session) => getProjectIdForSession(session.session_id) === activeProjectId.value)
    .sort((left, right) => (right.latest_message_at || 0) - (left.latest_message_at || 0)),
)

const runningProjectSessions = computed(
  () => activeProjectSessions.value.filter((session) => session.status === 'running').length,
)

const configuredSurfaceCount = computed(() => {
  const enabledProviders = providers.value.filter((provider) => provider.enabled).length
  const configuredConnectors = connectorCatalog.value.filter((connector) => connector.configured).length
  const browserConfigured = projects.value.filter((project) => !!project.browser_cdp_url).length
  return enabledProviders + configuredConnectors + browserConfigured
})

const slackConnector = computed(() =>
  connectorCatalog.value.find((connector) => connector.connector_id === 'slack') || null,
)

const visibleChannels = computed(() => {
  const slackConfigured = !!slackConnector.value?.configured
  const slackInstalled = !!slackConnector.value?.installed

  return [
    {
      id: 'slack',
      label: 'Slack',
      category: 'Connector-backed',
      stateLabel: slackConfigured ? 'Configured' : slackInstalled ? 'Needs setup' : 'Available',
      stateClass: slackConfigured
        ? 'border-emerald-400/50 text-emerald-700'
        : 'border-[var(--glass-border-strong)] text-[var(--text-secondary)]',
      description: 'Use the curated Slack connector to wire Ekachi into shared workspace context and downstream workflows.',
      detail: slackConfigured
        ? 'Slack is configured through the MCP connector catalog and can already participate in runtime workflows.'
        : 'Slack is available as an official connector template and can be configured without editing raw MCP JSON.',
      primaryLabel: 'Open Integrations',
      primaryAction: () => {
        setTopTab('connectors')
        connectorTab.value = 'integrations'
      },
      secondaryLabel: 'Open Automation',
      secondaryAction: () => router.push('/chat/automation'),
    },
    {
      id: 'whatsapp',
      label: 'WhatsApp',
      category: 'Webhook bridge',
      stateLabel: 'Webhook-ready',
      stateClass: 'border-sky-400/50 text-sky-700',
      description: 'Use inbound webhooks and project-scoped automations today while a higher-level catalog entry is added.',
      detail: 'Ekachi already supports authenticated webhook triggers, execution logs, retries, and cancellation. That makes WhatsApp-style inbound bridge flows operational now, even before a dedicated connector template exists.',
      primaryLabel: 'Open Automation',
      primaryAction: () => router.push('/chat/automation'),
      secondaryLabel: 'Open Connectors',
      secondaryAction: () => setTopTab('connectors'),
    },
    {
      id: 'lark',
      label: 'Lark',
      category: 'Webhook bridge',
      stateLabel: 'Webhook-ready',
      stateClass: 'border-sky-400/50 text-sky-700',
      description: 'Route Lark events through webhook automations today, then layer dedicated connector setup once credentials are standardized.',
      detail: 'This already outperforms Eigent’s placeholder channels surface by exposing a live operational path through webhook execution and retryable run control.',
      primaryLabel: 'Open Automation',
      primaryAction: () => router.push('/chat/automation'),
      secondaryLabel: 'Open Browser',
      secondaryAction: () => setTopTab('browser'),
    },
  ]
})

const activeChannel = computed(() => visibleChannels.value.find((channel) => channel.id === channelTab.value) || null)

const setTopTab = (tab: TopTab) => {
  router.replace({
    query: {
      ...route.query,
      tab,
    },
  })
}

const getProjectSessionCount = (projectId: string) =>
  sessions.value.filter((session) => getProjectIdForSession(session.session_id) === projectId).length

const getProviderLabel = (providerId: string) =>
  providers.value.find((provider) => provider.provider_id === providerId)?.label || providerId

const loadSessions = async () => {
  sessions.value = (await getSessions()).sessions
}

const loadWorkspaceData = async () => {
  try {
    await Promise.all([
      hydrateProjects(true),
      loadSessions(),
      loadControlPlaneConfig(),
      loadProviders(),
      loadConnectorCatalog(),
    ])
  } catch (error) {
    console.error('Failed to load control center:', error)
    showErrorToast('Failed to load control center data')
  }
}

const loadControlPlaneConfig = async () => {
  controlPlaneConfig.value = await getCachedControlPlaneConfig()
}

const loadProviders = async () => {
  providers.value = (await getProviders()).providers
}

const loadConnectorCatalog = async () => {
  connectorCatalog.value = await getMcpConnectors()
}

const loadAgentMemory = async () => {
  memoryLoading.value = true
  try {
    const memory = await getMemory(activeProject.value.system ? null : activeProject.value.id)
    agentMemoryContent.value = memory.content || ''
  } catch (error) {
    console.error('Failed to load project memory:', error)
    showErrorToast('Failed to load project memory')
  } finally {
    memoryLoading.value = false
  }
}

const saveAgentMemory = async () => {
  memorySaving.value = true
  try {
    await updateMemory(activeProject.value.system ? null : activeProject.value.id, agentMemoryContent.value)
    showSuccessToast('Project memory saved')
  } catch (error) {
    console.error('Failed to save project memory:', error)
    showErrorToast('Failed to save project memory')
  } finally {
    memorySaving.value = false
  }
}

const handleCreateProject = async () => {
  if (!newProjectName.value.trim()) return
  projectActionLoading.value = true
  try {
    const created = await createProjectRemote(newProjectName.value)
    if (created) {
      newProjectName.value = ''
      showSuccessToast('Project created')
      await loadSessions()
    }
  } catch (error) {
    console.error('Failed to create project:', error)
    showErrorToast('Failed to create project')
  } finally {
    projectActionLoading.value = false
  }
}

const startProjectRename = (projectId: string, currentName: string) => {
  editingProjectId.value = projectId
  projectRenameDraft.value = currentName
}

const cancelProjectRename = () => {
  editingProjectId.value = null
  projectRenameDraft.value = ''
}

const saveProjectRename = async () => {
  if (!editingProjectId.value || !projectRenameDraft.value.trim()) return
  try {
    await renameProjectRemote(editingProjectId.value, projectRenameDraft.value)
    showSuccessToast('Project renamed')
    cancelProjectRename()
  } catch (error) {
    console.error('Failed to rename project:', error)
    showErrorToast('Failed to rename project')
  }
}

const removeProject = async (projectId: string) => {
  if (!window.confirm('Delete this project? Sessions will move back to Inbox.')) return
  try {
    await deleteProjectRemote(projectId)
    showSuccessToast('Project deleted')
    await loadSessions()
  } catch (error) {
    console.error('Failed to delete project:', error)
    showErrorToast('Failed to delete project')
  }
}

const removeSession = async (sessionId: string) => {
  if (!window.confirm('Delete this session?')) return
  try {
    await deleteSession(sessionId)
    sessions.value = sessions.value.filter((session) => session.session_id !== sessionId)
    removeSessionFromProjects(sessionId)
    showSuccessToast('Session deleted')
  } catch (error) {
    console.error('Failed to delete session:', error)
    showErrorToast('Failed to delete session')
  }
}

const refreshActiveTab = async () => {
  if (activeTab.value === 'agents' && agentTab.value === 'memory') {
    await loadAgentMemory()
    return
  }
  await loadWorkspaceData()
}

const formatRelativeSessionTime = (timestamp: number) => {
  const deltaSeconds = Math.max(0, Math.floor(Date.now() / 1000) - timestamp)
  if (deltaSeconds < 60) return 'just now'
  if (deltaSeconds < 3600) return `${Math.floor(deltaSeconds / 60)}m ago`
  if (deltaSeconds < 86400) return `${Math.floor(deltaSeconds / 3600)}h ago`
  return `${Math.floor(deltaSeconds / 86400)}d ago`
}

watch(activeProjectId, () => {
  if (agentTab.value === 'memory') {
    void loadAgentMemory()
  }
})

watch(
  () => activeTab.value,
  (tab) => {
    if (tab === 'agents' && agentTab.value === 'memory') {
      void loadAgentMemory()
    }
    if (tab === 'channels') {
      void loadConnectorCatalog()
    }
  },
  { immediate: true },
)

watch(agentTab, (tab) => {
  if (tab === 'memory') {
    void loadAgentMemory()
  }
}, { immediate: true })

onMounted(async () => {
  await loadWorkspaceData()
})
</script>
