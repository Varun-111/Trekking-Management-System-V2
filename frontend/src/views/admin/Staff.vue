<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'

const tab = ref('active')
const active = ref([])
const blocked = ref([])
const showForm = ref(false)
const form = ref({ name: '', email: '', phone: '', password: '' })
const error = ref('')
const q = ref('')

async function load() {
    const r = await api.adminStaffList({ q: q.value })
    active.value = r.active
    blocked.value = r.blocked
}

async function addStaff() {
    error.value = ''
    const f = form.value
    if (!f.name.trim() || !f.email.trim() || !f.phone.trim() || !f.password) {
        alert('Please fill all fields.')
        return
    }
    if (!/^[0-9]{10}$/.test(f.phone.trim())) {
        alert('Phone number must be exactly 10 digits.')
        return
    }
    if (f.password.length < 6) {
        alert('Password must be at least 6 characters.')
        return
    }
    try {
        await api.adminAddStaff(form.value)
        form.value = { name: '', email: '', phone: '', password: '' }
        showForm.value = false
        await load()
    } catch (e) { error.value = e.message; alert(e.message) }
}

async function remove(id) { if (confirm('Remove this staff member? Their treks will be unassigned.')) { await api.adminRemoveStaff(id); await load() } }
async function block(id) { await api.adminBlock(id); await load() }
async function unblock(id) { await api.adminUnblock(id); await load() }

onMounted(load)
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
        <h2 class="mb-0">Trek Staff</h2>
        <button class="btn btn-success" @click="showForm = !showForm"><i class="bi bi-plus-lg me-1"></i> Add Staff</button>
      </div>
      <p class="small text-muted mb-3">Staff accounts can only be created here by the Admin - there is no staff sign-up form, so every account added is active immediately.</p>

      <div class="card shadow-sm mb-3" v-if="showForm">
        <div class="card-body">
          <h3 class="h5">Add Staff</h3>
          <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
          <form @submit.prevent="addStaff">
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Name</label>
                <input v-model="form.name" class="form-control" required>
              </div>
              <div class="col-md-6">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-control" required>
              </div>
            </div>
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" inputmode="numeric" maxlength="10" pattern="[0-9]{10}" placeholder="10-digit mobile number" required>
              </div>
              <div class="col-md-6">
                <label class="form-label">Password</label>
                <input v-model="form.password" type="password" class="form-control" minlength="6" placeholder="At least 6 characters" required>
              </div>
            </div>
            <button type="submit" class="btn btn-success me-2">Create</button>
            <button type="button" class="btn btn-outline-secondary" @click="showForm = false">Cancel</button>
          </form>
        </div>
      </div>

      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <form @submit.prevent="load" class="row g-2 align-items-end">
            <div class="col-auto flex-grow-1">
              <label class="form-label">Search</label>
              <input v-model="q" class="form-control" placeholder="Name or email">
            </div>
            <div class="col-auto">
              <button type="submit" class="btn btn-outline-success">
                <i class="bi bi-search me-1"></i> Search
              </button>
            </div>
          </form>
        </div>
      </div>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'active' }" role="button" @click="tab = 'active'">Active ({{ active.length }})</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'blocked' }" role="button" @click="tab = 'blocked'">Blocked ({{ blocked.length }})</a>
        </li>
      </ul>

      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive" v-if="tab === 'active'">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Phone</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="s in active" :key="s.id">
                  <td>{{ s.name }}</td>
                  <td>{{ s.email }}</td>
                  <td>{{ s.phone }}</td>
                  <td>
                    <button class="btn btn-sm btn-danger me-1" @click="block(s.id)">Block</button>
                    <button class="btn btn-sm btn-outline-secondary" @click="remove(s.id)">Remove</button>
                  </td>
                </tr>
                <tr v-if="!active.length">
                  <td colspan="4" class="text-center text-muted py-4">No active staff</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-responsive" v-if="tab === 'blocked'">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Phone</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="s in blocked" :key="s.id">
                  <td>{{ s.name }}</td>
                  <td>{{ s.email }}</td>
                  <td>{{ s.phone }}</td>
                  <td><button class="btn btn-sm btn-outline-success" @click="unblock(s.id)">Unblock</button></td>
                </tr>
                <tr v-if="!blocked.length">
                  <td colspan="4" class="text-center text-muted py-4">No blocked staff</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>