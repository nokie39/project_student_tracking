<template>
  <v-container fluid class="fill-height align-start bg-grey-lighten-5 pa-0">
    
    <v-card color="primary" rounded="b-xl" class="pa-4 pb-8 w-100" elevation="4">
      <div class="d-flex align-center justify-space-between text-white">
        <v-btn icon="mdi-chevron-left" variant="text" color="white" @click="changeMonth(-1)"></v-btn>
        
        <div class="text-center">
          <div class="text-h6 font-weight-bold">{{ currentMonthName }} {{ currentYear }}</div>
          <div class="text-caption opacity-80">ຕາຕະລາງຮຽນປະຈຳເດືອນ</div>
        </div>

        <v-btn icon="mdi-chevron-right" variant="text" color="white" @click="changeMonth(1)"></v-btn>
      </div>
    </v-card>

    <v-card class="mx-4 mt-n6 rounded-xl pa-2" elevation="3">
      <div class="d-flex justify-space-between mb-2 text-center">
        <div v-for="day in weekDays" :key="day" class="text-caption font-weight-bold text-grey-darken-1" style="width: 14.28%">
          {{ day }}
        </div>
      </div>

      <div class="d-flex flex-wrap">
        <div 
          v-for="n in startDayOffset" 
          :key="'empty-'+n" 
          style="width: 14.28%; height: 50px;"
        ></div>

        <div 
          v-for="date in daysInMonth" 
          :key="date" 
          style="width: 14.28%; height: 55px;"
          class="d-flex flex-column align-center justify-start pt-1 position-relative"
          @click="selectDate(date)"
        >
          <v-avatar 
            size="32" 
            :color="isSelected(date) ? 'primary' : (isToday(date) ? 'blue-lighten-4' : 'transparent')"
            :class="isSelected(date) ? 'text-white font-weight-bold' : 'text-grey-darken-3'"
            variant="flat"
          >
            {{ date }}
          </v-avatar>

          <div class="d-flex mt-1" v-if="getEventsForDate(date).length > 0">
            <v-icon size="6" color="success" class="mx-0">mdi-circle</v-icon>
            <v-icon v-if="getEventsForDate(date).length > 1" size="6" color="warning" class="ml-1">mdi-circle</v-icon>
          </div>
        </div>
      </div>
    </v-card>

    <v-container class="px-4 mt-2">
      <div class="text-subtitle-1 font-weight-bold text-grey-darken-3 mb-2">
        ວັນ{{ getLaoDayName(selectedDateObj) }}, ທີ {{ selectedDate }}
      </div>

      <div v-if="selectedEvents.length > 0">
        <v-timeline density="compact" side="end" align="start">
          <v-timeline-item
            v-for="sub in selectedEvents"
            :key="sub.id"
            :dot-color="getSubjectColor(sub.subject_name)"
            size="small"
            fill-dot
          >
            <v-card variant="outlined" class="ml-2 rounded-lg" :color="getSubjectColor(sub.subject_name)">
              <v-card-item class="py-2">
                <div class="d-flex justify-space-between">
                  <span class="text-caption font-weight-bold text-grey-darken-2">
                    {{ formatTime(sub.start_time) }} - {{ formatTime(sub.end_time) }}
                  </span>
                  <v-chip size="x-small" variant="flat" color="white" class="text-black">
                    ຫ້ອງ {{ sub.room }}
                  </v-chip>
                </div>
                <div class="text-subtitle-2 font-weight-bold mt-1">{{ sub.subject_name }}</div>
                <div class="text-caption text-grey-darken-2">
                  <v-icon size="small" start>mdi-account</v-icon> {{ sub.teacher_name || 'ຄູປະຈຳວິຊາ' }}
                </div>
              </v-card-item>
            </v-card>
          </v-timeline-item>
        </v-timeline>
      </div>

      <div v-else class="text-center py-10">
        <v-icon size="60" color="grey-lighten-2">mdi-calendar-blank</v-icon>
        <div class="text-body-1 text-grey mt-2">ບໍ່ມີຕາຕະລາງຮຽນ</div>
        <div class="text-caption text-grey-lighten-1">ພັກຜ່ອນໄດ້ເຕັມທີ່! 😴</div>
      </div>

    </v-container>

  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../services/api';

