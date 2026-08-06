<script setup>
import { ref, onMounted } from 'vue'
import { computed } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { store } from '../../store.js'
import { api } from '../../api.js'

const treks = ref([])
const bookings = ref([])
const username = computed(() => store.user ? store.user.username : '')

async function load() {
    const r = await api.trekkerDashboard()
    treks.value = r.treks
    bookings.value = r.bookings
}

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

      <div class="card shadow-sm mb-4">
        <div class="card-body d-flex align-items-center gap-3">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 flex-shrink-0"
               style="width: 46px; height: 46px;">
            <i class="bi bi-backpack2 text-success fs-5"></i>
          </div>
          <div>
            <h2 class="h4 mb-0">Welcome back, <span class="text-success">{{ username }}</span></h2>
            <p class="text-muted mb-0">Ready for your next trek?</p>
          </div>
        </div>
      </div>

      <h3 class="h5 mb-3">Open Treks</h3>
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Name</th><th>Place</th><th>Level</th><th>Seats Left</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in treks" :key="t.id">
                  <td>{{ t.name }}</td>
                  <td>{{ t.place }}</td>
                  <td>{{ t.level }}</td>
                  <td>{{ t.seats_left }}</td>
                  <td><router-link :to="'/trekker/treks/' + t.id" class="btn btn-sm btn-success">View</router-link></td>
                </tr>
                <tr v-if="!treks.length">
                  <td colspan="5" class="text-center text-muted py-4">No open treks right now</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <h3 class="h5 mb-3">My Active Bookings</h3>
      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Trek</th><th>Booked On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td>{{ b.trek_name }}</td>
                  <td>{{ b.booked_on }}</td>
                  <td><span :class="badgeClass(b.status)">{{ b.status }}</span></td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="3" class="text-center text-muted py-4">No active bookings</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>