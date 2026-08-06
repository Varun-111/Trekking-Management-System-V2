<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { store } from '../../store.js'
import { api } from '../../api.js'

const me = ref(null)
const saved = ref(false)

async function load() { me.value = await api.trekkerProfile() }
async function save() {
    if (!me.value.name.trim()) {
        alert('Name cannot be empty.')
        return
    }
    if (me.value.phone && !/^[0-9]{10}$/.test(me.value.phone.trim())) {
        alert('Phone number must be exactly 10 digits.')
        return
    }
    try {
        const updated = await api.trekkerUpdateProfile({ name: me.value.name, phone: me.value.phone })
        store.setUser(updated)
        saved.value = true
        setTimeout(() => saved.value = false, 2000)
    } catch (e) {
        alert(e.message)
    }
}
onMounted(load)
</script>

<template>
  <div>
    <Navbar />
    <div class="container py-4" v-if="me">
      <h2 class="mb-4">My Profile</h2>
      <div class="card shadow-sm" style="max-width: 460px;">
        <div class="card-body">
          <div class="alert alert-success py-2" v-if="saved">Profile updated!</div>

          <div class="mb-3">
            <label class="form-label">Name</label>
            <input v-model="me.name" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input :value="me.email" class="form-control" disabled>
          </div>
          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input v-model="me.phone" class="form-control" inputmode="numeric" maxlength="10" pattern="[0-9]{10}">
          </div>

          <button class="btn btn-success" @click="save">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>