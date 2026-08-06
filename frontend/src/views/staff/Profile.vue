<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import { api } from '../../api.js'

const me = ref(null)
const profile = ref(null)
const saved = ref(false)

async function load() {
    const r = await api.staffProfile()
    me.value = r.me
    profile.value = r.profile
}

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
        await api.staffUpdateProfile({
            name: me.value.name, phone: me.value.phone,
            designation: profile.value.designation, experience_years: profile.value.experience_years, bio: profile.value.bio,
        })
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
      <div class="card shadow-sm" style="max-width: 520px;">
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
          <div class="mb-3">
            <label class="form-label">Designation</label>
            <input v-model="profile.designation" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Experience (years)</label>
            <input type="number" min="0" v-model="profile.experience_years" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Bio</label>
            <textarea v-model="profile.bio" class="form-control" rows="3"></textarea>
          </div>

          <button class="btn btn-success" @click="save">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>