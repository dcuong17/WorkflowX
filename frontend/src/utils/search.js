export function normalizeSearchTerm(value) {
  return String(value ?? '').trim().toLowerCase()
}

export function matchesSearch(targets, searchQuery) {
  if (!searchQuery) return true

  return targets.some((target) => normalizeSearchTerm(target).includes(searchQuery))
}
