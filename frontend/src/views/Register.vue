<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'

const router = useRouter()
const username = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const success = ref('')

async function submit() {
    error.value = ''
    success.value = ''

    if (!username.value.trim() || !email.value.trim() || !phone.value.trim() || !password.value || !confirm.value) {
        alert('Please fill all fields.')
        return
    }
    if (!/^[0-9]{10}$/.test(phone.value.trim())) {
        alert('Phone number must be exactly 10 digits.')
        return
    }
    if (password.value.length < 6) {
        alert('Password must be at least 6 characters.')
        return
    }
    if (password.value !== confirm.value) {
        alert('Passwords do not match.')
        return
    }

    try {
        // Only Trekkers can self-register. Trek Staff accounts are created
        // by the Admin from the admin panel - there is no staff sign-up here.
        const { message } = await api.register({
            username: username.value, email: email.value, phone: phone.value,
            password: password.value, confirm: confirm.value,
        })
        success.value = message
        setTimeout(() => router.push('/login'), 1400)
    } catch (e) {
        error.value = e.message
        alert(e.message)
    }
}
</script>

<template>
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <div class="card shadow-sm" style="max-width: 460px; width: 100%;">
      <div class="card-body p-4">

        <div class="text-center mb-3">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-circle mb-2"
               style="width: 60px; height: 60px;">
            <i class="bi bi-person-plus text-success fs-4"></i>
          </div>
          <h3 class="mb-0">Join RidgeLine</h3>
          <p class="text-muted small mb-0">Register as a Trekker</p>
        </div>

        <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
        <div class="alert alert-success py-2" v-if="success">{{ success }}</div>

        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="username" class="form-control" required>
          </div>

          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required>
          </div>

          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input v-model="phone" class="form-control" inputmode="numeric" maxlength="10"
                   pattern="[0-9]{10}" placeholder="10-digit mobile number" required>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" minlength="6"
                     placeholder="At least 6 characters" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Confirm Password</label>
              <input v-model="confirm" type="password" class="form-control" required>
            </div>
          </div>

          <button type="submit" class="btn btn-success w-100">
            <i class="bi bi-check-circle me-1"></i> Register
          </button>
        </form>

        <p class="text-center small text-muted mt-3 mb-0">
          Already have an account? <router-link to="/login">Login</router-link>
        </p>

      </div>
    </div>
  </div>
</template>