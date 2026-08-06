<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'

const route = useRoute()
const trek = ref(null)
const bookings = ref([])
const seatsLeft = ref(0)
const wantedStatus = ref('')
const message = ref('')

async function load() {
    const r = await api.staffTrek(route.params.id)
    trek.value = r.trek
    bookings.value = r.bookings
    seatsLeft.value = r.trek.seats_left
    wantedStatus.value = r.trek.status
}

async function update() {
    message.value = ''
    if (seatsLeft.value === '' || seatsLeft.value === null || seatsLeft.value < 0 || seatsLeft.value > trek.value.total_seats) {
        alert(`Seats left must be between 0 and ${trek.value.total_seats}.`)
        return
    }
    const r = await api.staffUpdateTrek(route.params.id, { seats_left: seatsLeft.value, status: wantedStatus.value })
    message.value = r.message
    await load()
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
watch(() => route.params.id, load)
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4" v-if="trek">
      <router-link to="/staff/dashboard" class="small text-muted text-decoration-none">
        <i class="bi bi-arrow-left"></i> Back to Dashboard
      </router-link>
      <h2 class="mt-3 mb-4">{{ trek.name }}</h2>

      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <p><i class="bi bi-geo-alt"></i> <b>Place:</b> {{ trek.place }}</p>
              <p><i class="bi bi-bar-chart"></i> <b>Level:</b> {{ trek.level }}</p>
              <p><i class="bi bi-calendar-range"></i> <b>Duration:</b> {{ trek.days }} day(s)</p>
              <p><i class="bi bi-calendar-check"></i> <b>Dates:</b> {{ trek.start_date }} to {{ trek.end_date }}</p>
              <p v-if="trek.notes" class="mb-0"><b>Notes:</b> {{ trek.notes }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <div class="alert alert-success py-2" v-if="message">{{ message }}</div>

              <div class="mb-3">
                <label class="form-label">Seats Left (of {{ trek.total_seats }})</label>
                <input type="number" min="0" :max="trek.total_seats" v-model="seatsLeft" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Status</label>
                <select v-model="wantedStatus" class="form-select">
                  <option v-if="trek.status === 'Approved'" value="Approved">Approved</option>
                  <option>Open</option><option>Closed</option><option>Completed</option>
                </select>
              </div>
              <button class="btn btn-success" @click="update">Update Status</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="h5">Participants</h3>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Booked On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td>{{ b.user_name }}</td>
                  <td>{{ b.user_email }}</td>
                  <td>{{ b.booked_on }}</td>
                  <td><span :class="badgeClass(b.status)">{{ b.status }}</span></td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="4" class="text-center text-muted py-4">No participants yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>