<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'
import { store } from '../../store.js'

const treks = ref([])
async function load() {
    const r = await api.staffDashboard()
    treks.value = r.treks
}

// Same status -> Bootstrap color mapping used on the admin pages.
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
            <i class="bi bi-compass text-success fs-5"></i>
          </div>
          <div>
            <h2 class="h4 mb-0">Welcome back, <span class="text-success">{{ store.user?.username }}</span></h2>
            <p class="text-muted mb-0">Here are the treks assigned to you.</p>
          </div>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Name</th><th>Place</th><th>Seats</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in treks" :key="t.id">
                  <td>{{ t.name }}</td>
                  <td>{{ t.place }}</td>
                  <td>{{ t.seats_left }} / {{ t.total_seats }}</td>
                  <td><span :class="badgeClass(t.status)">{{ t.status }}</span></td>
                  <td><router-link :to="'/staff/trek/' + t.id" class="btn btn-sm btn-success">Manage</router-link></td>
                </tr>
                <tr v-if="!treks.length">
                  <td colspan="5" class="text-center text-muted py-4">No treks assigned yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>