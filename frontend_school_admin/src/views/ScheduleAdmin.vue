<template>
  <v-container fluid class="pa-0 pa-md-4">
    <v-card elevation="2" rounded="lg" class="h-100">
      <v-card-title class="d-flex flex-wrap justify-space-between align-center py-4 px-4 bg-teal-darken-1 text-white print-hide">
        <div class="text-h6 d-flex align-center">
          <v-icon icon="mdi-calendar-clock" start></v-icon>
          ຈັດການຕາຕະລາງຮຽນ
        </div>
        <v-btn 
            color="white" 
            variant="elevated" 
            class="text-teal-darken-2 font-weight-bold" 
            prepend-icon="mdi-printer" 
            @click="printSchedule" 
            :disabled="!selectedClass"
        >
            ພິມຕາຕະລາງ
        </v-btn>
      </v-card-title>

      <v-card-text class="mt-4">
        <v-row align="center" class="mb-4 print-hide">
          
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedClass"
              :items="classes"
              item-title="name"
              item-value="id"
              label="ເລືອກຫ້ອງຮຽນ"
              variant="solo-filled"
              density="comfortable"
              prepend-inner-icon="mdi-google-classroom"
              hide-details
              @update:model-value="fetchSchedule"
              class="rounded-lg"
            ></v-select>
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="selectedSemester"
              :items="semesters"
              item-title="title"
              item-value="id"
              label="ເລືອກພາກຮຽນ"
              variant="solo-filled"
              density="comfortable"
              prepend-inner-icon="mdi-calendar-range"
              hide-details
              @update:model-value="fetchSchedule"
              class="rounded-lg"
            ></v-select>
          </v-col>

          <v-col cols="12" md="5">
             <div v-if="selectedClass" class="d-flex gap-2 align-center">
                <v-chip color="teal" variant="flat">
                    ຫ້ອງ: {{ getClassName(selectedClass) }} | ພາກຮຽນທີ {{ selectedSemester }}
                </v-chip>
            </div>
          </v-col>
        </v-row>

        <v-divider class="mb-6 print-hide"></v-divider>

        <div v-if="selectedClass" class="timetable-container" id="printable-area">
            <div class="print-header text-center mb-4">
                <div class="text-h4 font-weight-bold mb-2">ຕາຕະລາງຮຽນ</div>
                <div class="text-h6">
                    ຫ້ອງ: {{ getClassName(selectedClass) }} 
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
                        @click="handleSlotClick(day.value, slot)"
                    >
                        <div v-if="getSubject(day.value, slot.start)" class="subject-card" :style="{ backgroundColor: getSubjectColor(getSubject(day.value, slot.start).subject_name) }">
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
                            <v-btn icon="mdi-close" size="x-small" variant="flat" color="error" class="delete-btn print-hide" @click.stop="confirmDelete(getSubject(day.value, slot.start))"></v-btn>
                        </div>
                        <div v-else-if="!slot.isBreak" class="empty-slot print-hide">
                            <v-icon icon="mdi-plus" color="grey-lighten-2"></v-icon>
                        </div>
                        <div v-else class="break-text text-grey-lighten-1">{{ slot.name }}</div>
                    </div>
                </template>
            </div>

            <div class="print-footer mt-10">
                <div class="d-flex justify-space-around">
                    <div class="text-center">
                        <p><strong>ອຳນວຍການ</strong></p>
                        <br><br><br>
                        <p>................................</p>
                    </div>
                    <div class="text-center">
                        <p><strong>ວິຊາການ</strong></p>
                        <br><br><br>
                        <p>................................</p>
                    </div>
                    <div class="text-center">
                        <p><strong>ຄູປະຈຳຫ້ອງ</strong></p>
                        <br><br><br>
                        <p>................................</p>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="text-center py-10 text-grey print-hide">
            <v-icon icon="mdi-calendar-blank" size="64" color="grey-lighten-2"></v-icon>
            <div class="mt-2">ກະລຸນາເລືອກຫ້ອງຮຽນ ແລະ ພາກຮຽນ ເພື່ອສະແດງຕາຕະລາງ</div>
        </div>
      </v-card-text>

      <v-dialog v-model="dialog" max-width="400px">
         <v-card rounded="xl">
            <v-card-title class="bg-teal text-white">ເພີ່ມວິຊາຮຽນ (ພາກຮຽນ {{ selectedSemester }})</v-card-title>
            <v-card-text class="pt-4">
                <div class="mb-4 text-subtitle-1">
                    <strong>ວັນ:</strong> {{ getDayText(newItem.day_of_week) }} <br>
                    <strong>ເວລາ:</strong> {{ newItem.start_time }} - {{ newItem.end_time }}
                </div>
                <v-select 
                    v-model="newItem.subject_name" 
                    :items="subjectsList" 
                    label="ວິຊາຮຽນ" 
                    variant="outlined"
                    prepend-inner-icon="mdi-book-open-variant"
                ></v-select>
                <v-select 
                    v-model="newItem.teacher_name" 
                    :items="teachersList" 
                    item-title="full_name" 
                    item-value="full_name" 
                    label="ຄູສອນ" 
                    variant="outlined"
                    prepend-inner-icon="mdi-human-male-board"
                ></v-select>
                <v-text-field 
                    v-model="newItem.room" 
                    label="ຫ້ອງຮຽນ (Optional)" 
                    variant="outlined"
                    prepend-inner-icon="mdi-door"
                ></v-text-field>
            </v-card-text>
            <v-card-actions class="justify-end px-4 pb-4">
                <v-btn variant="text" @click="dialog = false">ຍົກເລີກ</v-btn>
                <v-btn color="teal" variant="elevated" @click="saveSchedule" :loading="saving">ບັນທຶກ</v-btn>
            </v-card-actions>
         </v-card>
      </v-dialog>
      
      <v-dialog v-model="deleteDialog" max-width="350">
         <v-card rounded="xl">
            <v-card-title class="bg-red text-white">ຢືນຢັນການລຶບ</v-card-title>
            <v-card-text class="pt-4">
                ທ່ານຕ້ອງການລຶບວິຊາ <strong>{{ deletingItem?.subject_name }}</strong> ອອກບໍ່?
            </v-card-text>
            <v-card-actions class="justify-end">
                <v-btn variant="text" @click="deleteDialog = false">ຍົກເລີກ</v-btn>
                <v-btn color="red" variant="elevated" @click="executeDelete" :loading="deleting">ລຶບອອກ</v-btn>
            </v-card-actions>
         </v-card>
      </v-dialog>

      <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top" timeout="3000">
        {{ snackbar.message }}
      </v-snackbar>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api, { 
    getClasses, 
    createSchedule, 
    deleteSchedule,
    getTeachersForDropdown
} from '../services/api';

