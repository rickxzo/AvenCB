<template>
  <nav
    class="fixed top-0 left-0 w-full z-10 flex items-center justify-between px-12 py-6 text-white text-[12.5px] tracking-widest"
  >
    <!-- Brand -->
    <TextType
      class="text-[13px] font-['Roboto'] tracking-wider"
      :text="['RICK’S AvenCB']"
      :typingSpeed="75"
      :pauseDuration="1500"
      :showCursor="true"
      cursorCharacter="_"
    />

    <!-- Links -->
    <div class="flex gap-16 pr-32">
      <!-- HOME -->
      <router-link to="/" v-slot="{ isActive }">
        <span class="relative inline-block group leading-none">
          <!-- LEFT BRACKET -->
          <span
            class="absolute -left-4 transition-all duration-300 ease-out opacity-0 group-hover:opacity-100 group-hover:-translate-y-0"
            :class="isActive ? 'opacity-100 text-cyan-300' : 'text-white/60'"
          >
            [
          </span>

          <!-- LABEL -->
          <span
            class="transition-opacity duration-200 leading-none"
            :class="isActive ? 'opacity-100' : 'opacity-60'"
          >
            HOME
          </span>

          <!-- RIGHT BRACKET -->
          <span
            class="absolute -right-4 transition-all duration-300 ease-out opacity-0 group-hover:opacity-100 group-hover:-translate-y-0"
            :class="isActive ? 'opacity-100 text-cyan-300' : 'text-white/60'"
          >
            ]
          </span>
        </span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
import TextType from '../TextType.vue'
</script>
