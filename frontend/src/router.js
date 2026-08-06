import { createRouter, createWebHistory } from 'vue-router'
import { store } from './store.js'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('./views/Login.vue'), meta: { guest: true } },
    { path: '/register', component: () => import('./views/Register.vue'), meta: { guest: true } },

    { path: '/admin/dashboard', component: () => import('./views/admin/Dashboard.vue'), meta: { role: 'Admin' } },
    { path: '/admin/treks', component: () => import('./views/admin/Treks.vue'), meta: { role: 'Admin' } },
    { path: '/admin/staff', component: () => import('./views/admin/Staff.vue'), meta: { role: 'Admin' } },
    { path: '/admin/users', component: () => import('./views/admin/Users.vue'), meta: { role: 'Admin' } },
    { path: '/admin/bookings', component: () => import('./views/admin/Bookings.vue'), meta: { role: 'Admin' } },

    { path: '/staff/dashboard', component: () => import('./views/staff/Dashboard.vue'), meta: { role: 'Trek Staff' } },
    { path: '/staff/trek/:id', component: () => import('./views/staff/Trek.vue'), meta: { role: 'Trek Staff' } },
    { path: '/staff/participants', component: () => import('./views/staff/Participants.vue'), meta: { role: 'Trek Staff' } },
    { path: '/staff/profile', component: () => import('./views/staff/Profile.vue'), meta: { role: 'Trek Staff' } },

    { path: '/trekker/dashboard', component: () => import('./views/trekker/Dashboard.vue'), meta: { role: 'Trekker' } },
    { path: '/trekker/treks', component: () => import('./views/trekker/Treks.vue'), meta: { role: 'Trekker' } },
    { path: '/trekker/treks/:id', component: () => import('./views/trekker/TrekDetail.vue'), meta: { role: 'Trekker' } },
    { path: '/trekker/bookings', component: () => import('./views/trekker/Bookings.vue'), meta: { role: 'Trekker' } },
    { path: '/trekker/profile', component: () => import('./views/trekker/Profile.vue'), meta: { role: 'Trekker' } },

    { path: '/:pathMatch(.*)*', component: () => import('./views/NotFound.vue') },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

const roleHome = (role) =>
    role === 'Admin' ? '/admin/dashboard' : role === 'Trek Staff' ? '/staff/dashboard' : '/trekker/dashboard'

router.beforeEach((to) => {
    const role = store.isLoggedIn ? store.user.role : null

    if (to.meta.guest && role) return roleHome(role)
    if (to.meta.role && !role) return '/login'
    if (to.meta.role && role !== to.meta.role) return roleHome(role)
    return true
})

export default router