const classes = ref([]);
const selectedClass = ref(null);
const schedules = ref([]);
const teachersList = ref([]); 

const semesters = [
    { id: 1, title: 'ພາກຮຽນ 1 (Semester 1)' },
    { id: 2, title: 'ພາກຮຽນ 2 (Semester 2)' }
];
const selectedSemester = ref(1);

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
const days = [
    { text: 'ຈັນ (Mon)', value: 'Monday' },
    { text: 'ອັງຄານ (Tue)', value: 'Tuesday' },
    { text: 'ພຸດ (Wed)', value: 'Wednesday' },
    { text: 'ພະຫັດ (Thu)', value: 'Thursday' },
    { text: 'ສຸກ (Fri)', value: 'Friday' },
];

// ✅ 1. ອັບເດດລາຍຊື່ວິຊາໃຫ້ເປັນມາດຕະຖານ
const subjectsList = [
    'ພາສາລາວ (Lao Language)', 'ວັນນະຄະດີ (Literature)', 'ພາສາອັງກິດ (English)', 'ພາສາຝຣັ່ງ (French)', 'ພາສາຈີນ (Chinese)',
    'ຄະນິດສາດ (Mathematics)', 'ວິທະຍາສາດທຳມະຊາດ (Natural Sciences)', 'ຟີຊິກສາດ (Physics)', 'ເຄມີສາດ (Chemistry)', 'ຊີວະສາດ (Biology)',
    'ປະຫວັດສາດ (History)', 'ພູມສາດ (Geography)', 'ສຶກສາພົນລະເມືອງ (Civic Education)', 'ປ້ອງກັນຊາດ-ປ້ອງກັນຄວາມສະຫງົບ (National Defense)',
    'ICT/ຄອມພິວເຕີ (Computer)', 'ເຕັກໂນໂລຊີ (Technology)', 'ສິລະປະສຶກສາ (Arts)', 'ຫັດຖະກຳ (Handicrafts)',
    'ພະລະສຶກສາ (Physical Education)', 'ແນະແນວ/ກິດຈະກຳຫ້ອງ (Guidance)', 'ກິດຈະກຳນອກຫຼັກສູດ (Extracurricular)'
];

const dialog = ref(false);
const deleteDialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const newItem = ref({});
const deletingItem = ref(null);
const snackbar = ref({ show: false, message: '', color: 'success' });

const init = async () => {
    try {
        const classRes = await getClasses();
        classes.value = classRes.data;
        const teacherRes = await getTeachersForDropdown();
        teachersList.value = teacherRes.data;
    } catch (e) {}
};

// ==========================================
// ✅ ຈຸດສຳຄັນ: ຕັດວິນາທີອອກ (08:00:00 -> 08:00)
// ==========================================
const fetchSchedule = async () => {
    if (!selectedClass.value) return;
    try {
        const res = await api.get(`/lms/schedules/${selectedClass.value}?semester_id=${selectedSemester.value}`);
        
        // ແປງຂໍ້ມູນກ່ອນເກັບໃສ່ state
        schedules.value = res.data.map(item => ({
            ...item,
            // ໃຊ້ substring(0, 5) ເພື່ອຕັດ :00 ທາງຫຼັງອອກ
            start_time: item.start_time.substring(0, 5),
            end_time: item.end_time.substring(0, 5)
        }));

    } catch (error) {
        console.error("Error fetching schedule:", error);
        schedules.value = [];
    }
};

