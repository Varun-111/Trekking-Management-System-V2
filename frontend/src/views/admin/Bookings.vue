<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import Pagination from '../../components/Pagination.vue'
import { api } from '../../api.js'

const bookings = ref([])
const page = ref(1)
const totalPages = ref(1)

async function load() {
    const r = await api.adminBookings({ page: page.value })
    bookings.value = r.bookings
    totalPages.value = r.total_pages
}
function goPage(p) { page.value = p; load() }

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
      <h2 class="mb-4">All Bookings</h2>
      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Trekker</th>
                  <th>Trek</th>
                  <th>Place</th>
                  <th>Booked On</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td>{{ b.user_name }}</td>
                  <td>{{ b.trek_name }}</td>
                  <td>{{ b.trek_place }}</td>
                  <td>{{ b.booked_on }}</td>
                  <td><span :class="badgeClass(b.status)">{{ b.status }}</span></td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="5" class="text-center text-muted py-4">No bookings yet</td>
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