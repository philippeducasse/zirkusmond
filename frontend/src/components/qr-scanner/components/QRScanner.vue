<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import { Html5Qrcode } from "html5-qrcode";

const scanner = ref(null);
const lastScan = ref(null);
const error = ref(null);
const alreadyCheckedIn = ref(null);
const upcomingEvents = ref([]);
const selectedEvent = ref(null);

const successSound = ref(null);
const errorSound = ref(null);
const audioUnlocked = ref(false);

const unlockAudio = () => {
  if (audioUnlocked.value) return;
  [successSound.value, errorSound.value].forEach((audio) => {
    if (audio) {
      audio.volume = 0;
      audio
        .play()
        .then(() => {
          audio.pause();
          audio.currentTime = 0;
          audio.volume = 1;
        })
        .catch(() => {});
    }
  });
  audioUnlocked.value = true;
};

const fetchEvents = async () => {
  try {
    const response = await fetch("get-events");
    const data = await response.json();

    if (data.length > 0) {
      upcomingEvents.value = data;
      const today = new Date().toISOString().split("T")[0];
      const todayEvent = data.find((event) => event.begin.includes(today));
      if (todayEvent) {
        selectedEvent.value = todayEvent;
        initialiseScanner();
      }
    }
  } catch (err) {
    error.value = `Failed to load events: ${err.message}`;
  }
};

onMounted(() => {
  fetchEvents();
});

const playSound = (type) => {
  if (type === "success") {
    successSound.value?.play();
  } else if (type === "error") {
    errorSound.value?.play();
  }
};

const initialiseScanner = () => {
  scanner.value = new Html5Qrcode("reader");

  const config = {
    fps: 10,
    qrbox: (viewfinderWidth, viewfinderHeight) => {
      return { width: viewfinderWidth, height: viewfinderHeight };
    },
  };

  scanner.value
    .start({ facingMode: "environment" }, config, onScanSuccess, onScanError)
    .catch((err) => {
      error.value = `Failed to start scanner: ${err}`;
    });
};

const onScanSuccess = (decodedText) => {
  error.value = null;
  alreadyCheckedIn.value = null;
  lastScan.value = null;
  try {
    const data = JSON.parse(decodedText);
    checkInReservation(data.ticket, data.event);
  } catch {
    error.value = "Invalid QR code format";
    playSound("error");
  }
};

const onScanError = (err) => {
  if (!err.includes("No QR code found")) {
    // console.debug(err);
  }
};

onBeforeUnmount(() => {
  if (scanner.value) {
    scanner.value.stop();
  }
});

const checkInReservation = async (ticket_uuid, event_uuid) => {
  if (event_uuid !== selectedEvent.value.id) {
    error.value = "Ticket for wrong event!";
    playSound("error");
    return;
  }
  try {
    const response = await fetch(`${ticket_uuid}/check-in`);
    const data = await response.json();
    if (data.success) {
      lastScan.value = data;
      playSound("success");
      scanner.value.pause();
      setTimeout(() => scanner.value.resume(), 2000);
    } else if (data.error === "Ticket already checked in") {
      alreadyCheckedIn.value = data;
      scanner.value.pause();
      playSound("error");
      setTimeout(() => scanner.value.resume(), 2000);
    } else {
      playSound("error");
      error.value = data.error || "Check-in failed";
    }
  } catch (err) {
    error.value = `Error: ${err.message}`;
  }
};
</script>
<template>
  <div class="min-h-screen p-4" @click="unlockAudio">
    <div class="max-w-2xl mx-auto">
      <h1 class="text-6xl md:text-3xl font-bold mb-6 text-center">QR Code Scanner</h1>

      <h2 v-if="selectedEvent" class="text-5xl md:text-2xl font-bold mb-6 text-center">
        {{ selectedEvent.title }}-{{ selectedEvent.date }}
      </h2>
      <button
        v-if="selectedEvent"
        class="my-2 text-center w-full text-3xl"
        @click="
          selectedEvent = null;
          unlockAudio();
        "
      >
        Select another event
      </button>
      <!-- Event Selector -->
      <div v-if="!selectedEvent" class="p-4 mb-6">
        <label class="block text-3xl font-bold mb-2">Select Event:</label>
        <select
          v-model="selectedEvent"
          class="w-full px-4 py-3 text-xl border rounded-lg"
          @change="
            initialiseScanner();
            unlockAudio();
          "
        >
          <option value="">Choose an event...</option>
          <option v-for="event in upcomingEvents" :key="event.id" :value="event">
            {{ event.title }} - {{ event.date }}
          </option>
        </select>
      </div>

      <div id="reader" class="bg-white rounded-lg shadow-lg mb-6"></div>

      <div v-if="lastScan" class="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <h2 class="font-bold text-green-800 text-6xl mb-2">Checked In</h2>
        <div class="flex flex-col items-center">
          <svg
            class="w-28 h-28 mx-auto text-green-500 mb-4"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          <div class="text-left">
            <template v-if="lastScan.is_group">
              <p class="text-6xl"><strong>Tickets:</strong> {{ lastScan.guests.length }}</p>
              <p class="text-5xl"><strong>Guests:</strong> {{ lastScan.guests.join(", ") }}</p>
            </template>
            <template v-else>
              <p class="text-5xl"><strong>Guest:</strong> {{ lastScan.guests[0] }}</p>
            </template>
            <p class="text-5xl">
              <strong>Reservation ID:</strong> {{ lastScan.reservation_number }}
            </p>
          </div>
        </div>
      </div>

      <div
        v-else-if="alreadyCheckedIn"
        class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center"
      >
        <h2 class="font-bold text-yellow-800 text-6xl mb-2">Already Checked In</h2>
        <div class="flex flex-col items-center">
          <svg
            class="w-28 h-28 mx-auto text-yellow-500 mb-4"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div class="text-left">
            <p class="text-5xl">
              <strong>Reservation ID:</strong> {{ alreadyCheckedIn.reservation_number }}
            </p>
            <p class="text-5xl">
              <strong>Guests:</strong> {{ alreadyCheckedIn.guests.join(", ") }}
            </p>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div class="flex flex-col items-center justify-center">
          <svg
            class="w-28 h-28 mx-8 text-red-500 mb-4"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <p class="text-red-800 text-6xl">{{ error }}</p>
        </div>
      </div>
      <audio ref="successSound" src="/static/success_sound.mp3"></audio>
      <audio ref="errorSound" src="/static/error_sound.mp3"></audio>
    </div>
  </div>
</template>

<style scoped>
#reader {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}
</style>
