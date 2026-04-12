<template>
  <Dialog v-model:open="isSettingsDialogOpen">
    <DialogContent class="w-[95vw] max-w-[1100px] ek-glass-panel border-[var(--glass-border)]">
      <DialogTitle></DialogTitle>
      <DialogDescription></DialogDescription>
      
      <SettingsTabs 
        :tabs="tabs" 
        :default-tab="defaultTab"
        :current-sub-page="currentSubPage"
        :sub-page-configs="subPageConfigs"
        @tab-change="onTabChange"
        @navigate-to-profile="navigateToProfile"
        @back="goBack">
        
        <template #account>
          <AccountSettings @navigate-to-profile="navigateToProfile" />
        </template>
        
        <template #account-profile>
          <ProfileSettings @back="goBack" />
        </template>
        
        <template #settings>
          <GeneralSettings />
        </template>

        <template #models>
          <ModelsSettings :control-plane-config="controlPlaneConfig" />
        </template>

        <template #search>
          <SearchSettings :control-plane-config="controlPlaneConfig" />
        </template>

        <template #browser>
          <BrowserSettings :control-plane-config="controlPlaneConfig" />
        </template>

        <template #privacy>
          <PrivacySettings :dialog-open="isSettingsDialogOpen" />
        </template>

        <template #integrations>
          <IntegrationsSettings :control-plane-config="controlPlaneConfig" :dialog-open="isSettingsDialogOpen" />
        </template>

        <template #skills>
          <SkillsSettings />
        </template>
        
      </SettingsTabs>
      
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Blocks, Brain, Monitor, Search, Settings2, ShieldCheck, UserRound, Workflow } from 'lucide-vue-next'
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { useSettingsDialog } from '@/composables/useSettingsDialog'
import { getCachedControlPlaneConfig, type ControlPlaneConfigResponse } from '@/api/config'
import SettingsTabs from './SettingsTabs.vue'
import AccountSettings from './AccountSettings.vue'
import BrowserSettings from './BrowserSettings.vue'
import GeneralSettings from './GeneralSettings.vue'
import IntegrationsSettings from './IntegrationsSettings.vue'
import ModelsSettings from './ModelsSettings.vue'
import PrivacySettings from './PrivacySettings.vue'
import ProfileSettings from './ProfileSettings.vue'
import SearchSettings from './SearchSettings.vue'
import SkillsSettings from './SkillsSettings.vue'
import type { TabItem, SubPageConfig } from './SettingsTabs.vue'

// Use global settings dialog state
const { isSettingsDialogOpen, defaultTab } = useSettingsDialog()

// Navigation state for sub-pages
const currentSubPage = ref<string | null>(null)
const controlPlaneConfig = ref<ControlPlaneConfigResponse | null>(null)

// Tab configuration
const tabs: TabItem[] = [
  {
    id: 'account',
    label: 'Account',
    icon: UserRound
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings2
  },
  {
    id: 'models',
    label: 'Models',
    icon: Workflow
  },
  {
    id: 'search',
    label: 'Search',
    icon: Search
  },
  {
    id: 'browser',
    label: 'Browser',
    icon: Monitor
  },
  {
    id: 'privacy',
    label: 'Privacy',
    icon: ShieldCheck
  },
  {
    id: 'integrations',
    label: 'Integrations',
    icon: Blocks
  },
  {
    id: 'skills',
    label: 'Workforce',
    icon: Brain
  }
]

// Sub-page configuration
const subPageConfigs: SubPageConfig[] = [
  {
    id: 'profile',
    title: 'Profile',
    parentTabId: 'account'
  }
]

// Handle tab change
const onTabChange = (tabId: string) => {
  console.log('Tab changed to:', tabId)
  // Reset sub-page when changing tabs
  currentSubPage.value = null
}

// Navigate to profile sub-page
const navigateToProfile = () => {
  currentSubPage.value = 'profile'
}

// Go back to main view
const goBack = () => {
  currentSubPage.value = null
}

watch(isSettingsDialogOpen, async (isOpen) => {
  if (isOpen) {
    currentSubPage.value = null
    controlPlaneConfig.value = await getCachedControlPlaneConfig()
  }
}, { immediate: true })
</script>
