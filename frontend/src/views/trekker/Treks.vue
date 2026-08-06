<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import Pagination from '../../components/Pagination.vue'
import { api } from '../../api.js'

const treks = ref([])
const places = ref([])
const page = ref(1)
const totalPages = ref(1)
const q = ref('')
const level = ref('all')
const place = ref('all')
const date = ref('')

async function load() {
    const r = await api.trekkerTreks({ q: q.value, level: level.value, place: place.value, date: date.value, page: page.value })
    treks.value = r.treks
    places.value = r.places
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
      <h2 class="mb-4">Browse Treks</h2>

      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <form @submit.prevent="search" class="row g-2 align-items-end">
            <div class="col-md">
              <label class="form-label">Search</label>
              <input v-model="q" class="form-control" placeholder="Name or place">
            </div>
            <div class="col-md-auto">
              <label class="form-label">From Date</label>
              <input v-model="date" type="date" class="form-control">
            </div>
            <div class="col-md-auto">
              <label class="form-label">Level</label>
              <select v-model="level" class="form-select">
                <option value="all">All Levels</option>
                <option>Easy</option><option>Moderate</option><option>Hard</option>
              </select>
            </div>
            <div class="col-md-auto">
              <label class="form-label">Place</label>
              <select v-model="place" class="form-select">
                <option value="all">All Places</option>
                <option v-for="p in places" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>
            <div class="col-md-auto">
              <button type="submit" class="btn btn-success">
                <i class="bi bi-funnel me-1"></i> Filter
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
                <tr><th>Name</th><th>Place</th><th>Level</th><th>Days</th><th>Seats</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in treks" :key="t.id">
                  <td>{{ t.name }}</td>
                  <td>{{ t.place }}</td>
                  <td>{{ t.level }}</td>
                  <td>{{ t.days }}</td>
                  <td>{{ t.seats_left }} / {{ t.total_seats }}</td>
                  <td><span :class="badgeClass(t.status)">{{ t.status }}</span></td>
                  <td><router-link :to="'/trekker/treks/' + t.id" class="btn btn-sm btn-success">View</router-link></td>
                </tr>
                <tr v-if="!treks.length">
                  <td colspan="7" class="text-center text-muted py-4">No treks match your filters</td>
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