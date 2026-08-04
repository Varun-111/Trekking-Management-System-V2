<script setup>
defineProps(['page', 'totalPages'])
const emit = defineEmits(['change'])
</script>

<template>
  <nav v-if="totalPages > 1" class="mt-3">
    <ul class="pagination justify-content-center mb-0">
      <li class="page-item" :class="{ disabled: page <= 1 }">
        <button class="page-link" :disabled="page <= 1" @click="emit('change', page - 1)">
          <i class="bi bi-chevron-left"></i>
        </button>
      </li>
      <li
        v-for="p in totalPages"
        :key="p"
        class="page-item"
        :class="{ active: p === page }"
      >
        <button class="page-link" @click="emit('change', p)">{{ p }}</button>
      </li>
      <li class="page-item" :class="{ disabled: page >= totalPages }">
        <button class="page-link" :disabled="page >= totalPages" @click="emit('change', page + 1)">
          <i class="bi bi-chevron-right"></i>
        </button>
      </li>
    </ul>
  </nav>
</template>