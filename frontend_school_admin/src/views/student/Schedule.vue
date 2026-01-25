<template>
  <v-container fluid class="pa-0 pa-md-4">
    <v-card elevation="2" rounded="lg" class="h-100">
      
      <v-card-title class="d-flex flex-wrap justify-space-between align-center py-4 px-4 bg-primary text-white print-hide">
        <div class="text-h6 d-flex align-center">
          <v-icon icon="mdi-calendar-month" start></v-icon>
          ຕາຕະລາງຮຽນ (My Schedule)
        </div>
        <div class="d-flex align-center gap-2">
            <div style="width: 160px;" class="mr-2">
                <v-select
                v-model="selectedSemester"
                :items="semesters"
                item-title="title"
                item-value="id"
                label="ພາກຮຽນ"
                variant="solo-filled"
                density="compact"
                hide-details
                bg-color="white"
                class="text-body-2"
                @update:model-value="fetchSchedule"
                ></v-select>
            </div>
            <v-btn 
                color="white" 
                variant="elevated" 
                class="text-primary font-weight-bold" 
                prepend-icon="mdi-printer" 
                @click="printSchedule"
            >
                ພິມ
            </v-btn>
        </div>
      </v-card-title>

      <v-card-text class="mt-4">
        <div v-if="loading" class="d-flex justify-center align-center" style="height: 300px;">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else class="timetable-container" id="printable-area">
            <div class="print-header text-center mb-4">
                <div class="text-h4 font-weight-bold mb-2">ຕາຕະລາງຮຽນ</div>
                <div class="text-h6">
                    ນັກຮຽນ: {{ userProfile?.full_name || 'N/A' }} 
                    <span class="ml-4">ພາກຮຽນທີ: {{ selectedSemester }}</span>
                </div>
                <div class="text-subtitle-1">ສົກຮຽນ 2025-2026</div>
            </div>

            <div class="timetable-wrapper">
                <div class="time-header"></div>
                <div v-for="day in days" :key="day.value" class="day-header">{{ day.text }}</div>

                <template v-for="(slot, index) in timeSlots" :key="index">
                    <div class="time-col">
                        <div class="font-weight-bold">{{ slot.start }} - {{ slot.end }}</div>
                        <div class="text-caption">ຊົ່ວໂມງທີ {{ index + 1 }}</div>
                    </div>
                    <div 
                        v-for="day in days" 
                        :key="day.value + index" 
                        class="slot-cell"
                        :class="{'has-subject': getSubject(day.value, slot.start), 'break-time': slot.isBreak}"
                        @click="handleSlotClick(getSubject(day.value, slot.start))"
                    >
                        <div 
                            v-if="getSubject(day.value, slot.start)" 
                            class="subject-card" 
                            :style="{ backgroundColor: getSubjectColor(getSubject(day.value, slot.start).subject_name) }"
                        >
                            <div class="subject-content">
                                <div class="subject-name">{{ getSubject(day.value, slot.start).subject_name }}</div>
                                <div class="teacher-name">
                                    <v-icon size="x-small" class="print-hide" color="white">mdi-account</v-icon>
                                    {{ getSubject(day.value, slot.start).teacher_name }}
                                </div>
                                <div class="room-name" v-if="getSubject(day.value, slot.start).room">
                                    ({{ getSubject(day.value, slot.start).room }})
                                </div>
                            </div>
                        </div>
                        <div v-else class="break-text text-grey-lighten-1">{{ slot.name }}</div>
                    </div>
                </template>
            </div>

            <div class="print-footer mt-10">
                <div class="d-flex justify-space-around">
                    <div class="text-center"><p><strong>ຜູ້ອຳນວຍການ</strong></p><br><br><br><p>................................</p></div>
                    <div class="text-center"><p><strong>ວິຊາການ</strong></p><br><br><br><p>................................</p></div>
                    <div class="text-center"><p><strong>ຄູປະຈຳຫ້ອງ</strong></p><br><br><br><p>................................</p></div>
                </div>
            </div>
        </div>
      </v-card-text>

      <v-dialog v-model="detailDialog" max-width="450px">
        <v-card rounded="xl" v-if="selectedItem">
            <v-toolbar :color="getSubjectColor(selectedItem.subject_name)" dark>
                <v-toolbar-title class="text-white font-weight-bold">
                    <v-icon start>mdi-book-open-variant</v-icon> ລາຍລະອຽດວິຊາ
                </v-toolbar-title>
                <v-btn icon dark @click="detailDialog = false"><v-icon>mdi-close</v-icon></v-btn>
            </v-toolbar>

            <v-card-text class="pt-6">
                <div class="text-h6 font-weight-bold text-center mb-1">{{ selectedItem.subject_name }}</div>
                <div class="text-center text-grey mb-6">
                    {{ getDayText(selectedItem.day_of_week) }} | {{ formatTime(selectedItem.start_time) }} - {{ formatTime(selectedItem.end_time) }}
                </div>

                <v-list density="compact" class="bg-grey-lighten-5 rounded-lg border">
                    <v-list-item>
                        <template v-slot:prepend><v-icon color="indigo">mdi-human-male-board</v-icon></template>
                        <v-list-item-title>ຄູສອນ</v-list-item-title>
                        <v-list-item-subtitle class="text-body-1 text-black">{{ selectedItem.teacher_name || '-' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    <v-list-item>
                        <template v-slot:prepend><v-icon color="red">mdi-map-marker</v-icon></template>
                        <v-list-item-title>ຫ້ອງຮຽນ</v-list-item-title>
                        <v-list-item-subtitle class="text-body-1 text-black">{{ selectedItem.room || '-' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    <v-list-item>
                        <template v-slot:prepend><v-icon color="orange">mdi-note-text</v-icon></template>
                        <v-list-item-title>ໝາຍເຫດ</v-list-item-title>
                        <v-list-item-subtitle>{{ selectedItem.note || 'ບໍ່ມີ' }}</v-list-item-subtitle>
                    </v-list-item>
                </v-list>
            </v-card-text>

            <v-card-actions class="pa-4 pt-0">
                <v-btn 
                    block 
                    variant="elevated" 
                    color="primary" 
                    size="large" 
                    prepend-icon="mdi-calendar-plus"
                    @click="addToGoogleCalendar(selectedItem)"
                >
                    ເພີ່ມລົງ Google Calendar
                </v-btn>
            </v-card-actions>
        </v-card>
      </v-dialog>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api, { getProfile } from '../../services/api'; // Import getProfile ເພື່ອດຶງຊື່

const loading = ref(true);
const schedules = ref([]);
const userProfile = ref(null);

const semesters = [
    { id: 1, title: 'ພາກຮຽນ 1' },
    { id: 2, title: 'ພາກຮຽນ 2' }
];
const selectedSemester = ref(1);

const detailDialog = ref(false);
const selectedItem = ref(null);

// Time Slots & Days (Structure ດຽວກັບ Admin/Teacher)
const timeSlots = [
    { start: '08:00', end: '08:50', isBreak: false },
    { start: '09:00', end: '09:50', isBreak: false },
    { start: '10:00', end: '10:50', isBreak: false },
    { start: '11:00', end: '11:50', isBreak: false },
    { start: '12:00', end: '13:00', isBreak: true, name: 'ພັກທ່ຽງ (Lunch)' },
    { start: '13:00', end: '13:50', isBreak: false },
    { start: '14:00', end: '14:50', isBreak: false },
    { start: '15:00', end: '15:50', isBreak: false },
];
// Backend returns string "Monday" or int "1"
const days = [
    { text: 'ຈັນ (Mon)', value: 'Monday', intVal: 1 },
    { text: 'ອັງຄານ (Tue)', value: 'Tuesday', intVal: 2 },
    { text: 'ພຸດ (Wed)', value: 'Wednesday', intVal: 3 },
    { text: 'ພະຫັດ (Thu)', value: 'Thursday', intVal: 4 },
    { text: 'ສຸກ (Fri)', value: 'Friday', intVal: 5 },
];

const fetchSchedule = async () => {
    loading.value = true;
    try {
        // ດຶງຊື່ນັກຮຽນມາໂຊຫົວເຈ້ຍ
        if(!userProfile.value) {
            const profileRes = await getProfile();
            userProfile.value = profileRes.data;
        }

        const res = await api.get(`/students/schedule?semester_id=${selectedSemester.value}`);
        schedules.value = res.data;
    } catch (error) {
        console.error("Error fetching schedule:", error);
    } finally {
        loading.value = false;
    }
};

// Helper: Match Schedule to Slot
const getSubject = (dayVal, startTime) => {
    return schedules.value.find(s => {
        // Handle both string days ("Monday") and int days (1)
        let dayMatch = false;
        const dayInt = parseInt(s.day_of_week);
        
        if (!isNaN(dayInt)) {
            // ຖ້າ Backend ສົ່ງມາເປັນເລກ (1=Mon)
            const targetDay = days.find(d => d.value === dayVal);
            dayMatch = targetDay && targetDay.intVal === dayInt;
        } else {
            // ຖ້າ Backend ສົ່ງມາເປັນ string ("Monday")
            dayMatch = s.day_of_week === dayVal;
        }
        
        return dayMatch && s.start_time === startTime;
    });
};

const handleSlotClick = (item) => {
    if (item) {
        selectedItem.value = item;
        detailDialog.value = true;
    }
};

const getSubjectColor = (subjectName) => {
    if (!subjectName) return '#757575';
    const name = subjectName.toLowerCase();
    if (name.includes('ຄະນິດ') || name.includes('math') || name.includes('ຟີຊິກ') || name.includes('ເຄມີ')) return '#1E88E5'; 
    if (name.includes('ພາສາ') || name.includes('ວັນນະຄະດີ') || name.includes('english')) return '#E53935'; 
    if (name.includes('ປະຫວັດ') || name.includes('ພູມສາດ') || name.includes('ພົນລະເມືອງ')) return '#FB8C00'; 
    if (name.includes('ພະລະ') || name.includes('ສິລະປະ')) return '#43A047'; 
    if (name.includes('ict') || name.includes('ຄອມພິວເຕີ')) return '#8E24AA'; 
    return '#546E7A'; // Default
};

const getDayText = (dayValOrInt) => {
    // Try finding by string value
    let d = days.find(x => x.value === dayValOrInt);
    // If not found, try finding by int value
    if (!d && !isNaN(parseInt(dayValOrInt))) {
        d = days.find(x => x.intVal === parseInt(dayValOrInt));
    }
    return d ? d.text : dayValOrInt;
};

const formatTime = (timeStr) => timeStr ? timeStr.substring(0, 5) : '';

const addToGoogleCalendar = (item) => {
    const now = new Date();
    const currentDay = now.getDay(); 
    
    // Convert day to int index (0=Sun, 1=Mon...)
    let targetDay = parseInt(item.day_of_week);
    if(isNaN(targetDay)) {
        const dayMap = { 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7 };
        targetDay = dayMap[item.day_of_week] || 1;
    }
    const jsDay = targetDay === 7 ? 0 : targetDay;

    let daysUntil = (jsDay + 7 - currentDay) % 7;
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

    const title = `ຮຽນ: ${item.subject_name}`;
    const details = `ຄູ: ${item.teacher_name || '-'}\nຫ້ອງ: ${item.room || '-'}`;
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&dates=${formatGCalDate(startDate)}/${formatGCalDate(endDate)}&details=${encodeURIComponent(details)}&location=${encodeURIComponent(item.room || '')}&recur=RRULE:FREQ=WEEKLY`;
    window.open(url, '_blank');
};

const printSchedule = () => {
    window.print();
};

onMounted(fetchSchedule);
</script>

<style scoped>
/* CSS Grid ຕາຕະລາງ */
.timetable-container { overflow-x: auto; border: 1px solid #ddd; border-radius: 8px; padding: 1px; }
.timetable-wrapper { display: grid; grid-template-columns: 100px repeat(5, 1fr); gap: 1px; background-color: #ddd; min-width: 800px; }
.time-header, .day-header, .time-col, .slot-cell { background-color: white; padding: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.day-header { font-weight: bold; background-color: #E3F2FD; color: #1565C0; }
.time-col { background-color: #FAFAFA; }
.slot-cell { min-height: 80px; position: relative; cursor: pointer; transition: 0.2s; }
.slot-cell:hover:not(.has-subject):not(.break-time) { background-color: #E0F7FA; }

/* ບັດວິຊາ */
.subject-card { width: 100%; height: 100%; color: white; border-radius: 4px; padding: 4px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2); font-size: 0.85rem; }
.subject-name { font-weight: bold; line-height: 1.2; margin-bottom: 2px; }
.teacher-name { font-size: 0.75rem; opacity: 0.95; }
.room-name { font-size: 0.7rem; font-style: italic; opacity: 0.9; }

.break-time { background-color: #F5F5F5; cursor: default; font-style: italic; font-size: 0.8rem; color: #9E9E9E; }
.print-header, .print-footer { display: none; }
</style>

<style>
/* Print Styles */
@media print {
    .v-navigation-drawer, .v-app-bar, .v-toolbar, .print-hide, .v-overlay, .v-btn { display: none !important; }
    body, html, #app, .v-application, .v-main { width: 100% !important; height: auto !important; margin: 0 !important; padding: 0 !important; background: white !important; overflow: visible !important; }
    .v-main { padding-top: 0 !important; padding-left: 0 !important; }
    .timetable-container { border: none !important; width: 100% !important; overflow: visible !important; }
    .timetable-wrapper { min-width: 0 !important; width: 100% !important; gap: 0 !important; background-color: transparent !important; border: 2px solid black !important; }
    .day-header, .time-col, .slot-cell { border: 1px solid black !important; background-color: white !important; color: black !important; page-break-inside: avoid; }
    .subject-card { box-shadow: none !important; border: none !important; background-color: transparent !important; color: black !important; padding: 0 !important; }
    .subject-name { font-size: 10pt; text-decoration: underline; }
    .print-header, .print-footer { display: block !important; }
    @page { size: A4 landscape; margin: 1cm; }
}
</style>