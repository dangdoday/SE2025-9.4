import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import App from './App.vue'
import router from './router'
import './styles/main.css'

// PrimeVue components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import Dropdown from 'primevue/dropdown'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import ProgressBar from 'primevue/progressbar'
import Tag from 'primevue/tag'
import Tooltip from 'primevue/tooltip'

const app = createApp(App)

// Pinia store
app.use(createPinia())

// Vue Router
app.use(router)

// PrimeVue with dark theme
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark-mode',
      cssLayer: false
    }
  }
})
app.use(ToastService)

// Register PrimeVue components globally
app.component('Button', Button)
app.component('InputText', InputText)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Card', Card)
app.component('Dialog', Dialog)
app.component('Toast', Toast)
app.component('Dropdown', Dropdown)
app.component('TabView', TabView)
app.component('TabPanel', TabPanel)
app.component('ProgressBar', ProgressBar)
app.component('Tag', Tag)

// Directives
app.directive('tooltip', Tooltip)

app.mount('#app')
