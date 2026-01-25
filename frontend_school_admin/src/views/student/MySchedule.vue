<template>
  <v-container class="py-6">
    
    <div class="d-flex flex-wrap justify-space-between align-center mb-6">
      <div class="text-h5 font-weight-bold text-primary">
        <v-icon start>mdi-calendar-month</v-icon> ຕາຕະລາງຮຽນ (My Schedule)
      </div>
      
      <div style="width: 180px;">
        <v-select
          v-model="selectedSemester"
          :items="semesters"
          item-title="title"
          item-value="id"
          label="ເລືອກພາກຮຽນ"
          variant="solo-filled"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-calendar-range"
          @update:model-value="fetchSchedule"
          class="rounded-lg"
        ></v-select>
      </div>
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
                  :dot-color="getSubjectColor(item.subject_name)"
                  size="small"
                >
                  <template v-slot:opposite>
                    <span class="text-subtitle-1 font-weight-bold text-grey-darken-3">{{ formatTime(item.start_time) }}</span>
                    <div class="text-caption text-grey">ເຖິງ {{ formatTime(item.end_time) }}</div>
                  </template>

                  <v-card class="elevation-2 border-s-lg" :style="{ 'border-left-color': getSubjectColor(item.subject_name) + ' !important' }">
                    <v-card-item>
                      <div class="d-flex justify-space-between align-start">
                        <div>
                          <v-card-title class="text-body-1 font-weight-bold text-primary">
                            {{ item.subject_name }}
                          </v-card-title>
                          <v-card-subtitle>
                            <v-icon size="small" start>mdi-human-male-board</v-icon> {{ item.teacher_name }}
                          </v-card-subtitle>
                        </div>
                        
                        <v-tooltip text="ເພີ່ມລົງ Google Calendar" location="top">
                          <template v-slot:activator="{ props }">
                            <v-btn 
                              v-bind="props"
                              icon="mdi-calendar-plus" 
                              variant="text" 
                              color="success"
                              size="small"
                              @click="addToGoogleCalendar(item)"
                            ></v-btn>
                          </template>
                        </v-tooltip>
                      </div>
                    </v-card-item>
                    
                    <v-divider></v-divider>
                    
                    <v-card-text class="py-2 d-flex align-center text-caption text-grey-darken-2">
                      <v-icon size="small" start color="red-lighten-1">mdi-map-marker</v-icon> 
                      ຫ້ອງ: <strong>{{ item.room || '-' }}</strong>
                      <v-spacer></v-spacer>
                      <span v-if="item.note" class="text-info font-italic">
                         <v-icon size="small" start>mdi-note-text</v-icon> "{{ item.note }}"
                      </span>
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </div>

            <div v-else class="d-flex flex-column align-center justify-center pt-16 text-grey">
              <v-icon size="80" color="grey-lighten-2" class="mb-4">mdi-calendar-blank</v-icon>
              <div class="text-h6 font-weight-regular">ມື້ນີ້ບໍ່ມີການຮຽນ-ການສອນ</div>
              <div class="text-body-2">ພັກຜ່ອນໃຫ້ສະບາຍໃຈ! 😊</div>
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

// Semester Selection
const semesters = [
  { id: 1, title: 'ພາກຮຽນ 1' },
  { id: 2, title: 'ພາກຮຽນ 2' }
];
const selectedSemester = ref(1);

const groupedSchedules = computed(() => {
  const groups = {};
  schedules.value.forEach(item => {
    // Convert Day String to Index if needed
    let dIndex = parseInt(item.day_of_week);
    if(isNaN(dIndex)) {
       const dayMap = { 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7 };
       dIndex = dayMap[item.day_of_week] || 1;
    }

    if (!groups[dIndex]) groups[dIndex] = [];
    groups[dIndex].push(item);
  });
  return groups;
});

const fetchSchedule = async () => {
  loading.value = true;
  try {
    // ✅ ສົ່ງ semester_id ໄປນຳ
    const res = await api.get(`/students/schedule?semester_id=${selectedSemester.value}`);
    schedules.value = res.data;
    
    // Set active tab to today
    const today = new Date().getDay(); // 0=Sun, 1=Mon
    activeTab.value = today === 0 ? 7 : today;
  } catch (error) {
    console.error("Error fetching schedule:", error);
  } finally {
    loading.value = false;
  }
};

const formatTime = (timeStr) => timeStr ? timeStr.substring(0, 5) : '';

// Helper for Colors
const getSubjectColor = (subjectName) => {
    if (!subjectName) return 'indigo';
    const name = subjectName.toLowerCase();
    if (name.includes('ຄະນິດ') || name.includes('math')) return 'blue'; 
    if (name.includes('ພາສາ') || name.includes('english')) return 'red'; 
    if (name.includes('ພະລະ') || name.includes('sport')) return 'green'; 
    if (name.includes('ict') || name.includes('com')) return 'purple'; 
    return 'indigo';
};

// Function: Add to Google Calendar
const addToGoogleCalendar = (item) => {
  const now = new Date();
  const currentDay = now.getDay(); 
  let targetDay = parseInt(item.day_of_week);
  if(isNaN(targetDay)) {
       const dayMap = { 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7 };
       targetDay = dayMap[item.day_of_week] || 1;
  }
  const jsDay = targetDay === 7 ? 0 : targetDay;
  
  let daysUntil = (jsDay + 7 - currentDay) % 7;
  if (daysUntil === 0) daysUntil = 0; 

  const targetDate = new Date(now);
  targetDate.setDate(now.getDate() + daysUntil);

  const [startH, startM] = item.start_time.split(':');
  const [endH, endM] = item.end_time.split(':');

  const startDate = new Date(targetDate);
  startDate.setHours(parseInt(startH), parseInt(startM), 0);
  
  const endDate = new Date(targetDate);
  endDate.setHours(parseInt(endH), parseInt(endM), 0);

  const formatGCalDate = (date) => {
    const pad = (n) => n < 10 ? '0' + n : n;
    return date.getFullYear() + pad(date.getMonth() + 1) + pad(date.getDate()) + 'T' + pad(date.getHours()) + pad(date.getMinutes()) + '00';
  };

  const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent('ຮຽນ: ' + item.subject_name)}&dates=${formatGCalDate(startDate)}/${formatGCalDate(endDate)}&details=${encodeURIComponent('ຄູ: ' + item.teacher_name)}&location=${encodeURIComponent('ຫ້ອງ ' + item.room)}&recur=RRULE:FREQ=WEEKLY`;
  window.open(url, '_blank');
};

onMounted(fetchSchedule);
</script>

<style scoped>
:deep(.v-timeline-item__body) { width: 100%; }
.border-s-lg { border-left-width: 4px !important; }
</style>