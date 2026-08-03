<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'
import { store } from '../store.js'

const router = useRouter()
const email = ref('')
const password = ref('')
const role = ref('Trekker')
const error = ref('')

// roles use guideline-correct naming end-to-end now (Admin / Trek Staff / Trekker)
const roles = [
    { value: 'Trekker', label: 'Trekker' },
    { value: 'Trek Staff', label: 'Trek Staff' },
    { value: 'Admin', label: 'Admin' },
]

async function submit() {
    error.value = ''
    try {
        const { user } = await api.login({ email: email.value, password: password.value, role: role.value })
        store.setUser(user)
        if (user.role === 'Admin') router.push('/admin/dashboard')
        else if (user.role === 'Trek Staff') router.push('/staff/dashboard')
        else router.push('/trekker/dashboard')
    } catch (e) {
        error.value = e.message
    }
}
</script>

<template>
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <div class="card shadow-sm" style="max-width: 420px; width: 100%;">
      <div class="card-body p-4">

        <div class="text-center mb-3">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-circle mb-2"
               style="width: 60px; height: 60px;">
            <i class="bi bi-geo-alt-fill text-success fs-4"></i>
          </div>
          <h3 class="mb-0">RidgeLine</h3>
          <p class="text-muted small mb-0">Sign in to continue</p>
        </div>

        <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>

        <div class="mb-3">
          <label class="form-label">Login as</label>
          <select v-model="role" class="form-select">
            <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
        </div>

        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" placeholder="you@example.com" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" placeholder="********" required>
          </div>
          <button type="submit" class="btn btn-success w-100">
            <i class="bi bi-box-arrow-in-right me-1"></i> Login
          </button>
        </form>

        <p class="text-center small text-muted mt-3 mb-0">
          New here? <router-link to="/register">Register</router-link>
        </p>

      </div>
    </div>
  </div>
</template>