<template>
    <div class="pointer-events-auto cursor-default">
        <div class="min-w-max inline-block transition-[transform,opacity,scale] duration-150" tabindex="-1"
            role="dialog">
            <div
                class="profile-menu-surface flex w-[min(320px,calc(100vw-24px))] flex-col rounded-[20px] border-[0.5px] border-[var(--glass-border-strong)]">
                <div class="flex gap-2 px-4 pt-5 pb-3 w-full">
                    <div class="relative flex items-center justify-center font-bold cursor-pointer flex-shrink-0">
                        <div class="relative flex items-center justify-center font-bold flex-shrink-0 rounded-full overflow-hidden"
                            style="width: 48px; height: 48px; font-size: 24px; color: rgba(255, 255, 255, 0.9); background-color: rgb(59, 130, 246);">
                            {{ avatarLetter }}</div>
                    </div>
                    <div class="flex overflow-hidden flex-col justify-center">
                        <div class="flex gap-1 items-center w-full"><span
                                class="text-[var(--text-primary)] text-base font-semibold leading-[22px] truncate">{{
                                    currentUser?.fullname || t('Unknown User') }}</span></div><span
                            class="text-[var(--text-tertiary)] text-[13px] font-normal leading-[18px] truncate">{{
                                currentUser?.email || t('No email') }}</span>
                    </div>
                </div>
                <div class="flex flex-col gap-3 px-3 pb-3">
                    <div class="flex flex-col gap-1">
                        <div class="w-full h-[1px] my-1 bg-[var(--border-main)]"></div>
                        <div
                            class="flex gap-3 items-center p-2 rounded-lg cursor-pointer text-[var(--text-primary)] hover:bg-[var(--fill-tsp-white-main)]"
                            @click="handleAccountClick">
                            <div class="flex-shrink-0 w-5 h-5">
                                <User :size="20" />
                            </div>
                            <span
                                class="overflow-hidden flex-1 text-sm font-medium leading-5 whitespace-nowrap text-ellipsis">{{
                                t('Account') }}</span>
                        </div>
                        <div
                            class="flex gap-3 items-center p-2 rounded-lg cursor-pointer text-[var(--text-primary)] hover:bg-[var(--fill-tsp-white-main)]"
                            @click="handleSettingsClick">
                            <div class="flex-shrink-0 w-5 h-5">
                                <Settings2 :size="20" />
                            </div>
                            <span
                                class="overflow-hidden flex-1 text-sm font-medium leading-5 whitespace-nowrap text-ellipsis">{{
                                t('Settings') }}</span>
                        </div>
                        <div
                            class="flex gap-3 items-center p-2 rounded-lg cursor-pointer text-[var(--text-primary)] hover:bg-[var(--fill-tsp-white-main)]"
                            @click="handleModelsClick">
                            <div class="flex-shrink-0 w-5 h-5">
                                <Workflow :size="20" />
                            </div>
                            <span
                                class="overflow-hidden flex-1 text-sm font-medium leading-5 whitespace-nowrap text-ellipsis">Models</span>
                        </div>
                        <div
                            class="flex gap-3 items-center p-2 rounded-lg cursor-pointer text-[var(--text-primary)] hover:bg-[var(--fill-tsp-white-main)]"
                            @click="handleControlCenterClick">
                            <div class="flex-shrink-0 w-5 h-5">
                                <LayoutGrid :size="20" />
                            </div>
                            <span
                                class="overflow-hidden flex-1 text-sm font-medium leading-5 whitespace-nowrap text-ellipsis">Control Center</span>
                        </div>
                        <div
                            class="flex gap-3 items-center p-2 rounded-lg cursor-pointer text-[var(--text-primary)] hover:bg-[var(--fill-tsp-white-main)]"
                            @click="handleIntegrationsClick">
                            <div class="flex-shrink-0 w-5 h-5">
                                <Blocks :size="20" />
                            </div>
                            <span
                                class="overflow-hidden flex-1 text-sm font-medium leading-5 whitespace-nowrap text-ellipsis">Integrations</span>
                        </div>
                        <div class="w-full h-[1px] my-1 bg-[var(--border-main)]"></div>
                        <div v-if="authProvider !== 'none'"
                            class="flex gap-3 items-center p-2 rounded-lg cursor-pointer hover:bg-[var(--fill-tsp-white-main)] text-[var(--function-error)]"
                            @click="handleLogout">
                            <div class="flex-shrink-0 w-5 h-5">
                                <LogOut :size="20" />
                            </div>
                            <span
                                class="overflow-hidden flex-1 text-sm font-medium leading-5 whitespace-nowrap text-ellipsis">{{
                                t('Logout') }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuth } from '../composables/useAuth';
import { useSettingsDialog } from '../composables/useSettingsDialog';
import { getCachedAuthProvider } from '../api/config';
import { Blocks, LayoutGrid, LogOut, Settings2, User, Workflow } from 'lucide-vue-next';

const router = useRouter();
const { t } = useI18n();
const { currentUser, logout } = useAuth();
const { openSettingsDialog } = useSettingsDialog();
const authProvider = ref<string | null>(null);

// Get first letter of user's fullname for avatar display
const avatarLetter = computed(() => {
    return currentUser.value?.fullname?.charAt(0)?.toUpperCase() || 'M';
});

// Handle Account click - open settings dialog with account tab
const handleAccountClick = () => {
    openSettingsDialog('account');
};

// Handle Settings click - open settings dialog with settings tab
const handleSettingsClick = () => {
    openSettingsDialog('settings');
};

const handleModelsClick = () => {
    openSettingsDialog('models');
};

const handleControlCenterClick = () => {
    router.push('/chat/control');
};

const handleIntegrationsClick = () => {
    openSettingsDialog('integrations');
};

// Handle logout action
const handleLogout = async () => {
    try {
        await logout();
        router.push('/login');
    } catch (error) {
        console.error('Logout failed:', error);
    }
};

onMounted(async () => {
    authProvider.value = await getCachedAuthProvider();
});
</script>

<style scoped>
.profile-menu-surface {
    background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.88)),
        var(--glass-surface-strong);
    box-shadow:
        0 20px 40px rgba(15, 23, 42, 0.12),
        var(--glass-shadow-soft);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

:global(.dark) .profile-menu-surface {
    background:
        linear-gradient(180deg, rgba(20, 24, 31, 0.94), rgba(20, 24, 31, 0.9)),
        var(--glass-surface-strong);
}
</style>
