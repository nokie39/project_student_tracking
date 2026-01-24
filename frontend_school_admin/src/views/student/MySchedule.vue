<template>
  <v-container class="py-6">
    <div class="text-h5 font-weight-bold mb-4 text-primary">
      <v-icon start>mdi-calendar-month</v-icon> ຕາຕະລາງຮຽນ
    </div>

    <div v-if="loading" class="d-flex justify-center align-center" style="height: 300px;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <v-card v-else rounded="xl" elevation="3">
      <v-tabs
        v-model="activeTab"
        bg-color="primary"
        align-tabs="center"
        show-arrows
        slider-color="yellow-accent-4"
      >
        <v-tab v-for="(dayName, index) in dayNames" :key="index" :value="index + 1">
          {{ dayName }}
        </v-tab>
      </v-tabs>

      <v-card-text class="bg-grey-lighten-4" style="min-height: 400px;">
        <v-window v-model="activeTab">
          <v-window-item v-for="dayIndex in [1, 2, 3, 4, 5, 6, 7]" :key="dayIndex" :value="dayIndex">
            
            <div v-if="groupedSchedules[dayIndex] && groupedSchedules[dayIndex].length > 0">
              <v-timeline side="end" density="compact">
                <v-timeline-item
                  v-for="item in groupedSchedules[dayIndex]"
                  :key="item.id"
                  dot-color="indigo"
                  size="small"
                >
                  <template v-slot:opposite>
                    <span class="text-h6 font-weight-bold text-indigo">{{ formatTime(item.start_time) }}</span>
                    <div class="text-caption text-grey">ເຖິງ {{ formatTime(item.end_time) }}</div>
                  </template>

                  <v-card class="elevation-2" rounded="lg">
                    <v-card-item>
                      <div class="d-flex justify-space-between align-start">
                        <div>
                          <v-card-title class="text-body-1 font-weight-bold">
                            {{ item.subject_name }}
                          </v-card-title>
                          <v-card-subtitle>
                            <v-icon size="small" start>mdi-account</v-icon> {{ item.teacher_name }}
                          </v-card-subtitle>
                        </div>
                        
                        <v-tooltip text="ເພີ່ມລົງປະຕິທິນ" location="top">
                          <template v-slot:activator="{ props }">
                            <v-btn 
                              v-bind="props"
                              icon="mdi-calendar-plus" 
                              variant="text" 
                              color="primary"
                              size="small"
                              @click="addToGoogleCalendar(item)"
                            ></v-btn>
                          </template>
                        </v-tooltip>
                      </div>
                    </v-card-item>
                    
                    <v-divider></v-divider>
                    
                    <v-card-text class="py-2 d-flex align-center text-caption text-grey-darken-1">
                      <v-icon size="small" start color="red">mdi-map-marker</v-icon> 
                      ຫ້ອງ: {{ item.room }}
                      <v-spacer></v-spacer>
                      <span v-if="item.note" class="text-info font-italic">
                         "{{ item.note }}"
                      </span>
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </div>

            <div v-else class="d-flex flex-column align-center justify-center pt-10 text-grey">
              <v-icon size="60" class="mb-2">mdi-coffee-outline</v-icon>
              <div class="text-h6">ມື້ນີ້ບໍ່ມີການຮຽນ-ການສອນ</div>
              <div class="text-body-2">ພັກຜ່ອນໃຫ້ສະບາຍໃຈ!</div>
            </div>

          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../services/api';

const loading = ref(true);
const schedules = ref([]);
const activeTab = ref(1);
const dayNames = ['ວັນຈັນ', 'ວັນອັງຄານ', 'ວັນພຸດ', 'ວັນພະຫັດ', 'ວັນສຸກ', 'ວັນເສົາ', 'ວັນອາທິດ'];

const groupedSchedules = computed(() => {
  const groups = {};
  schedules.value.forEach(item => {
    if (!groups[item.day_of_week]) groups[item.day_of_week] = [];
    groups[item.day_of_week].push(item);
  });
  return groups;
});

const fetchSchedule = async () => {
  try {
    const res = await api.get('/students/schedule');
    schedules.value = res.data;
    const today = new Date().getDay(); 
    activeTab.value = today === 0 ? 7 : today;
  } catch (error) {
    console.error("Error fetching schedule:", error);
  } finally {
    loading.value = false;
  }
};

const formatTime = (timeStr) => {
  return timeStr ? timeStr.substring(0, 5) : '';
};

// 🔥 Function: Add to Google Calendar
const addToGoogleCalendar = (item) => {
  // 1. ຄຳນວນຫາວັນທີຂອງ "ວັນຮຽນຄັ້ງຖັດໄປ"
  const now = new Date();
  const currentDay = now.getDay(); // 0=Sun, 1=Mon
  
  // ປ່ຽນ DB Day (1=Mon...7=Sun) ໃຫ້ເປັນ JS Day (0=Sun...6=Sat) ເພື່ອຄຳນວນ
  // DB: 1, 2, 3, 4, 5, 6, 7
  // JS: 1, 2, 3, 4, 5, 6, 0
  const targetDay = item.day_of_week === 7 ? 0 : item.day_of_week;
  
  // ຄຳນວນວ່າອີກຈັກມື້ຈະຮອດ (Days Until)
  let daysUntil = (targetDay + 7 - currentDay) % 7;
  if (daysUntil === 0) daysUntil = 0; // ຖ້າແມ່ນມື້ນີ້ກໍເອົາມື້ນີ້ເລີຍ

  const targetDate = new Date(now);
  targetDate.setDate(now.getDate() + daysUntil);

  // 2. ຕັ້ງເວລາເລີ່ມ ແລະ ເວລາຈົບ
  const [startH, startM] = item.start_time.split(':');
  const [endH, endM] = item.end_time.split(':');

  const startDate = new Date(targetDate);
  startDate.setHours(parseInt(startH), parseInt(startM), 0);
  
  const endDate = new Date(targetDate);
  endDate.setHours(parseInt(endH), parseInt(endM), 0);

  // 3. ຈັດ Format ວັນທີໃຫ້ເປັນແບບ Google (YYYYMMDDTHHMMSS)
  // ໃຊ້ Local Time ເພື່ອບໍ່ໃຫ້ງົງເລື່ອງ Timezone
  const formatGCalDate = (date) => {
    const pad = (n) => n < 10 ? '0' + n : n;
    return date.getFullYear() +
           pad(date.getMonth() + 1) +
           pad(date.getDate()) + 'T' +
           pad(date.getHours()) +
           pad(date.getMinutes()) + '00';
  };

  const startStr = formatGCalDate(startDate);
  const endStr = formatGCalDate(endDate);

  // 4. ສ້າງ URL
  const title = `ຮຽນ: ${item.subject_name}`;
  const details = `ອາຈານ: ${item.teacher_name || '-'}\nໝາຍເຫດ: ${item.note || '-'}`;
  const location = `ຫ້ອງ ${item.room}`;
  
  // recur=RRULE:FREQ=WEEKLY ແປວ່າໃຫ້ມັນເຕືອນທຸກອາທິດ
  const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&dates=${startStr}/${endStr}&details=${encodeURIComponent(details)}&location=${encodeURIComponent(location)}&recur=RRULE:FREQ=WEEKLY`;

  // 5. ເປີດ Tab ໃໝ່
  window.open(url, '_blank');
};

onMounted(fetchSchedule);
</script>

<style scoped>
:deep(.v-timeline-item__body) {
  width: 100%;
}
</style>