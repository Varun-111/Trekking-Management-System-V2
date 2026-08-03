import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router.js'
import { store } from './store.js'
import { api } from './api.js'

async function bootstrap() {
    try {
        const { user } = await api.me()
        if (user) store.setUser(user)
    } catch (e) {
        // not logged in - router guards will redirect to /login
    }

    const app = createApp(App)
    app.use(router)
    app.mount('#app')
}

bootstrap()
