<script setup lang="ts">
import Favico from 'favico.js';

import { useRoute } from 'vue-router';
import Menu from 'primevue/menu';
import type { MenuItem } from 'primevue/menuitem';
import { breakpointsTailwind } from '@vueuse/core';

const botStore = useBotStore();

const settingsStore = useSettingsStore();
const layoutStore = useLayoutStore();
const route = useRoute();
const router = useRouter();
const favicon = ref<Favico | undefined>(undefined);
const pingInterval = ref<number>();

const breakpoints = useBreakpoints(breakpointsTailwind);

const isMobile = breakpoints.smallerOrEqual('md');

async function clickLogout() {
  botStore.removeBot(botStore.selectedBot);
  // TODO: This should be per bot
  await router.push('/');
}

const setOpenTradesAsPill = (tradeCount: number) => {
  if (!favicon.value) {
    favicon.value = new Favico({
      animation: 'none',
      // position: 'up',
      // fontStyle: 'normal',
      // bgColor: '#',
      // textColor: '#FFFFFF',
    });
  }
  if (tradeCount !== 0 && settingsStore.openTradesInTitle === 'showPill') {
    favicon.value.badge(tradeCount);
  } else {
    favicon.value.reset();
    console.log('reset');
  }
};
const resetDynamicLayout = (): void => {
  console.log(`resetLayout called for ${route?.fullPath}`);
  switch (route?.fullPath) {
    case '/trade':
      layoutStore.resetTradingLayout();
      break;
    case '/dashboard':
      layoutStore.resetDashboardLayout();
      break;
    default:
  }
};
const setTitle = () => {
  let title = 'freqUI';
  if (settingsStore.openTradesInTitle === OpenTradeVizOptions.asTitle) {
    title = `(${botStore.activeBotorUndefined?.openTradeCount}) ${title}`;
  }
  if (botStore.activeBotorUndefined?.botName) {
    title = `${title} - ${botStore.activeBotorUndefined?.botName}`;
  }
  document.title = title;
};

onBeforeUnmount(() => {
  if (pingInterval.value) {
    clearInterval(pingInterval.value);
  }
});

onMounted(async () => {
  await settingsStore.loadUIVersion();
  pingInterval.value = window.setInterval(botStore.pingAll, 60000);
});

settingsStore.$subscribe((_, state) => {
  const needsUpdate = settingsStore.openTradesInTitle !== state.openTradesInTitle;
  if (needsUpdate) {
    setTitle();
    setOpenTradesAsPill(botStore.activeBotorUndefined?.openTradeCount || 0);
  }
});

watch(
  () => botStore.activeBotorUndefined?.botName,
  () => setTitle(),
);
watch(
  () => botStore.activeBotorUndefined?.openTradeCount,
  () => {
    if (settingsStore.openTradesInTitle === OpenTradeVizOptions.showPill) {
      setOpenTradesAsPill(botStore.activeBotorUndefined?.openTradeCount ?? 0);
    } else if (settingsStore.openTradesInTitle === OpenTradeVizOptions.asTitle) {
      setTitle();
    }
  },
);

// Navigation items array
const navItems = ref([
  {
    label: 'Trade',
    to: '/trade',
    visible: computed(() => !botStore.canRunBacktest),
    icon: 'i-mdi-currency-usd',
  },
  {
    label: 'Dashboard',
    to: '/dashboard',
    visible: computed(() => !botStore.canRunBacktest),
    icon: 'i-mdi-view-dashboard',
  },
  {
    label: 'Chart',
    to: '/graph',
    icon: 'i-mdi-chart-line',
  },
  {
    label: 'Logs',
    to: '/logs',
    icon: 'i-mdi-format-list-bulleted',
  },
  {
    label: 'Settings',
    to: '/settings',
    mobileOnly: true,
    icon: 'i-mdi-cog',
  },
  {
    label: 'API Keys',
    to: '/api_settings',
    icon: 'i-mdi-key',
  },
  {
    label: 'Backtest',
    to: '/backtest',
    visible: computed(() => botStore.canRunBacktest),
    icon: 'i-mdi-currency-usd',
  },
  {
    label: 'Hyperopt',
    to: '/hyperopt',
    visible: computed(() => botStore.canRunBacktest),
    icon: 'i-mdi-tune-variant',
  },
  {
    label: 'Download Data',
    to: '/download_data',
    visible: computed(
      () => botStore.isWebserverMode && botStore.activeBot.botFeatures.downloadDataView,
    ),
    icon: 'i-mdi-download',
  },
  {
    label: 'Pairlist Config',
    to: '/pairlist_config',
    icon: 'i-mdi-format-list-numbered-rtl',
    visible: computed(
      () =>
        (botStore.activeBot?.isWebserverMode ?? false) &&
        botStore.activeBot.botFeatures.pairlistConfig,
    ),
  },
]);

