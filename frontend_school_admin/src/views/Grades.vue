<template>
  <v-container>
    <v-card elevation="2" class="ma-2" rounded="xl">
      <v-card-title class="bg-primary text-white py-4 d-flex align-center">
        <v-icon icon="mdi-clipboard-list-outline" start></v-icon>
        <span>ຈັດການຄະແນນ</span>
        <v-spacer></v-spacer>
        
        <v-chip :color="isLocked ? 'amber-darken-3' : 'success'" variant="flat" size="small" class="ml-2">
          <v-icon start :icon="isLocked ? 'mdi-lock' : 'mdi-lock-open-variant'"></v-icon>
          {{ lockReason }}
        </v-chip>

        <v-btn 
            v-if="isAdminOrHead"
            variant="tonal" 
            :color="manualLockStatus ? 'error' : 'white'" 
            size="small" 
            class="ml-2"
            :prepend-icon="manualLockStatus ? 'mdi-lock-off' : 'mdi-lock-plus'"
            @click="toggleAdminLock"
            :loading="togglingLock"
        >
            {{ manualLockStatus ? 'Auto' : 'ປົດລັອກພິເສດ' }}
        </v-btn>

        <v-btn 
            variant="elevated" 
            color="indigo-lighten-5" 
            class="ml-2 text-primary font-weight-bold"
            size="small"
            prepend-icon="mdi-file-chart-outline"
            @click="goToReport"
        >
            ສະຫຼຸບຜົນການຮຽນ
        </v-btn>

      </v-card-title>

      <v-card-text class="mt-4">
        <v-row class="mb-2" align="center">
          <v-col cols="12" md="3">
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

          <v-col cols="12" md="3">
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

          <v-col cols="12" md="3">
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

          <v-col cols="12" md="3">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="ຄົ້ນຫາ (ຊື່/ລະຫັດ)"
              single-line
              hide-details
              density="compact"
              variant="outlined"
              clearable
            ></v-text-field>
          </v-col>

          <v-col v-if="isLocked" cols="12" md="12">
            <v-alert type="warning" density="compact" variant="tonal" icon="mdi-alert" class="mb-0">
               {{ lockReason }} - ບໍ່ສາມາດແກ້ໄຂໄດ້.
            </v-alert>
          </v-col>
        </v-row>

        <div class="d-flex gap-2 mb-2 justify-end" v-if="!isLocked && students.length > 0">
           <v-btn 
             color="primary" 
             variant="tonal" 
             prepend-icon="mdi-format-paint"
             @click="openBulkDialog"
           >
             {{ selected.length > 0 ? `ໃສ່ຄະແນນໃຫ້ ${selected.length} ຄົນທີ່ເລືອກ` : 'ໃສ່ຄະແນນລວດດຽວ (ທຸກຄົນ)' }}
           </v-btn>
        </div>

        <v-divider class="mb-4"></v-divider>

        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="students"
          :loading="loading"
          :search="search"
          show-select
          return-object
          class="elevation-0 border rounded-lg overflow-hidden cursor-pointer"
          items-per-page="-1"
          height="600px" 
          fixed-header
          hover
          @click:row="openEditDialog"
          no-data-text="⚠️ ບໍ່ພົບຂໍ້ມູນນັກຮຽນ"
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
              @keydown.enter="$event.target.blur()"
              @click.stop
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
              @keydown.enter="$event.target.blur()"
              @click.stop
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
              @keydown.enter="$event.target.blur()"
              @click.stop
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
              @keydown.enter="$event.target.blur()"
              @click.stop
            ></v-text-field>
          </template>

          <template v-slot:item.total_score="{ item }">
            <v-chip :color="item.total_score >= 50 ? 'success' : 'deep-orange'" variant="tonal" class="font-weight-bold">
              {{ item.total_score ? item.total_score.toFixed(2) : '0.00' }}
            </v-chip>
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-history" size="small" variant="text" color="primary" @click.stop="viewLogs(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>

      <v-dialog v-model="bulkDialog" max-width="400">
        <v-card rounded="xl">
          <v-card-title class="bg-primary text-white">
            <v-icon start>mdi-format-paint</v-icon> ໃສ່ຄະແນນລວດດຽວ
          </v-card-title>
          <v-card-text class="pt-4">
            <p class="mb-4 text-body-2 text-grey-darken-1">
              {{ selected.length > 0 
                  ? `ກຳລັງຈະໃສ່ຄະແນນໃຫ້ ${selected.length} ຄົນທີ່ຖືກເລືອກ.` 
                  : 'ກຳລັງຈະໃສ່ຄະແນນໃຫ້ "ທຸກຄົນ" ໃນຫ້ອງ.' 
              }}
            </p>
            
            <v-select
              v-model="bulkType"
              :items="[
                { title: 'ຄະແນນມາຮຽນ (Attendance)', value: 'ATTENDANCE' },
                { title: 'ຄະແນນວຽກບ້ານ/ເສັງຍ່ອຍ (Homework)', value: 'HOMEWORK' },
                { title: 'ຄະແນນກາງພາກ (Midterm)', value: 'MIDTERM' },
                { title: 'ຄະແນນທ້າຍພາກ (Final)', value: 'FINAL' }
              ]"
              label="ເລືອກປະເພດຄະແນນ"
              variant="outlined"
            ></v-select>

            <v-text-field
              v-model.number="bulkValue"
              label="ຄະແນນທີ່ຕ້ອງການໃສ່"
              type="number"
              variant="outlined"
              auto-focus
            ></v-text-field>
          </v-card-text>
          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="bulkDialog = false">ຍົກເລີກ</v-btn>
            <v-btn 
              color="primary" 
              variant="elevated" 
              @click="executeBulkFill" 
              :disabled="!bulkType || bulkValue === ''"
            >
              ບັນທຶກ
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="editDialog" max-width="500px" persistent>
        <v-card rounded="xl">
          <v-card-title class="bg-primary text-white d-flex align-center">
             <v-icon start>mdi-account-edit</v-icon>
             ແກ້ໄຂຄະແນນ
             <v-spacer></v-spacer>
             <v-btn icon="mdi-close" variant="text" density="compact" @click="editDialog = false"></v-btn>
          </v-card-title>

          <v-card-text class="pt-4">
             <div class="text-center mb-4">
                <h3 class="text-h6 font-weight-bold">{{ editingStudent.full_name }}</h3>
                <span class="text-caption text-grey">ລະຫັດ: {{ editingStudent.student_code }}</span>
             </div>

             <v-row>
                <v-col cols="6">
                   <v-text-field 
                      v-model.number="editingStudent.attendance_score" 
                      label="ມາຮຽນ (10)" type="number" variant="outlined" 
                      :disabled="isLocked" auto-focus
                   ></v-text-field>
                </v-col>
                <v-col cols="6">
                   <v-text-field 
                      v-model.number="editingStudent.homework_score" 
                      label="ວຽກບ້ານ/ເສັງຍ່ອຍ (20)" type="number" variant="outlined"
                      :disabled="isLocked"
                   ></v-text-field>
                </v-col>
                <v-col cols="6">
                   <v-text-field 
                      v-model.number="editingStudent.midterm_score" 
                      label="ກາງພາກ (30)" type="number" variant="outlined"
                      :disabled="isLocked"
                   ></v-text-field>
                </v-col>
                <v-col cols="6">
                   <v-text-field 
                      v-model.number="editingStudent.final_score" 
                      label="ທ້າຍພາກ (40)" type="number" variant="outlined"
                      :disabled="isLocked"
                   ></v-text-field>
                </v-col>
             </v-row>

             <v-alert color="info" variant="tonal" class="mt-2 text-center">
                <strong>ຄະແນນລວມ: {{ calculateTotal(editingStudent).toFixed(2) }}</strong>
             </v-alert>
          </v-card-text>

          <v-card-actions class="pa-4">
             <v-spacer></v-spacer>
             <v-btn variant="text" color="grey" @click="editDialog = false">ຍົກເລີກ</v-btn>
             <v-btn variant="elevated" color="primary" @click="saveDialog" :loading="savingDialog" :disabled="isLocked">
                ບັນທຶກການແກ້ໄຂ
             </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router'; 
