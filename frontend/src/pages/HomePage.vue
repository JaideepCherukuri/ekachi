<template>
  <SimpleBar>
    <div
      class="flex flex-col h-full flex-1 min-w-0 mx-auto w-full sm:min-w-[390px] px-3 sm:px-5 justify-center items-start gap-2 relative max-w-full sm:max-w-full">
      <div class="ek-sticky-glass w-full pt-4 pb-4 px-3 sm:px-5 sticky top-0 z-10 mx-[-0.75rem] sm:mx-[-1.25rem]">
        <div class="flex justify-between items-center w-full absolute left-0 right-0">
          <div class="h-8 relative z-20 overflow-hidden flex gap-2 items-center flex-shrink-0">
            <div class="relative flex items-center">
              <div @click="toggleLeftPanel" v-if="!isLeftPanelShow"
                class="flex h-7 w-7 items-center justify-center cursor-pointer rounded-md hover:bg-[var(--fill-tsp-gray-main)]">
                <PanelLeft class="size-5 text-[var(--icon-secondary)]" />
              </div>
            </div>
            <div class="flex">
              <Bot :size="30" />
              <ManusLogoTextIcon />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <a v-if="showGithubButton"
               :href="githubRepositoryUrl"
               target="_blank"
               rel="noopener noreferrer"
               class="items-center justify-center whitespace-nowrap font-medium transition-colors hover:opacity-90 active:opacity-80 px-[12px] gap-[6px] text-sm min-w-16 outline outline-1 -outline-offset-1 hover:bg-[var(--fill-tsp-white-light)] text-[var(--text-primary)] outline-[var(--border-btn-main)] bg-transparent clickable hidden sm:flex rounded-[100px] relative h-[32px] group"
               title="Visit GitHub Repository">
              <Github class="size-[18px]" />
              GitHub
            </a>
            <div class="relative flex items-center" aria-expanded="false" aria-haspopup="dialog"
              @mouseenter="handleUserMenuEnter" @mouseleave="handleUserMenuLeave">
              <div class="relative flex items-center justify-center font-bold cursor-pointer flex-shrink-0">
                <div
                  class="relative flex items-center justify-center font-bold flex-shrink-0 rounded-full overflow-hidden"
                  style="width: 32px; height: 32px; font-size: 16px; color: rgba(255, 255, 255, 0.9); background-color: rgb(59, 130, 246);">
                  {{ avatarLetter }}</div>
              </div>
              <!-- User Menu -->
              <div v-if="showUserMenu" @mouseenter="handleUserMenuEnter" @mouseleave="handleUserMenuLeave"
                class="absolute top-full right-0 mt-1 mr-[-15px] z-50">
                <UserMenu />
              </div>
            </div>
          </div>
        </div>
        <div class="h-8"></div>
      </div>
      <div class="w-full max-w-full sm:max-w-[768px] sm:min-w-[390px] mx-auto mt-24 sm:mt-[180px] mb-auto">
        <div class="w-full flex pl-4 items-center justify-start pb-6">
          <div class="flex flex-col gap-3">
            <div class="inline-flex items-center gap-2 self-start px-3 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface-soft)] text-xs text-[var(--text-secondary)]">
              <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: activeProject.color }"></span>
              <span>Project</span>
              <span class="font-medium text-[var(--text-primary)]">{{ activeProject.name }}</span>
            </div>
            <span class="text-[var(--text-primary)] text-start font-serif text-[32px] leading-[40px]" :style="{
              fontFamily:
                'ui-serif, Georgia, Cambria, &quot;Times New Roman&quot;, Times, serif',
            }">
              {{ $t('Hello') }}, {{ currentUser?.fullname }}
              <br />
              <span class="text-[var(--text-tertiary)]">
                {{ $t('What can I do for you?') }}
              </span>
            </span>
          </div>
        </div>
        <div class="flex flex-col gap-1 w-full">
          <div
            v-if="projects.length > 1"
            class="ek-glass-card flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 rounded-[20px] px-3 py-3 mb-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-medium text-[var(--text-primary)]">Project</div>
              <div class="text-xs text-[var(--text-tertiary)]">New sessions will be created inside the selected project.</div>
            </div>
            <Select v-model="selectedProjectId">
              <SelectTrigger class="w-full sm:w-[280px] h-[38px]">
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent :side-offset="5">
                <SelectItem
                  v-for="project in projects"
                  :key="project.id"
                  :value="project.id"
                >
                  {{ project.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div
            v-if="providers.length > 1"
            class="ek-glass-card flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 rounded-[20px] px-3 py-3 mb-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-medium text-[var(--text-primary)]">Provider</div>
              <div class="text-xs text-[var(--text-tertiary)]">Choose the runtime profile for this new task.</div>
            </div>
            <Select v-model="selectedProviderId">
              <SelectTrigger class="w-full sm:w-[280px] h-[38px]">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent :side-offset="5">
                <SelectItem
                  v-for="provider in providers"
                  :key="provider.provider_id"
                  :value="provider.provider_id"
                >
                  {{ provider.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div
            v-if="availableModels.length > 0"
            class="ek-glass-card flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 rounded-[20px] px-3 py-3 mb-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-medium text-[var(--text-primary)]">{{ t('Model') }}</div>
              <div class="text-xs text-[var(--text-tertiary)]">{{ t('Choose the model for this new task') }}</div>
            </div>
            <Select v-model="selectedModel">
              <SelectTrigger class="w-full sm:w-[280px] h-[38px]">
                <SelectValue :placeholder="t('Select model')" />
              </SelectTrigger>
              <SelectContent :side-offset="5">
                <SelectItem
                  v-for="model in availableModels"
                  :key="model"
                  :value="model"
                >
                  {{ model }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="ek-glass-panel flex flex-col w-full rounded-[28px] p-1 sm:p-2">
            <div class="[&amp;:not(:empty)]:pb-2 rounded-[22px_22px_0px_0px]">
            </div>
            <ChatBox :rows="2" v-model="message" @submit="handleSubmit" :isRunning="false" :attachments="attachments" />
          </div>
        </div>
      </div>
    </div>
  </SimpleBar>
</template>

<script setup lang="ts">
import SimpleBar from '../components/SimpleBar.vue';
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import ChatBox from '../components/ChatBox.vue';
import { createSession } from '../api/agent';
import { getProviders, type ProviderResponse } from '@/api/providers';
import { showErrorToast } from '../utils/toast';
import { Bot, PanelLeft, Github } from 'lucide-vue-next';
import ManusLogoTextIcon from '../components/icons/ManusLogoTextIcon.vue';
import type { FileInfo } from '../api/file';
import { useLeftPanel } from '../composables/useLeftPanel';
import { useFilePanel } from '../composables/useFilePanel';
import { useAuth } from '../composables/useAuth';
import { getCachedClientConfig } from '../api/config';
import UserMenu from '../components/UserMenu.vue';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useProjects } from '@/composables/useProjects';

const { t } = useI18n();
const router = useRouter();
const message = ref('');
const isSubmitting = ref(false);
const attachments = ref<FileInfo[]>([]);
const { toggleLeftPanel, isLeftPanelShow } = useLeftPanel();
const { hideFilePanel } = useFilePanel();
const { currentUser } = useAuth();
const showGithubButton = ref(false);
const githubRepositoryUrl = ref('https://github.com/JaideepCherukuri/ekachi');
const providers = ref<ProviderResponse[]>([]);
const selectedModel = ref('');
const selectedProviderId = ref('system');
const { projects, activeProjectId, assignSessionToProject, getProjectById, setActiveProject, hydrateProjects, syncSession } = useProjects();
const selectedProjectId = ref(activeProjectId.value);
const selectedProvider = computed(() => providers.value.find((provider) => provider.provider_id === selectedProviderId.value) || null)
const availableModels = computed(() => selectedProvider.value?.available_models || [])

// Get first letter of user's fullname for avatar display
const avatarLetter = computed(() => {
  return currentUser.value?.fullname?.charAt(0)?.toUpperCase() || 'E';
});

const activeProject = computed(() => getProjectById(selectedProjectId.value));

// User menu state
const showUserMenu = ref(false);
const userMenuTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

// Show user menu on hover
const handleUserMenuEnter = () => {
  if (userMenuTimeout.value) {
    clearTimeout(userMenuTimeout.value);
    userMenuTimeout.value = null;
  }
  showUserMenu.value = true;
};

// Hide user menu with delay
const handleUserMenuLeave = () => {
  userMenuTimeout.value = setTimeout(() => {
    showUserMenu.value = false;
  }, 200); // 200ms delay to allow moving to menu
};

onMounted(() => {
  hideFilePanel();
})

onMounted(async () => {
  try {
    await hydrateProjects()
  } catch (error) {
    console.error('Failed to hydrate projects:', error)
  }
  const clientConfig = await getCachedClientConfig();
  if (clientConfig) {
    showGithubButton.value = clientConfig.show_github_button;
    githubRepositoryUrl.value = clientConfig.github_repository_url;
  }
  const providerResponse = await getProviders()
  providers.value = providerResponse.providers.filter((provider) => provider.enabled || provider.is_system)
  const systemProvider = providers.value.find((provider) => provider.is_system)
  selectedProviderId.value = systemProvider?.provider_id || providers.value[0]?.provider_id || 'system'
  selectedModel.value = systemProvider?.default_model_name || providers.value[0]?.default_model_name || ''
});

watch(selectedProjectId, (projectId) => {
  setActiveProject(projectId);
});

watch(activeProjectId, (projectId) => {
  selectedProjectId.value = projectId
})

watch(activeProject, (project) => {
  if (!project) return
  if (project.default_provider_id) {
    selectedProviderId.value = project.default_provider_id
  }
  const provider = providers.value.find((item) => item.provider_id === selectedProviderId.value) || selectedProvider.value
  if (project.default_model_name) {
    selectedModel.value = project.default_model_name
  } else if (provider) {
    selectedModel.value = provider.default_model_name
  }
}, { immediate: true })

watch(selectedProviderId, (providerId) => {
  if (!providerId) return
  const provider = providers.value.find((item) => item.provider_id === providerId)
  if (!provider) return
  if (!provider.available_models.includes(selectedModel.value)) {
    selectedModel.value = provider.default_model_name
  }
})

const handleSubmit = async () => {
  if (message.value.trim() && !isSubmitting.value) {
    isSubmitting.value = true;

    try {
      // Create new Agent
      const session = await createSession(
        selectedModel.value || undefined,
        {
          project_id: activeProject.value.id,
          project_name: activeProject.value.name,
          project_color: activeProject.value.color,
        },
        selectedProviderId.value || undefined,
      );
      const sessionId = session.session_id;
      syncSession(session)
      assignSessionToProject(sessionId, selectedProjectId.value);

      // Navigate to new route with session_id, passing initial message via state
      router.push({
        path: `/chat/${sessionId}`,
        state: {
          message: message.value, files: attachments.value.map((file: FileInfo) => ({
            file_id: file.file_id,
            filename: file.filename,
            content_type: file.content_type,
            size: file.size,
            upload_date: file.upload_date
          }))
        }
      });
    } catch (error) {
      console.error('Failed to create session:', error);
      showErrorToast(t('Failed to create session, please try again later'));
      isSubmitting.value = false;
    }
  }
};
</script>
