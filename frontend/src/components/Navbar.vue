<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../store.js'
import { api } from '../api.js'

const router = useRouter()
const role = computed(() => store.user ? store.user.role : null)

async function logout() {
    await api.logout()
    store.clear()
    router.push('/login')
}
</script>

<template>
  <nav class="navbar navbar-expand-lg bg-white shadow-sm mb-4" v-if="role">
    <div class="container">
      <router-link
        class="navbar-brand fw-bold text-success"
        :to="role === 'Admin' ? '/admin/dashboard' : role === 'Trek Staff' ? '/staff/dashboard' : '/trekker/dashboard'"
      >
        <i class="bi bi-geo-alt-fill"></i> RidgeLine
      </router-link>

      <div class="d-flex flex-wrap align-items-center gap-1 ms-auto">
        <template v-if="role === 'Admin'">
          <router-link to="/admin/dashboard" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-grid"></i> Dashboard</router-link>
          <router-link to="/admin/treks" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-signpost-split"></i> Treks</router-link>
          <router-link to="/admin/staff" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-person-badge"></i> Staff</router-link>
          <router-link to="/admin/users" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-people"></i> Trekkers</router-link>
          <router-link to="/admin/bookings" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-journal-check"></i> Bookings</router-link>
        </template>
        <template v-else-if="role === 'Trek Staff'">
          <router-link to="/staff/dashboard" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-grid"></i> Dashboard</router-link>
          <router-link to="/staff/participants" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-people"></i> Participants</router-link>
          <router-link to="/staff/profile" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-person-circle"></i> Profile</router-link>
        </template>
        <template v-else-if="role === 'Trekker'">
          <router-link to="/trekker/dashboard" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-grid"></i> Dashboard</router-link>
          <router-link to="/trekker/treks" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-signpost-split"></i> Browse Treks</router-link>
          <router-link to="/trekker/bookings" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-journal-check"></i> My Bookings</router-link>
          <router-link to="/trekker/profile" class="nav-link px-3" active-class="active fw-semibold text-success"><i class="bi bi-person-circle"></i> Profile</router-link>
        </template>
        <span class="nav-link px-3 text-danger" role="button" @click="logout"><i class="bi bi-box-arrow-right"></i> Logout</span>
      </div>
    </div>
  </nav>
</template>