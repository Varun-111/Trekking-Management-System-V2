<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'

const bookings = ref([])
const exporting = ref(false)
const exportMsg = ref('')
let pollTimer = null

async function load() { bookings.value = await api.trekkerBookings() }
async function cancel(id) { await api.trekkerCancelBooking(id); await load() }

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

async function exportCsv() {
    exporting.value = true
    exportMsg.value = 'Preparing your CSV...'

    try {
        const { task_id } = await api.triggerCsvExport()
        pollStatus(task_id)
    } catch (e) {
        exporting.value = false
        exportMsg.value = e.message
    }
}

function triggerDownload(url) {
    // Programmatic <a download> click - browser saves the file straight to
    // Downloads without navigating away or opening a new tab/window.
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
}

function pollStatus(taskId) {
    const maxAttempts = 40 // ~60 seconds
    let attempts = 0

    pollTimer = setInterval(async () => {
        attempts++
        if (attempts > maxAttempts) {
            clearInterval(pollTimer); pollTimer = null
            exporting.value = false
            exportMsg.value = 'Export is taking longer than expected. Please try again shortly.'
            return
        }

        let result
        try {
            result = await api.csvExportStatus(taskId)
        } catch (e) {
            clearInterval(pollTimer); pollTimer = null
            exporting.value = false
            exportMsg.value = 'Export failed: ' + e.message
            return
        }

        if (result.state === 'SUCCESS') {
            clearInterval(pollTimer); pollTimer = null
            exporting.value = false
            exportMsg.value = 'Download starting...'
            triggerDownload(`/api/export/history/csv/download/${result.filename}`)
            setTimeout(() => { exportMsg.value = '' }, 2000)
        } else if (result.state === 'FAILURE') {
            clearInterval(pollTimer); pollTimer = null
            exporting.value = false
            exportMsg.value = 'Export failed: ' + (result.error || 'unknown error')
        } else {
            exportMsg.value = 'Processing export...'
        }
    }, 1500)
}

onMounted(load)
onBeforeUnmount(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
        <h2 class="mb-0">My Bookings</h2>
        <button class="btn btn-success" @click="exportCsv" :disabled="exporting">
          <i class="bi bi-download me-1"></i> {{ exporting ? 'Exporting...' : 'Export as CSV' }}
        </button>
      </div>
      <p class="small text-muted mb-3">Every trek you've booked, completed or cancelled shows up here.</p>

      <p class="small text-muted" v-if="exportMsg">{{ exportMsg }}</p>

      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr><th>Trek</th><th>Place</th><th>Trek Dates</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td>{{ b.trek_name }}</td>
                  <td>{{ b.trek_place }}</td>
                  <td>{{ b.trek_start_date }} - {{ b.trek_end_date }}</td>
                  <td><span :class="badgeClass(b.status)">{{ b.status }}</span></td>
                  <td>
                    <button v-if="b.status === 'Booked'" class="btn btn-sm btn-danger" @click="cancel(b.id)">Cancel</button>
                    <span v-else class="text-muted small">-</span>
                  </td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="5" class="text-center text-muted py-4">No bookings yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>