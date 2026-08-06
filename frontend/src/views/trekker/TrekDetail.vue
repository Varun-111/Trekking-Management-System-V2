<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'

const route = useRoute()
const router = useRouter()
const trek = ref(null)
const alreadyBooked = ref(false)
const error = ref('')

async function load() {
    const r = await api.trekkerTrekDetail(route.params.id)
    trek.value = r.trek
    alreadyBooked.value = r.already_booked
}

async function book() {
    error.value = ''
    try {
        await api.trekkerBookTrek(route.params.id)
        router.push('/trekker/bookings')
    } catch (e) { error.value = e.message }
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
      <router-link to="/trekker/treks" class="small text-muted text-decoration-none">
        <i class="bi bi-arrow-left"></i> Back to Treks
      </router-link>

      <div class="card shadow-sm mt-3" style="max-width: 620px;">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h2 class="h4 mb-0">{{ trek.name }}</h2>
            <span :class="badgeClass(trek.status)">{{ trek.status }}</span>
          </div>

          <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
          <div class="alert alert-success py-2" v-if="alreadyBooked">You've already booked this trek.</div>

          <p><i class="bi bi-geo-alt"></i> <b>Place:</b> {{ trek.place }}</p>
          <p><i class="bi bi-bar-chart"></i> <b>Level:</b> {{ trek.level }}</p>
          <p><i class="bi bi-calendar-range"></i> <b>Duration:</b> {{ trek.days }} day(s)</p>
          <p><i class="bi bi-calendar-check"></i> <b>Dates:</b> {{ trek.start_date }} to {{ trek.end_date }}</p>
          <p><i class="bi bi-ticket-perforated"></i> <b>Seats Left:</b> {{ trek.seats_left }} / {{ trek.total_seats }}</p>
          <p v-if="trek.notes"><b>Notes:</b> {{ trek.notes }}</p>

          <button class="btn btn-success" @click="book" :disabled="alreadyBooked || trek.status !== 'Open' || trek.seats_left <= 0">
            <i class="bi bi-check-circle me-1"></i> Book This Trek
          </button>
        </div>
      </div>
    </div>
  </div>
</template>