import { getClassGrades, updateGrade, getClasses, getLockStatus, toggleClassLock } from '../services/api'; 
import GradeAuditLogs from './GradeAuditLogs.vue';

const router = useRouter(); 
const students = ref([]);
const loading = ref(false);
const search = ref('');
const selected = ref([]); // ✅ ເກັບລາຍຊື່ນັກຮຽນທີ່ຖືກເລືອກ

// Classes & Month
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
const selectedMonth = ref(9); 

// Hybrid Lock States
const isLocked = ref(false);
const manualLockStatus = ref(false);
const lockReason = ref('ກຳລັງເປີດໃຫ້ປ້ອນ');
const togglingLock = ref(false);

// Subject State
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

// Edit Dialog States
const editDialog = ref(false);
const savingDialog = ref(false);
const editingStudent = ref({});

// Bulk Fill States
const bulkDialog = ref(false);
const bulkType = ref('ATTENDANCE'); 
const bulkValue = ref(10); 

// Audit & Updates States
const reasonDialog = ref(false);
const reasonText = ref('');
const oldValue = ref(null);
const pendingPayload = ref(null);
const activeItem = ref(null);
const activeField = ref(null);

const logsDialog = ref(false);
const activeLogStudentId = ref(null);

// Updated Headers to show max scores
const headers = [
  { title: 'ລະຫັດ', key: 'student_code' },
  { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name', width: '200px' },
  { title: 'ມາຮຽນ (10)', key: 'ATTENDANCE', align: 'center' },
  { title: 'ວຽກບ້ານ/ເສັງຍ່ອຍ (20)', key: 'HOMEWORK', align: 'center' },
  { title: 'ກາງພາກ (30)', key: 'midterm_score', align: 'center' },
  { title: 'ທ້າຍພາກ (40)', key: 'final_score', align: 'center' },
  { title: 'ລວມ', key: 'total_score', align: 'center' },
  { title: 'ປະຫວັດ', key: 'actions', sortable: false, align: 'center' },
];

const isAdminOrHead = computed(() => {
    const role = localStorage.getItem('role');
    return role === 'admin' || role === 'head_teacher';
});

// --- FUNCTIONS ---

// ✅ Function to Navigate to Report
const goToReport = () => {
  const role = localStorage.getItem('role');
  const prefix = role === 'head_teacher' ? 'head' : role; 
  router.push(`/${prefix}/reports/semester`);
};

const fetchClasses = async () => {
    try {
        const res = await getClasses();
        classes.value = res.data;
        if (classes.value.length > 0) {
            selectedClass.value = classes.value[0].id; 
            fetchData();
        }
    } catch (error) {
        console.error("Error fetching classes:", error);
    }
};

const fetchData = async () => {
  if (!selectedClass.value) return;

  loading.value = true;
  selected.value = []; // Reset selected rows
  try {
    // 1. Get Grades
    const res = await getClassGrades(selectedClass.value, selectedMonth.value, selectedSubject.value);
    students.value = res.data;
    
    // 2. Get Lock Status
    try {
        const lockRes = await getLockStatus(selectedClass.value);
        manualLockStatus.value = lockRes.data.is_manual_locked;
    } catch (e) {
        manualLockStatus.value = false;
    }

    // 3. Calc Logic
    calculateHybridLock(selectedMonth.value);

  } catch (error) { 
    console.error("Error loading grades:", error); 
  }
  loading.value = false;
};

const calculateHybridLock = (monthId) => {
    // ✅ Logic ໃໝ່: ຖ້າ Admin ເປີດ Override (manualLockStatus = true) ໃຫ້ "ປົດລັອກ"
    if (manualLockStatus.value === true) {
        isLocked.value = false; 
        lockReason.value = "ປົດລັອກ";
        return;
    }

    // ຖ້າ Admin ບໍ່ໄດ້ປົດລັອກ -> ໃຊ້ Auto Lock ຕາມວັນທີ
    const now = new Date();
    const currentMonth = now.getMonth() + 1;
    const currentDay = now.getDate();

    if (currentMonth === 1 && monthId === 12) {
        if (currentDay <= 5) {
             isLocked.value = false;
             lockReason.value = "🟢 ເປີດ (ຊ່ວງຜ່ອນຜັນປີໃໝ່)";
        } else {
             isLocked.value = true;
             lockReason.value = "🔒 ໝົດເຂດແກ້ໄຂ (Auto)";
        }
        return;
    }

    if (monthId < currentMonth) {
        isLocked.value = true;
        lockReason.value = "ໝົດເຂດ";
    } else {
        isLocked.value = false;
        lockReason.value = "ເປີດ";
    }
};

const toggleAdminLock = async () => {
    if (!selectedClass.value) return;
    togglingLock.value = true;
    try {
        const res = await toggleClassLock(selectedClass.value);
        manualLockStatus.value = res.data.is_locked;
        calculateHybridLock(selectedMonth.value);
    } catch (error) {
        alert("Error updating lock status");
    }
    togglingLock.value = false;
};

// Open Bulk Dialog
const openBulkDialog = () => {
    bulkDialog.value = true;
    bulkValue.value = 10; 
};

// ✅ Execute Bulk Fill with Selection Support
const executeBulkFill = async () => {
  if (isLocked.value) return;
  
  // ຖ້າມີການເລືອກ Checkbox ໃຫ້ໃຊ້ກຸ່ມນັ້ນ, ຖ້າບໍ່ມີ ໃຫ້ໃຊ້ທຸກຄົນ
  const targets = selected.value.length > 0 ? selected.value : students.value;
  
  loading.value = true;
  bulkDialog.value = false;

  for (const stu of targets) {
      if (bulkType.value === 'ATTENDANCE') stu.attendance_score = bulkValue.value;
      if (bulkType.value === 'HOMEWORK') stu.homework_score = bulkValue.value;
      if (bulkType.value === 'MIDTERM') stu.midterm_score = bulkValue.value;
      if (bulkType.value === 'FINAL') stu.final_score = bulkValue.value;
      
      try {
        await updateGrade({
            student_id: stu.student_id,
            class_id: selectedClass.value,
            month_id: selectedMonth.value,
            subject_name: selectedSubject.value,
            score_type: bulkType.value,
            score_value: bulkValue.value
        });
      } catch (err) {
          console.error(`Failed to update student ${stu.student_code}`);
      }
  }
  
  await fetchData();
  selected.value = []; // Clear selection
  loading.value = false;
};

// Popup Logic
const openEditDialog = (event, { item }) => {
    editingStudent.value = { ...item }; 
    editDialog.value = true;
};

const calculateTotal = (stu) => {
    return (parseFloat(stu.attendance_score) || 0) +
           (parseFloat(stu.homework_score) || 0) +
           (parseFloat(stu.midterm_score) || 0) +
           (parseFloat(stu.final_score) || 0);
};

const saveDialog = async () => {
    if (isLocked.value) return;
    savingDialog.value = true;
    
    const stu = editingStudent.value;
    
    try {
        const types = ['ATTENDANCE', 'HOMEWORK', 'MIDTERM', 'FINAL'];
        const values = [stu.attendance_score, stu.homework_score, stu.midterm_score, stu.final_score];

        for (let i = 0; i < types.length; i++) {
             await updateGrade({
                student_id: stu.student_id,
                class_id: selectedClass.value,
                month_id: selectedMonth.value,
                subject_name: selectedSubject.value,
                score_type: types[i],
                score_value: parseFloat(values[i]) || 0
            });
        }

        await fetchData(); 
        editDialog.value = false;
        
    } catch (error) {
        alert("ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ");
    }
    savingDialog.value = false;
};

const setOldValue = (val) => { oldValue.value = val || 0; };

const handleSave = async (item, type, newValue) => {
  if (isLocked.value) return;
  const val = parseFloat(newValue) || 0;
  if (val === oldValue.value) return;

  const payload = {
    student_id: item.student_id,
    class_id: selectedClass.value, 
    month_id: selectedMonth.value,
    subject_name: selectedSubject.value,
    score_type: type,
    score_value: val
  };

  if (oldValue.value !== 0) {
    pendingPayload.value = payload;
    activeItem.value = item;
    if (type === 'ATTENDANCE') activeField.value = 'attendance_score';
    if (type === 'HOMEWORK') activeField.value = 'homework_score';
    if (type === 'MIDTERM') activeField.value = 'midterm_score';
    if (type === 'FINAL') activeField.value = 'final_score';
    reasonDialog.value = true;
  } else {
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
    fetchData();
  }
};

const viewLogs = (item) => {
  activeLogStudentId.value = item.student_id;
  logsDialog.value = true;
};

onMounted(fetchClasses);
</script>

<style scoped>
.score-input { width: 90px; margin: 0 auto; }
.score-input :deep(input) { text-align: center; font-weight: bold; color: #1976D2; }

/* Pointer for clickable rows */
.cursor-pointer :deep(tbody tr) {
    cursor: pointer;
}

:deep(tbody tr:hover) {
    background-color: #f5f5f5 !important;
}
</style>