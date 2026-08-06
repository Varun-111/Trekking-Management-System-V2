<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'
import { store } from '../../store.js'

const counts = ref(null)
const latest = ref([])
const pendingTreks = ref([])

async function load() {
    const d = await api.adminDashboard()
    counts.value = d.counts
    latest.value = d.latest
    pendingTreks.value = d.pending_treks
}

onMounted(load)

// Same status -> Bootstrap color mapping used on the Bookings page.
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
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4" v-if="counts">

      <div class="card shadow-sm mb-4">
        <div class="card-body d-flex align-items-center gap-3">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 flex-shrink-0"
               style="width: 46px; height: 46px;">
            <i class="bi bi-shield-check text-success fs-5"></i>
          </div>
          <div>
            <h2 class="h4 mb-0">Welcome back, <span class="text-success">{{ store.user?.username }}</span></h2>
            <p class="text-muted mb-0">Here's what's happening across RidgeLine today.</p>
          </div>
        </div>
      </div>

      <div class="row row-cols-1 row-cols-md-4 g-3 mb-4">
        <div class="col">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <i class="bi bi-signpost-split text-success"></i>
              <div class="fs-2 fw-bold">{{ counts.treks }}</div>
              <div class="text-muted small">Active Treks</div>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <i class="bi bi-people text-success"></i>
              <div class="fs-2 fw-bold">{{ counts.members }}</div>
              <div class="text-muted small">Trekkers</div>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <i class="bi bi-person-badge text-success"></i>
              <div class="fs-2 fw-bold">{{ counts.staff }}</div>
              <div class="text-muted small">Trek Staff</div>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <i class="bi bi-journal-check text-success"></i>
              <div class="fs-2 fw-bold">{{ counts.active_bookings }}</div>
              <div class="text-muted small">Active Bookings</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card shadow-sm mb-4" v-if="pendingTreks.length">
        <div class="card-body">
          <h3 class="h5">Treks Awaiting Staff Assignment</h3>
          <p class="small text-muted">These treks are Pending until a Trek Staff member is assigned to them.</p>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Trek</th><th>Place</th><th>Start Date</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in pendingTreks" :key="t.id">
                  <td>{{ t.name }}</td>
                  <td>{{ t.place }}</td>
                  <td>{{ t.start_date }}</td>
                  <td><span :class="badgeClass(t.status)">{{ t.status }}</span></td>
                  <td><router-link :to="'/admin/treks'" class="btn btn-sm btn-success">Assign Staff</router-link></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="h5">Recent Bookings</h3>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Trekker</th><th>Trek</th><th>Booked On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in latest" :key="b.id">
                  <td>{{ b.user_name }}</td>
                  <td>{{ b.trek_name }}</td>
                  <td>{{ b.booked_on }}</td>
                  <td><span :class="badgeClass(b.status)">{{ b.status }}</span></td>
                </tr>
                <tr v-if="!latest.length">
                  <td colspan="4" class="text-center text-muted py-4">No bookings yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>