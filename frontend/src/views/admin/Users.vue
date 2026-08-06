<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import Pagination from '../../components/Pagination.vue'
import { api } from '../../api.js'

const users = ref([])
const page = ref(1)
const totalPages = ref(1)
const q = ref('')

async function load() {
    const r = await api.adminUsers({ q: q.value, page: page.value })
    users.value = r.users
    totalPages.value = r.total_pages
}

async function block(id) { await api.adminBlock(id); await load() }
async function unblock(id) { await api.adminUnblock(id); await load() }
function goPage(p) { page.value = p; load() }
function search() { page.value = 1; load() }

onMounted(load)
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4">
      <h2 class="mb-4">Trekkers</h2>

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
                <tr><th>Name</th><th>Email</th><th>Phone</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-if="!users.length">
                  <td colspan="5" class="text-center text-muted py-4">No trekkers yet</td>
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