// State
const currentDateObj = ref(new Date());
const selectedDate = ref(new Date().getDate());
const schedules = ref([]);
const weekDays = ['ອາ', 'ຈ', 'ອ', 'ພ', 'ພຫ', 'ສຸ', 'ເສ'];

// ✅ 1. ສ້າງ Mapping ພາສາ (ໃຫ້ກົງກັບ Database ຂອງທ່ານ)
const dayMapping = {
  'Sunday': 'ວັນອາທິດ',
  'Monday': 'ວັນຈັນ',
  'Tuesday': 'ວັນອັງຄານ',
  'Wednesday': 'ວັນພຸດ',
  'Thursday': 'ວັນພະຫັດ',
  'Friday': 'ວັນສຸກ',
  'Saturday': 'ວັນເສົາ'
};

// API Fetch
const fetchSchedule = async () => {
  try {
    const res = await api.get('/students/schedule');
    schedules.value = res.data;
  } catch (error) {
    console.error(error);
  }
};

// --- Calendar Logic ---

const currentYear = computed(() => currentDateObj.value.getFullYear());
const currentMonth = computed(() => currentDateObj.value.getMonth());

const currentMonthName = computed(() => {
  const months = [
    'ມັງກອນ', 'ກຸມພາ', 'ມີນາ', 'ເມສາ', 'ພຶດສະພາ', 'ມິຖຸນາ',
    'ກໍລະກົດ', 'ສິງຫາ', 'ກັນຍາ', 'ຕຸລາ', 'ພະຈິກ', 'ທັນວາ'
  ];
  return months[currentMonth.value];
});

const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate();
});

const startDayOffset = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 1).getDay();
});

const selectedDateObj = computed(() => {
  return new Date(currentYear.value, currentMonth.value, selectedDate.value);
});

// --- Actions ---

const changeMonth = (offset) => {
  const newDate = new Date(currentDateObj.value);
  newDate.setMonth(newDate.getMonth() + offset);
  currentDateObj.value = newDate;
  selectedDate.value = 1; 
};

const selectDate = (date) => {
  selectedDate.value = date;
};

// --- Helper Functions ---

const isSelected = (date) => date === selectedDate.value;

const isToday = (date) => {
  const today = new Date();
  return date === today.getDate() && 
         currentMonth.value === today.getMonth() && 
         currentYear.value === today.getFullYear();
};

const getLaoDayName = (dateObj) => {
  const daysFull = ['ທິດ', 'ຈັນ', 'ອັງຄານ', 'ພຸດ', 'ພະຫັດ', 'ສຸກ', 'ເສົາ'];
  return daysFull[dateObj.getDay()];
};

// ✅ 2. ແກ້ໄຂຟັງຊັນນີ້ໃຫ້ໃຊ້ Mapping
const getEventsForDate = (date) => {
  // ຫາວັນພາສາອັງກິດ (Monday, Tuesday...)
  const tempDate = new Date(currentYear.value, currentMonth.value, date);
  const dayNameEn = tempDate.toLocaleDateString('en-US', { weekday: 'long' });

  // ແປງເປັນພາສາລາວ (ວັນຈັນ, ວັນອັງຄານ...)
  const dayNameLao = dayMapping[dayNameEn];

  // Filter ໂດຍທຽບກັບພາສາລາວ
  return schedules.value.filter(s => {
    if (!s.day_of_week) return false;
    return s.day_of_week.trim() === dayNameLao;
  }).sort((a,b) => a.start_time.localeCompare(b.start_time));
};

const selectedEvents = computed(() => {
  return getEventsForDate(selectedDate.value);
});

const formatTime = (time) => time?.substring(0, 5);

const getSubjectColor = (subject) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'deep-purple'];
  let hash = 0;
  for (let i = 0; i < subject.length; i++) hash = subject.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
};

onMounted(fetchSchedule);
</script>

<style scoped>
.v-avatar {
  font-size: 14px;
}
</style>