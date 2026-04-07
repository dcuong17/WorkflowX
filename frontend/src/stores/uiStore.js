import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

function normalize(value) {
  return String(value ?? '').trim().toLowerCase()
}

export const useUiStore = defineStore('uiStore', () => {
  const searchQuery = ref('')

  const normalizedSearch = computed(() => normalize(searchQuery.value))
  const hasSearch = computed(() => normalizedSearch.value.length > 0)

  function setSearchQuery(value) {
    searchQuery.value = value
  }

  function clearSearch() {
    searchQuery.value = ''
  }

  return {
    searchQuery,
    normalizedSearch,
    hasSearch,
    setSearchQuery,
    clearSearch,
  }
})
