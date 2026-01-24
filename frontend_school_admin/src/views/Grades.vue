<template>
  <v-container>
    <v-card elevation="2" class="ma-2" rounded="xl">
      <v-card-title class="bg-primary text-white py-4 d-flex align-center">
        <v-icon icon="mdi-clipboard-list-outline" start></v-icon>
        <span>ຈັດການຄະແນນ (Grading System)</span>
        <v-spacer></v-spacer>
        <v-chip :color="isLocked ? 'amber-darken-3' : 'success'" variant="flat" size="small" class="ml-2">
          <v-icon start :icon="isLocked ? 'mdi-lock' : 'mdi-lock-open-variant'"></v-icon>
          {{ isLocked ? 'ລັອກຂໍ້ມູນແລ້ວ' : 'ກຳລັງເປີດໃຫ້ປ້ອນ' }}
        </v-chip>
      </v-card-title>

      <v-card-text class="mt-4">
        <v-row class="mb-2" align="center">
          
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedClass"
              :items="classes"
              item-title="name"
              item-value="id"
              label="ເລືອກຫ້ອງຮຽນ"
              variant="outlined"
              density="compact"
              hide-details
              prepend-inner-icon="mdi-google-classroom"
              @update:model-value="fetchData"
            ></v-select>
          </v-col>

          <v-col cols="12" md="4">
            <v-select
              v-model="selectedMonth"
              :items="months"
              item-title="name"
              item-value="id"
              label="ເລືອກປະຈຳເດືອນ"
              variant="outlined"
              density="compact"
              hide-details
              prepend-inner-icon="mdi-calendar"
              @update:model-value="fetchData"
            ></v-select>
          </v-col>

          <v-col cols="12" md="4">
            <v-select
                v-model="selectedSubject"
                :items="subjects"
                item-title="title"
                item-value="value"
                label="ເລືອກວິຊາຮຽນ"
                variant="outlined"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-book-open-page-variant"
                @update:model-value="fetchData"
            ></v-select>
          </v-col>

          <v-col v-if="isLocked" cols="12" md="4">
            <v-alert type="warning" density="compact" variant="tonal" icon="mdi-alert" class="mb-0">
              ຂໍ້ມູນຖືກລັອກ ບໍ່ສາມາດແກ້ໄຂໄດ້.
            </v-alert>
          </v-col>
        </v-row>

        <v-divider class="mb-4"></v-divider>

        <v-data-table
          :headers="headers"
          :items="students"
          :loading="loading"
          class="elevation-0 border rounded-lg overflow-hidden"
          items-per-page="-1"
          no-data-text="⚠️ ບໍ່ພົບຂໍ້ມູນນັກຮຽນໃນຫ້ອງນີ້ (ກະລຸນາກວດສອບການລົງທະບຽນ)"
        >
          <template v-slot:item.ATTENDANCE="{ item }">
            <v-text-field
              v-model.number="item.attendance_score"
              type="number"
              density="compact"
              variant="outlined"
              class="score-input"
              hide-details
              :disabled="isLocked"
              @focus="setOldValue(item.attendance_score)"
              @blur="handleSave(item, 'ATTENDANCE', item.attendance_score)"
            ></v-text-field>
          </template>

          <template v-slot:item.HOMEWORK="{ item }">
            <v-text-field
              v-model.number="item.homework_score"
              type="number"
              density="compact"
              variant="outlined"
              class="score-input"
              hide-details
              :disabled="isLocked"
              @focus="setOldValue(item.homework_score)"
              @blur="handleSave(item, 'HOMEWORK', item.homework_score)"
            ></v-text-field>
          </template>

          <template v-slot:item.midterm_score="{ item }">
            <v-text-field
              v-model.number="item.midterm_score"
              type="number"
              density="compact"
              variant="outlined"
              class="score-input"
              hide-details
              :disabled="isLocked"
              @focus="setOldValue(item.midterm_score)"
              @blur="handleSave(item, 'MIDTERM', item.midterm_score)"
            ></v-text-field>
          </template>
          
           <template v-slot:item.final_score="{ item }">
            <v-text-field
              v-model.number="item.final_score"
              type="number"
              density="compact"
              variant="outlined"
              class="score-input"
              hide-details
              :disabled="isLocked"
              @focus="setOldValue(item.final_score)"
              @blur="handleSave(item, 'FINAL', item.final_score)"
            ></v-text-field>
          </template>

          <template v-slot:item.total_score="{ item }">
            <v-chip :color="item.total_score >= 50 ? 'success' : 'deep-orange'" variant="tonal" class="font-weight-bold">
              {{ item.total_score ? item.total_score.toFixed(2) : '0.00' }}
            </v-chip>
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-history" size="small" variant="text" color="primary" @click="viewLogs(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>

      <v-dialog v-model="reasonDialog" max-width="450" persistent>
        <v-card rounded="xl">
          <v-card-title class="bg-amber-darken-2 text-white">
            <v-icon start>mdi-comment-question</v-icon> ຢືນຢັນການແກ້ໄຂ
          </v-card-title>
          <v-card-text class="pt-4">
            <p class="mb-4">ທ່ານກຳລັງປ່ຽນແປງຄະແນນ ({{ oldValue }} -> {{ pendingPayload?.score_value }}), ກະລຸນາລະບຸເຫດຜົນ:</p>
            <v-textarea v-model="reasonText" label="ເຫດຜົນ *" variant="outlined" rows="3" auto-focus></v-textarea>
          </v-card-text>
          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="cancelUpdate">ຍົກເລີກ</v-btn>
            <v-btn color="primary" variant="elevated" :disabled="!reasonText" @click="confirmUpdate">ບັນທຶກ</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="logsDialog" max-width="600" scrollable>
        <GradeAuditLogs v-if="activeLogStudentId" :student-id="activeLogStudentId" :month-id="selectedMonth" @close="logsDialog = false" />
      </v-dialog>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// 🔥 Import ຟັງຊັນທີ່ຈຳເປັນຈາກ API
import { getClassGrades, updateGrade, getClasses } from '../services/api'; 
// 🔥 Import Component ລູກສຳລັບເບິ່ງປະຫວັດ
import GradeAuditLogs from './GradeAuditLogs.vue';

const students = ref([]);
const loading = ref(false);

// 🔥 1. ຕົວແປ Classes ແລະ State
const classes = ref([]);
const selectedClass = ref(null);

const months = ref([
    { id: 9, name: 'ກັນຍາ (Sep)' },
    { id: 10, name: 'ຕຸລາ (Oct)' },
    { id: 11, name: 'ພະຈິກ (Nov)' },
    { id: 12, name: 'ທັນວາ (Dec)' },
    { id: 1, name: 'ມັງກອນ (Jan)' },
    { id: 2, name: 'ກຸມພາ (Feb)' },
]); 
const selectedMonth = ref(9); // Default ກັນຍາ
const isLocked = ref(false);


// ✅ NEW: Subject State & Options
const selectedSubject = ref('GENERAL');
const subjects = ref([
    { title: 'ທົ່ວໄປ (General)', value: 'GENERAL' },
    { title: 'ຄະນິດສາດ (Math)', value: 'MATH' },
    { title: 'ພາສາລາວ (Lao)', value: 'LAO' },
    { title: 'ພາສາອັງກິດ (English)', value: 'ENGLISH' },
    { title: 'ຟີຊິກ (Physics)', value: 'PHYSICS' },
    { title: 'ເຄມີ (Chemistry)', value: 'CHEMISTRY' },
    { title: 'ຊີວະ (Biology)', value: 'BIOLOGY' },
    { title: 'ປະຫວັດສາດ (History)', value: 'HISTORY' },
    { title: 'ພູມສາດ (Geography)', value: 'GEOGRAPHY' },
    { title: 'ສຶກສາພົນລະເມືອງ (Civics)', value: 'CIVICS' },
    { title: 'ICT / ຄອມພິວເຕີ', value: 'ICT' },
]);

// States for Audit Log & Updates
const reasonDialog = ref(false);
const reasonText = ref('');
const oldValue = ref(null);
const pendingPayload = ref(null);
const activeItem = ref(null);
const activeField = ref(null);

const logsDialog = ref(false);
const activeLogStudentId = ref(null);

const headers = [
  { title: 'ລະຫັດ', key: 'student_code' },
  { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name', width: '200px' },
  { title: 'ມາຮຽນ', key: 'ATTENDANCE', align: 'center' },
  { title: 'ວຽກບ້ານ', key: 'HOMEWORK', align: 'center' },
  { title: 'ກາງພາກ', key: 'midterm_score', align: 'center' },
  { title: 'ທ້າຍພາກ', key: 'final_score', align: 'center' },
  { title: 'ລວມ', key: 'total_score', align: 'center' },
  { title: 'ປະຫວັດ', key: 'actions', sortable: false, align: 'center' },
];

// 🔥 2. ໂຫຼດລາຍຊື່ຫ້ອງຮຽນກ່ອນ
const fetchClasses = async () => {
    try {
        const res = await getClasses();
        classes.value = res.data;
        if (classes.value.length > 0) {
            selectedClass.value = classes.value[0].id; // ເລືອກຫ້ອງທຳອິດ Auto
            fetchData(); // ໂຫຼດຄະແນນ
        }
    } catch (error) {
        console.error("Error fetching classes:", error);
    }
};

const fetchData = async () => {
  if (!selectedClass.value) return; // ຖ້າຍັງບໍ່ເລືອກຫ້ອງ ບໍ່ຕ້ອງໂຫຼດ

  loading.value = true;
  try {
    // ✅ NEW: Pass selectedSubject to API
    const res = await getClassGrades(selectedClass.value, selectedMonth.value, selectedSubject.value);
    students.value = res.data;
    // (Optional logic: ກວດສອບ lock ຈາກ API ຖ້າມີ)
    isLocked.value = false; 
  } catch (error) { 
    console.error("Error loading grades:", error); 
  }
  loading.value = false;
};

const setOldValue = (val) => { oldValue.value = val || 0; };

const handleSave = async (item, type, newValue) => {
  if (isLocked.value) return;
  const val = parseFloat(newValue) || 0;
  if (val === oldValue.value) return;

  const payload = {
    student_id: item.student_id,
    class_id: selectedClass.value, // 🔥 ໃຊ້ຫ້ອງທີ່ເລືອກ
    month_id: selectedMonth.value,
    subject_name: selectedSubject.value, // ✅ NEW: Include subject in payload
    score_type: type,
    score_value: val
  };

  // ຖ້າມີການແກ້ໄຂຄ່າ (ບໍ່ແມ່ນຄ່າ 0 ຕັ້ງແຕ່ຕົ້ນ) ໃຫ້ຖາມເຫດຜົນ
  if (oldValue.value !== 0) {
    pendingPayload.value = payload;
    activeItem.value = item;
    // Map field name ໃຫ້ຖືກຕ້ອງເພື່ອໃຊ້ຕອນ Cancel
    if (type === 'ATTENDANCE') activeField.value = 'attendance_score';
    if (type === 'HOMEWORK') activeField.value = 'homework_score';
    if (type === 'MIDTERM') activeField.value = 'midterm_score';
    if (type === 'FINAL') activeField.value = 'final_score';
    reasonDialog.value = true;
  } else {
    // ຖ້າເປັນຄ່າ 0 (ຄະແນນໃໝ່) ບັນທຶກເລີຍ
    executeSave(payload, item);
  }
};

const confirmUpdate = () => {
  const payload = { ...pendingPayload.value, reason: reasonText.value };
  executeSave(payload, activeItem.value);
  reasonDialog.value = false;
  reasonText.value = '';
};

const cancelUpdate = () => {
  // ກູ້ຄືນຄ່າເກົ່າ
  if(activeItem.value && activeField.value) {
      activeItem.value[activeField.value] = oldValue.value;
  }
  reasonDialog.value = false;
  reasonText.value = '';
};

const executeSave = async (payload, item) => {
  try {
    const res = await updateGrade(payload);
    item.total_score = res.data.total_score;
  } catch (error) {
    alert(error.response?.data?.detail || 'ເກີດຂໍ້ຜິດພາດ');
    // ຖ້າ Error ໃຫ້ໂຫຼດຂໍ້ມູນໃໝ່ເພື່ອ reset ຄ່າ
    fetchData();
  }
};

const viewLogs = (item) => {
  activeLogStudentId.value = item.student_id;
  logsDialog.value = true;
};

// 🔥 3. ເອີ້ນໃຊ້ fetchClasses ເມື່ອໂຫຼດໜ້າ
onMounted(fetchClasses);
</script>

<style scoped>
.score-input { width: 90px; margin: 0 auto; }
.score-input :deep(input) { text-align: center; font-weight: bold; color: #1976D2; }
</style>