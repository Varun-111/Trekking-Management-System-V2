<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import Pagination from '../../components/Pagination.vue'
import { api } from '../../api.js'

const bookings = ref([])
const page = ref(1)
const totalPages = ref(1)
const q = ref('')

async function load() {
    const r = await api.staffParticipants({ q: q.value, page: page.value })
    bookings.value = r.bookings
    totalPages.value = r.total_pages
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
      <h2 class="mb-4">Participants (across my treks)</h2>

      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <form @submit.prevent="search" class="row g-2 align-items-end">
            <div class="col-auto flex-grow-1">
              <label class="form-label">Search by name</label>
              <input v-model="q" class="form-control">
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
                <tr><th>Name</th><th>Trek</th><th>Booked On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td>{{ b.user_name }}</td>
                  <td>{{ b.trek_name }}</td>
                  <td>{{ b.booked_on }}</td>
                  <td><span :class="badgeClass(b.status)">{{ b.status }}</span></td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="4" class="text-center text-muted py-4">No participants yet</td>
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