const menuItems = computed<MenuItem[]>(() => [
  {
    label: `V: ${settingsStore.uiVersion}`,
    disabled: true,
  },
  {
    label: 'Settings',
    icon: 'i-mdi-cog',
    command: () => router.push('/settings'),
  },
  {
    label: 'Lock dynamic Layout',
    checkbox: true,
    checked: layoutStore.layoutLocked,
    command: () => {
      layoutStore.layoutLocked = !layoutStore.layoutLocked;
    },
  },
  {
    label: 'Reset Layout',
    icon: 'i-mdi-lock-reset',
    command: resetDynamicLayout,
  },
  {
    label: 'Logout',
    icon: 'i-mdi-logout',
    command: clickLogout,
    visible: botStore.hasBots && botStore.botCount === 1,
  },
]);
const menu = ref<InstanceType<typeof Menu> | null>();
function toggleMenu(event) {
  menu.value?.toggle(event);
}
const drawerVisible = ref(false);
</script>

<template>
  <header>
    <div class="flex bg-gray-900 dark:bg-gray-950 border-b border-primary-500">
      <RouterLink class="ms-2 flex flex-row items-center pe-2 gap-2" exact to="/">
        <div class="h-[30px] w-[30px] flex items-center justify-center rounded-lg bg-primary-500 text-black">
          <svg fill="none" viewBox="0 0 48 48" class="w-6 h-6" xmlns="http://www.w3.org/2000/svg">
            <path clip-rule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" fill="currentColor" fill-rule="evenodd"></path>
          </svg>
        </div>
        <span class="text-white text-xl md:hidden lg:inline text-nowrap font-bold tracking-tight">BinanceBot</span>
      </RouterLink>
      <div class="flex justify-between w-full text-center items-center ms-3">
        <div class="items-center hidden md:flex gap-5 ms-5">
          <RouterLink
            v-for="(item, index) in navItems.filter(
              (item) => (item.visible ?? true) && !item.mobileOnly,
            )"
            :key="index"
            :to="item.to"
            class="text-gray-300 hover:text-primary-500 flex items-center gap-2 transition-colors font-medium"
            active-class="text-primary-500 font-bold"
          >
            {{ item.label }}
          </RouterLink>
          <ThemeSelect />
        </div>

        <!-- Right aligned nav items -->
        <div v-if="!isMobile" class="flex ms-auto">
          <!-- TODO This should show outside of the dropdown in XS mode -->
          <div
            v-if="!settingsStore.confirmDialog"
            class="my-auto me-5 flex text-primary-500"
            title="Confirm dialog deactivated, Forced exits will be executed immediately. Be careful."
          >
            <i-mdi-run-fast />
            <i-mdi-alert />
          </div>
          <div class="flex justify-between">
            <Select
              v-if="botStore.botCount > 1"
              :model-value="botStore.selectedBotObj"
              size="small"
              class="m-1"
              no-caret
              severity="info"
              toggle-class="flex align-items-center "
              menu-class="my-0 py-0"
              :options="botStore.availableBotsSorted"
              @update:model-value="botStore.selectBot($event.botId)"
            >
              <template #value="{ value }">
                <BotEntry :bot="value" :no-buttons="true" />
              </template>

              <template #option="{ option }">
                <BotEntry :bot="option" :no-buttons="true" />
              </template>
            </Select>
            <ReloadControl class="me-3" title="Confirm Dialog deactivated." />
          </div>
          <div
            class="hidden md:flex md:flex-wrap lg:flex-nowrap items-center nav-item text-gray-300 me-2"
          >
            <span class="text-sm me-2">
              {{
                (botStore.activeBotorUndefined && botStore.activeBotorUndefined.botName) ||
                'No bot selected'
              }}
            </span>
            <span v-if="botStore.botCount === 1">
              {{
                botStore.activeBotorUndefined && botStore.activeBotorUndefined.isBotOnline
                  ? 'Online'
                  : 'Offline'
              }}
            </span>
          </div>
          <div v-if="botStore.hasBots" class="flex items-center">
            <!-- Hide dropdown on xs, instead show below  -->
            <Button severity="contrast" variant="text" size="small" @click="toggleMenu">
              <div class="flex items-center">
                <Avatar shape="circle" severity="contrast">
                  <!-- <Avatar label="FT" shape="circle"></Avatar> -->
                  FT
                </Avatar>
                <i-mdi-chevron-down />
              </div>
            </Button>
            <Menu ref="menu" :model="menuItems" popup class="w-56">
              <template #item="{ item }">
                <div
                  class="flex flex-row items-center gap-2 p-1"
                  :class="{
                    'cursor-pointer': !item.disabled,
                  }"
                >
                  <i-mdi-cog v-if="item.icon === 'i-mdi-cog'" />
                  <i-mdi-logout v-if="item.icon === 'i-mdi-logout'" />
                  <i-mdi-lock-reset v-if="item.icon === 'i-mdi-lock-reset'" />
                  <BaseCheckbox v-if="item.checkbox" v-model="item.checked" />
                  <span>{{ item.label }}</span>
                </div>
              </template>
            </Menu>
          </div>
          <div v-else>
            <!-- should open Modal window! -->
            <LoginModal v-if="route?.path !== '/login'" />
          </div>
        </div>

        <!-- Mobile menu -->
        <div v-if="isMobile" class="ms-auto flex">
          <Button
            class="text-gray-300 text-xl"
            variant="text"
            @click="drawerVisible = !drawerVisible"
          >
            <template #icon>
              <i-mdi-menu />
            </template>
          </Button>
          <Drawer
            v-model:visible="drawerVisible"
            header="Drawer"
            position="right"
            class="bg-gray-900"
          >
            <template #container>
              <div class="flex flex-row items-center">
                <h3 class="text-xl font-bold w-full text-center text-white">BinanceBot</h3>
                <Button
                  class="float-right mt-1 me-1"
                  variant="outlined"
                  @click="drawerVisible = !drawerVisible"
                >
                  <template #icon>
                    <i-mdi-close />
                  </template>
                </Button>
              </div>
              <div class="flex flex-col gap-1 items-center mt-4">
                <RouterLink
                  v-for="(item, index) in navItems.filter((item) => item.visible ?? true)"
                  :key="index"
                  :to="item.to"
                  class="text-gray-300 hover:text-primary-500 p-2 transition-colors"
                  active-class="text-primary-500 font-bold"
                >
                  {{ item.label }}
                </RouterLink>
                <Divider />
                <span class="text-gray-300 text-center"
                  >Version: {{ settingsStore.uiVersion }}</span
                >
                <div class="text-gray-400 text-xs text-center mt-1">BinanceBot Trading System</div>

                <div class="flex flex-row items-center justify-center">
                  <ThemeSelect show-text />
                </div>
                <Select
                  v-if="botStore.botCount > 1"
                  :model-value="botStore.selectedBotObj"
                  size="small"
                  class="m-1"
                  no-caret
                  severity="info"
                  toggle-class="flex align-items-center "
                  menu-class="my-0 py-0"
                  :options="botStore.availableBotsSorted"
                  @update:model-value="botStore.selectBot($event.botId)"
                >
                  <template #value="{ value }">
                    <BotEntry :bot="value" :no-buttons="true" />
                  </template>

                  <template #option="{ option }">
                    <BotEntry :bot="option" :no-buttons="true" />
                  </template>
                </Select>
                <ReloadControl class="justify-center w-full" title="Confirm Dialog deactivated." />
              </div>
            </template>
          </Drawer>
        </div>
      </div>
    </div>
  </header>
</template>
