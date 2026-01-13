<template>
  <div class="fixed inset-0 flex items-center justify-center">
    <GlassSurface :width="450" :height="520" :border-radius="24">
      <!-- Chat Container -->
      <div class="w-full h-full flex flex-col text-white">
        <!-- Header -->
        <div class="px-4 py-3 border-b border-white/10 text-sm font-medium">AvenCB</div>

        <!-- Messages -->
        <div ref="chatArea" class="flex-1 px-4 py-3 space-y-3 overflow-y-auto no-scrollbar scroll-smooth">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="msg.role === 'user' ? 'ml-auto bg-white/20' : 'mr-auto bg-white/10'"
            class="max-w-[75%] px-3 py-2 rounded-xl text-sm backdrop-blur"
          >
            {{ msg.text }}
          </div>
        </div>

        <!-- Input -->
        <div class="p-3 border-t border-white/10">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input
              v-model="input"
              type="text"
              placeholder="Type something..."
              class="flex-1 bg-white/10 rounded-lg px-3 py-2 text-sm outline-none placeholder-white/40"
            />
            <button
              type="submit"
              class="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-sm"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </GlassSurface>
  </div>
</template>

<script setup>
import GlassSurface from '../GlassSurface.vue'
import { ref, nextTick } from 'vue'

const input = ref('')
const chatArea = ref(null)

const messages = ref([
  { role: 'bot', text: 'Hello. Say something.' }
])

const pushMessage = (msg) => {
  messages.value.push(msg)
  if (messages.value.length > 10) {
    messages.value = messages.value.slice(-10)
  }
}

const replaceLastBotMessage = (text) => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'bot') {
      messages.value[i].text = text
      return
    }
  }
}

const sendMessage = async () => {
  const userText = input.value.trim()
  if (!userText) return

  // user message
  pushMessage({ role: 'user', text: userText })
  input.value = ''

  // typing indicator
  pushMessage({ role: 'bot', text: '...' })

  await nextTick()
  chatArea.value.scrollTop = chatArea.value.scrollHeight

  try {
    const res = await fetch('https://avencbot-b.onrender.com/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: messages.value,
      }),
    })

    const data = await res.json()

    replaceLastBotMessage(data.message ?? 'No response')
  } catch (err) {
    replaceLastBotMessage('Server error. Try again.')
  }

  await nextTick()
  chatArea.value.scrollTop = chatArea.value.scrollHeight
}
</script>

<style scoped>
.no-scrollbar {
  -ms-overflow-style: none;  /* IE & Edge */
  scrollbar-width: none;     /* Firefox */
}
.no-scrollbar::-webkit-scrollbar {
  display: none;             /* Chrome, Safari */
}
</style>
