<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import Pagination from '../../components/Pagination.vue'
import { api } from '../../api.js'

const treks = ref([])
const staffList = ref([])
const page = ref(1)
const totalPages = ref(1)
const q = ref('')
const showForm = ref(false)
const editingId = ref(null)
const error = ref('')

const emptyForm = () => ({ name: '', place: '', level: 'Easy', days: 1, seats: 10, staff_id: '', start_date: '', notes: '' })
const form = ref(emptyForm())

async function load() {
    const [t, s] = await Promise.all([
        api.adminTreks({ q: q.value, page: page.value }),
        api.adminStaffList(),
    ])
    treks.value = t.treks
    totalPages.value = t.total_pages
    staffList.value = s.active
}

function openAdd() {
    editingId.value = null
    form.value = emptyForm()
    error.value = ''
    showForm.value = true
}
function openEdit(t) {
    editingId.value = t.id
    form.value = { ...t, staff_id: t.staff_id || '', seats: t.total_seats }
    error.value = ''
    showForm.value = true
}

function todayStr() {
    const d = new Date()
    return d.toISOString().slice(0, 10)
}

async function save() {
    error.value = ''
    const f = form.value
    if (!f.name.trim() || !f.place.trim() || !f.level || !f.days || !f.seats || !f.start_date) {
        alert('Please fill all required fields.')
        return
    }
    if (f.start_date <= todayStr()) {
        alert('Trek start date must be after today.')
        return
    }
    try {
        if (editingId.value) await api.adminEditTrek(editingId.value, form.value)
        else await api.adminAddTrek(form.value)
        showForm.value = false
        await load()
    } catch (e) {
        error.value = e.message
        alert(e.message)
    }
}

async function remove(id) {
    if (!confirm('Remove this trek? Past bookings will be kept for history.')) return
    await api.adminDeleteTrek(id)
    await load()
}

function goPage(p) { page.value = p; load() }
function search() { page.value = 1; load() }

// Same status -> Bootstrap color mapping used on the other pages.
const statusColor = {
    open: 'success', completed: 'success', approved: 'success',
    upcoming: 'warning', pending: 'warning',
    closed: 'danger', cancelled: 'danger', blocked: 'danger',
    ongoing: 'info', booked: 'info',
}
function badgeClass(s) {
    const color = statusColor[(s || '').toLowerCase()] || 'secondary'
    return 'badge bg-' + color
}

onMounted(load)
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
        <h2 class="mb-0">Manage Treks</h2>
        <button class="btn btn-success" @click="openAdd"><i class="bi bi-plus-lg me-1"></i> Add Trek</button>
      </div>

      <div class="card shadow-sm mb-3" v-if="showForm">
        <div class="card-body">
          <h3 class="h5">{{ editingId ? 'Edit Trek' : 'Add New Trek' }}</h3>
          <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
          <form @submit.prevent="save">
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Trek Name</label>
                <input v-model="form.name" class="form-control" required>
              </div>
              <div class="col-md-6">
                <label class="form-label">Place</label>
                <input v-model="form.place" class="form-control" required>
              </div>
            </div>
            <div class="row g-3 mb-3">
              <div class="col-md-4">
                <label class="form-label">Level</label>
                <select v-model="form.level" class="form-select">
                  <option>Easy</option><option>Moderate</option><option>Hard</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Days</label>
                <input type="number" min="1" v-model="form.days" class="form-control" required>
              </div>
              <div class="col-md-4">
                <label class="form-label">Total Seats</label>
                <input type="number" min="0" v-model="form.seats" class="form-control" required>
              </div>
            </div>
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Assign Staff</label>
                <select v-model="form.staff_id" class="form-select">
                  <option value="">-- None --</option>
                  <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Start Date</label>
                <input type="date" v-model="form.start_date" class="form-control" :min="todayStr()" required>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea v-model="form.notes" class="form-control" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-success me-2">Save Trek</button>
            <button type="button" class="btn btn-outline-secondary" @click="showForm = false">Cancel</button>
          </form>
        </div>
      </div>

      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <form @submit.prevent="search" class="row g-2 align-items-end">
            <div class="col-auto flex-grow-1">
              <label class="form-label">Search</label>
              <input v-model="q" class="form-control" placeholder="Name or place">
            </div>
            <div class="col-auto">
              <button type="submit" class="btn btn-outline-success">
                <i class="bi bi-search me-1"></i> Search
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Name</th><th>Place</th><th>Level</th><th>Seats</th><th>Status</th><th>Staff</th><th>Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in treks" :key="t.id">
                  <td>{{ t.name }}</td>
                  <td>{{ t.place }}</td>
                  <td>{{ t.level }}</td>
                  <td>{{ t.seats_left }} / {{ t.total_seats }}</td>
                  <td><span :class="badgeClass(t.status)">{{ t.status }}</span></td>
                  <td>{{ t.staff_name || '-' }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-secondary me-1" @click="openEdit(t)"><i class="bi bi-pencil"></i></button>
                    <button class="btn btn-sm btn-danger" @click="remove(t.id)"><i class="bi bi-trash"></i></button>
                  </td>
                </tr>
                <tr v-if="!treks.length">
                  <td colspan="7" class="text-center text-muted py-4">No treks found</td>
                </tr>
              </tbody>
            </table>
          </div>
          <Pagination :page="page" :total-pages="totalPages" @change="goPage" />
        </div>
      </div>
    </div>
  </div>
</template>