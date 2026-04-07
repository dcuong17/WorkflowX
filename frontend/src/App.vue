<script setup>
import { storeToRefs } from 'pinia'

import { apiClient } from './plugins/axios'
import { useWorkspaceStore } from './stores/workspace'

const workspaceStore = useWorkspaceStore()
const { stats, reviewSteps, apiBaseUrl } = storeToRefs(workspaceStore)

const endpointPreview = apiClient.getUri({ url: '/auth/signin' })
</script>

<template>
  <main class="min-h-screen bg-sand text-ink">
    <section class="mx-auto flex min-h-screen max-w-6xl flex-col justify-between px-6 py-8 lg:px-10">
      <div class="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div class="rounded-[2rem] bg-[radial-gradient(circle_at_top_left,_rgba(194,65,12,0.18),_transparent_36%),linear-gradient(135deg,_#fffaf3_0%,_#f3e2cf_52%,_#ead6bd_100%)] p-8 shadow-card lg:p-12">
          <p class="font-body text-sm uppercase tracking-[0.35em] text-ember">WorkflowX Frontend</p>
          <h1 class="mt-4 max-w-xl font-display text-5xl font-bold leading-none text-ink lg:text-7xl">
            Vue + Vite shell ready for backend integration.
          </h1>
          <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
            Frontend cũ đã được thay bằng một nền tảng mới dùng Vue, TailwindCSS, Pinia và Axios để kết nối tới API Django trong cùng repository.
          </p>

          <div class="mt-10 grid gap-4 sm:grid-cols-3">
            <article
              v-for="item in stats"
              :key="item.label"
              class="rounded-[1.5rem] border border-white/70 bg-white/80 p-5 backdrop-blur"
            >
              <p class="text-sm uppercase tracking-[0.2em] text-slate-500">{{ item.label }}</p>
              <p class="mt-3 text-3xl font-semibold text-ink">{{ item.value }}</p>
              <p class="mt-2 text-sm text-slate-600">{{ item.caption }}</p>
            </article>
          </div>
        </div>

        <aside class="rounded-[2rem] bg-ink p-8 text-white shadow-card lg:p-10">
          <p class="text-sm uppercase tracking-[0.3em] text-amber-200">Configured Modules</p>
          <ul class="mt-6 space-y-4">
            <li class="rounded-2xl bg-white/10 p-4">
              <p class="font-display text-xl">TailwindCSS</p>
              <p class="mt-2 text-sm text-slate-200">Utility-first styling is wired through <code>src/style.css</code> and <code>tailwind.config.js</code>.</p>
            </li>
            <li class="rounded-2xl bg-white/10 p-4">
              <p class="font-display text-xl">Pinia</p>
              <p class="mt-2 text-sm text-slate-200">A starter workspace store is mounted globally from <code>src/main.js</code>.</p>
            </li>
            <li class="rounded-2xl bg-white/10 p-4">
              <p class="font-display text-xl">Axios</p>
              <p class="mt-2 text-sm text-slate-200">Central API client points at <code>{{ apiBaseUrl }}</code>.</p>
            </li>
          </ul>
          <div class="mt-6 rounded-2xl border border-white/15 bg-black/10 p-4">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-300">Endpoint Preview</p>
            <p class="mt-2 break-all font-mono text-sm text-amber-100">{{ endpointPreview }}</p>
          </div>
        </aside>
      </div>

      <section class="mt-8 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <article class="rounded-[2rem] bg-white p-8 shadow-card">
          <p class="text-sm uppercase tracking-[0.3em] text-tide">Review Workflow</p>
          <ol class="mt-6 space-y-4">
            <li
              v-for="step in reviewSteps"
              :key="step.title"
              class="rounded-2xl border border-slate-200 px-5 py-4"
            >
              <p class="font-display text-xl text-ink">{{ step.title }}</p>
              <p class="mt-2 text-sm leading-7 text-slate-600">{{ step.description }}</p>
            </li>
          </ol>
        </article>

        <article class="rounded-[2rem] bg-white p-8 shadow-card">
          <p class="text-sm uppercase tracking-[0.3em] text-ember">Next Integration Targets</p>
          <div class="mt-6 grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl bg-cloud p-5">
              <h2 class="font-display text-2xl text-ink">Authentication</h2>
              <p class="mt-3 text-sm leading-7 text-slate-600">
                Connect forms to the backend auth endpoints and persist tokens in a dedicated Pinia auth store.
              </p>
            </div>
            <div class="rounded-2xl bg-cloud p-5">
              <h2 class="font-display text-2xl text-ink">Workspace Dashboard</h2>
              <p class="mt-3 text-sm leading-7 text-slate-600">
                Use the shared Axios client to load workspaces, members, and task counters from the backend.
              </p>
            </div>
            <div class="rounded-2xl bg-cloud p-5">
              <h2 class="font-display text-2xl text-ink">Task Review Board</h2>
              <p class="mt-3 text-sm leading-7 text-slate-600">
                Build manager and member views around the enforced backend status transitions.
              </p>
            </div>
            <div class="rounded-2xl bg-cloud p-5">
              <h2 class="font-display text-2xl text-ink">Environment Config</h2>
              <p class="mt-3 text-sm leading-7 text-slate-600">
                Override the API base URL at deploy time with <code>VITE_API_BASE_URL</code>.
              </p>
            </div>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>