const getSubject = (day, startTime) => {
    return schedules.value.find(s => s.day_of_week === day && s.start_time === startTime);
};

const handleSlotClick = (day, slot) => {
    if (slot.isBreak) return;
    const existing = getSubject(day, slot.start);
    if (!existing) {
        newItem.value = {
            class_id: selectedClass.value,
            semester_id: selectedSemester.value,
            day_of_week: day,
            start_time: slot.start,
            end_time: slot.end,
            subject_name: '',
            teacher_name: '',
            room: ''
        };
        dialog.value = true;
    }
};

const saveSchedule = async () => {
    saving.value = true;
    try {
        await createSchedule(newItem.value);
        snackbar.value = { show: true, message: 'ບັນທຶກສຳເລັດ', color: 'success' };
        dialog.value = false;
        fetchSchedule(); // ດຶງຂໍ້ມູນໃໝ່ຫຼັງບັນທຶກ
    } catch (error) {
        snackbar.value = { show: true, message: 'ຊ່ອງນີ້ມີວິຊາຮຽນແລ້ວ', color: 'error' };
    } finally {
        saving.value = false;
    }
};

const confirmDelete = (item) => { deletingItem.value = item; deleteDialog.value = true; };
const executeDelete = async () => {
    deleting.value = true;
    try { await deleteSchedule(deletingItem.value.id); deleteDialog.value = false; fetchSchedule(); }
    catch(e) { snackbar.value = {show:true, message:'Error', color:'error'}; }
    finally { deleting.value = false; }
};

// ✅ 2. ອັບເດດລະບົບສີແຍກຕາມໝວດວິຊາ
const getSubjectColor = (subjectName) => {
    if (!subjectName) return '#757575';
    const name = subjectName.toLowerCase();
    if (name.includes('ຄະນິດ') || name.includes('math') || name.includes('ຟີຊິກ')) return '#1E88E5'; 
    if (name.includes('ພາສາ') || name.includes('english')) return '#E53935'; 
    if (name.includes('ປະຫວັດ') || name.includes('ພູມສາດ')) return '#FB8C00'; 
    if (name.includes('ພະລະ') || name.includes('ສິລະປະ')) return '#43A047'; 
    if (name.includes('ict') || name.includes('ຄອມ')) return '#8E24AA'; 
    return '#00ACC1';
};

const getClassName = (id) => classes.value.find(x => x.id === id)?.name || '';
const getDayText = (dayVal) => days.find(x => x.value === dayVal)?.text || dayVal;
const printSchedule = () => window.print();

onMounted(init);
</script>

<style scoped>
.timetable-container { overflow-x: auto; border: 1px solid #ddd; border-radius: 8px; padding: 1px; }
.timetable-wrapper { display: grid; grid-template-columns: 100px repeat(5, 1fr); gap: 1px; background-color: #ddd; min-width: 800px; }
.time-header, .day-header, .time-col, .slot-cell { background-color: white; padding: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.day-header { font-weight: bold; background-color: #E0F2F1; color: #00695C; }
.time-col { background-color: #FAFAFA; }
.slot-cell { min-height: 80px; position: relative; cursor: pointer; }
.slot-cell:hover:not(.has-subject):not(.break-time) { background-color: #E0F7FA; }
.subject-card { width: 100%; height: 100%; color: white; border-radius: 4px; padding: 4px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2); position: relative; font-size: 0.85rem; }
.subject-name { font-weight: bold; line-height: 1.2; margin-bottom: 2px; text-decoration: none; }
.teacher-name { font-size: 0.75rem; opacity: 0.95; }
.room-name { font-size: 0.7rem; font-style: italic; opacity: 0.9; }
.delete-btn { position: absolute; top: 2px; right: 2px; opacity: 0; transition: opacity 0.2s; }
.subject-card:hover .delete-btn { opacity: 1; }
.break-time { background-color: #F5F5F5; cursor: default; font-style: italic; font-size: 0.8rem; color: #9E9E9E; }
.print-header, .print-footer { display: none; }
</style>

<style>
@media print {
    .v-navigation-drawer, .v-app-bar, .v-toolbar, .print-hide, .v-overlay, .v-btn { display: none !important; }
    body, html, #app, .v-application, .v-main { width: 100% !important; height: auto !important; margin: 0 !important; padding: 0 !important; background: white !important; overflow: visible !important; }
    .v-main { padding-top: 0 !important; padding-left: 0 !important; }
    .timetable-container { border: none !important; width: 100% !important; overflow: visible !important; }
    .timetable-wrapper { min-width: 0 !important; width: 100% !important; gap: 0 !important; background-color: transparent !important; border: 2px solid black !important; }
    .day-header, .time-col, .slot-cell { border: 1px solid black !important; background-color: white !important; color: black !important; page-break-inside: avoid; }
    .subject-card { box-shadow: none !important; border: none !important; background-color: transparent !important; color: black !important; padding: 0 !important; }
    .subject-name { font-size: 10pt; text-decoration: underline; }
    .teacher-name { font-size: 9pt; }
    .print-header, .print-footer { display: block !important; }
    @page { size: A4 landscape; margin: 1cm; }
}
</style>