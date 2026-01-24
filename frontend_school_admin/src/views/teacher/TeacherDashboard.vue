<template>
  <v-container fluid class="pa-4 bg-grey-lighten-5 h-100">
    
    <v-row align="center" class="mb-4">
      <v-col cols="12" md="8">
        <h2 class="text-h5 font-weight-bold text-primary">
          <v-icon start>mdi-teach</v-icon> Teacher Dashboard
        </h2>
        <div class="text-body-2 text-grey">ຈັດການຂໍ້ມູນການຮຽນ-ການສອນ ແລະ ນັກຮຽນຂອງທ່ານ</div>
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedClassId"
          :items="myClasses"
          item-title="name"
          item-value="id"
          label="ເລືອກຫ້ອງຮຽນ"
          variant="solo-filled"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-google-classroom"
          class="rounded-lg"
          @update:model-value="fetchStudents"
          :loading="loadingClasses"
          no-data-text="ທ່ານຍັງບໍ່ມີຫ້ອງຮຽນທີ່ຮັບຜິດຊອບ"
        ></v-select>
      </v-col>
    </v-row>

    <div v-if="loadingStudents" class="text-center py-10">
      <v-progress-circular indeterminate color="primary" size="50"></v-progress-circular>
      <div class="mt-2 text-grey">ກຳລັງໂຫຼດຂໍ້ມູນນັກຮຽນ...</div>
    </div>

    <div v-else-if="selectedClassId">
      
      <v-row class="mb-4">
        <v-col cols="12" sm="4">
          <v-card class="pa-4 rounded-xl" elevation="1">
            <div class="d-flex align-center">
              <v-avatar color="primary-lighten-5" class="text-primary" size="50">
                <v-icon>mdi-account-group</v-icon>
              </v-avatar>
              <div class="ml-3">
                <div class="text-caption text-grey">ນັກຮຽນທັງໝົດ</div>
                <div class="text-h5 font-weight-bold">{{ students.length }} ຄົນ</div>
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card class="pa-4 rounded-xl" elevation="1">
            <div class="d-flex align-center">
              <v-avatar color="success-lighten-5" class="text-success" size="50">
                <v-icon>mdi-calendar-check</v-icon>
              </v-avatar>
              <div class="ml-3">
                <div class="text-caption text-grey">ເຊັກຊື່ມື້ນີ້</div>
                <div class="text-h5 font-weight-bold">
                  {{ isTodayChecked ? 'ຮຽບຮ້ອຍ ✅' : 'ຍັງບໍ່ທັນເຊັກ ⚠️' }}
                </div>
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4" class="d-flex align-center justify-end">
             <v-btn 
                color="primary" 
                prepend-icon="mdi-plus-circle" 
                class="text-none font-weight-bold rounded-lg"
                height="50"
                block
                @click="dialogBehavior = true"
             >
                ໃຫ້ຄະແນນພຶດຕິກຳ (ດ່ວນ)
             </v-btn>
        </v-col>
      </v-row>

      <v-card elevation="2" rounded="lg" class="overflow-hidden">
        <v-tabs v-model="tab" bg-color="white" color="primary" grow>
          <v-tab value="students"><v-icon start>mdi-format-list-bulleted</v-icon> ລາຍຊື່ນັກຮຽນ</v-tab>
          <v-tab value="attendance"><v-icon start>mdi-calendar-edit</v-icon> ເຊັກຊື່ (Attendance)</v-tab>
          <v-tab value="behavior"><v-icon start>mdi-star-half-full</v-icon> ປະຫວັດຄະແນນພຶດຕິກຳ</v-tab>
        </v-tabs>

        <v-window v-model="tab" class="pa-4 bg-white">
          
          <v-window-item value="students">
            <v-data-table
              :headers="studentHeaders"
              :items="students"
              density="comfortable"
              hover
            >
              <template v-slot:item.full_name="{ item }">
                <div class="d-flex align-center py-2">
                  <v-avatar color="grey-lighten-3" size="36" class="mr-3">
                    <span class="font-weight-bold text-primary">{{ item.full_name.charAt(0) }}</span>
                  </v-avatar>
                  <div>
                    <div class="font-weight-bold">{{ item.full_name }}</div>
                    <div class="text-caption text-grey">{{ item.student_code }}</div>
                  </div>
                </div>
              </template>
              
              <template v-slot:item.parent="{ item }">
                 <div v-if="item.parent_phone">
                    <v-icon size="small" start>mdi-phone</v-icon> {{ item.parent_phone }}
                 </div>
                 <div v-else class="text-grey text-caption">-</div>
              </template>

              <template v-slot:item.points="{ item }">
                 <v-chip 
                    :color="item.total_merit_points >= 0 ? 'success' : 'error'" 
                    size="small" 
                    class="font-weight-bold"
                 >
                    {{ item.total_merit_points }} pts
                 </v-chip>
              </template>

              <template v-slot:item.actions="{ item }">
                 <v-btn size="small" variant="text" color="primary" icon="mdi-file-account" title="ເບິ່ງ Portfolio"></v-btn>
              </template>
            </v-data-table>
          </v-window-item>

          <v-window-item value="attendance">
             <div class="text-center py-10 text-grey">
                <v-icon size="64" class="mb-3">mdi-tools</v-icon>
                <div class="text-h6">ຟັງຊັນນີ້ກຳລັງພັດທະນາ</div>
                <div>(ຈະເພີ່ມໃນຂັ້ນຕອນຕໍ່ໄປ)</div>
             </div>
          </v-window-item>

          <v-window-item value="behavior">
             <div class="text-center py-10 text-grey">
                <v-icon size="64" class="mb-3">mdi-tools</v-icon>
                <div class="text-h6">ຟັງຊັນນີ້ກຳລັງພັດທະນາ</div>
                <div>(ຈະເພີ່ມໃນຂັ້ນຕອນຕໍ່ໄປ)</div>
             </div>
          </v-window-item>

        </v-window>
      </v-card>

    </div>

    <div v-else class="d-flex flex-column align-center justify-center py-16 text-grey">
      <v-icon size="100" color="grey-lighten-3" class="mb-4">mdi-google-classroom</v-icon>
      <div class="text-h6">ກະລຸນາເລືອກຫ້ອງຮຽນ</div>
      <div class="text-body-2">ເລືອກຫ້ອງຮຽນຈາກເມນູດ້ານເທິງເພື່ອເລີ່ມຕົ້ນ</div>
    </div>

    <v-dialog v-model="dialogBehavior" max-width="500px">
      <v-card rounded="xl">
        <v-card-title class="bg-primary text-white d-flex align-center">
           <v-icon start>mdi-star-face</v-icon> ບັນທຶກພຶດຕິກຳ
        </v-card-title>
        <v-card-text class="pt-4">
           <v-select
              v-model="behaviorForm.student_id"
              :items="students"
              item-title="full_name"
              item-value="id"
              label="ເລືອກນັກຮຽນ *"
              variant="outlined"
              prepend-inner-icon="mdi-account"
           ></v-select>

           <v-radio-group v-model="behaviorForm.type" inline>
              <v-radio label="ຊົມເຊີຍ (+)" value="POSITIVE" color="success"></v-radio>
              <v-radio label="ຕັກເຕືອນ (-)" value="NEGATIVE" color="error"></v-radio>
           </v-radio-group>

           <v-text-field
              v-model="behaviorForm.title"
              label="ຫົວຂໍ້ (ເຊັ່ນ: ຊ່ວຍເຫຼືອໝູ່, ມາຊ້າ) *"
              variant="outlined"
           ></v-text-field>

           <v-text-field
              v-model.number="behaviorForm.points"
              label="ຄະແນນ (ຕົວເລກ)"
              type="number"
              variant="outlined"
              prepend-inner-icon="mdi-numeric"
           ></v-text-field>

           <v-textarea
              v-model="behaviorForm.description"
              label="ລາຍລະອຽດເພີ່ມເຕີມ"
              variant="outlined"
              rows="2"
           ></v-textarea>
        </v-card-text>
        <v-card-actions class="justify-end px-4 pb-4">
           <v-btn variant="text" @click="dialogBehavior = false">ຍົກເລີກ</v-btn>
           <v-btn color="primary" variant="elevated" @click="submitBehavior" :loading="savingBehavior">ບັນທຶກ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top">
       {{ snackbar.message }}
    </v-snackbar>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getMyClasses, getStudentsInClass, addBehaviorLog } from '../../services/api';

// States
const myClasses = ref([]);
const students = ref([]);
const selectedClassId = ref(null);
const loadingClasses = ref(false);
const loadingStudents = ref(false);
const savingBehavior = ref(false);
const tab = ref('students');
const isTodayChecked = ref(false);

const dialogBehavior = ref(false);
const behaviorForm = ref({
    student_id: null,
    type: 'POSITIVE',
    title: '',
    points: 1,
    description: ''
});

const snackbar = ref({ show: false, message: '', color: 'success' });

const studentHeaders = [
    { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name', align: 'start' },
    { title: 'ເບີໂທຜູ້ປົກຄອງ', key: 'parent', align: 'start' },
    { title: 'ຄະແນນສະສົມ', key: 'points', align: 'center' },
    { title: 'ຈັດການ', key: 'actions', align: 'end', sortable: false },
];

// 1. ໂຫຼດຫ້ອງຮຽນຂອງຄູ
const fetchClasses = async () => {
    loadingClasses.value = true;
    try {
        const res = await getMyClasses();
        myClasses.value = res.data;
        
        // ຖ້າມີຫ້ອງດຽວ ຫຼື ຫຼາຍຫ້ອງ ໃຫ້ເລືອກຫ້ອງທຳອິດ Auto
        if (myClasses.value.length > 0) {
            selectedClassId.value = myClasses.value[0].id;
            fetchStudents();
        }
    } catch (error) {
        console.error("Error fetching classes:", error);
    } finally {
        loadingClasses.value = false;
    }
};

// 2. ໂຫຼດນັກຮຽນໃນຫ້ອງ
const fetchStudents = async () => {
    if (!selectedClassId.value) return;
    loadingStudents.value = true;
    try {
        const res = await getStudentsInClass(selectedClassId.value);
        students.value = res.data;
    } catch (error) {
        console.error("Error fetching students:", error);
    } finally {
        loadingStudents.value = false;
    }
};

// 3. ບັນທຶກຄະແນນພຶດຕິກຳ
const submitBehavior = async () => {
    if (!behaviorForm.value.student_id || !behaviorForm.value.title) {
        showMsg("ກະລຸນາປ້ອນຂໍ້ມູນໃຫ້ຄົບ", "error");
        return;
    }

    savingBehavior.value = true;
    try {
        // ປັບຄະແນນໃຫ້ເປັນລົບ ຖ້າເລືອກ NEGATIVE
        let pts = Math.abs(behaviorForm.value.points);
        if (behaviorForm.value.type === 'NEGATIVE') pts = -pts;

        await addBehaviorLog({
            ...behaviorForm.value,
            points: pts
        });

        showMsg("ບັນທຶກຄະແນນສຳເລັດ! ✅");
        dialogBehavior.value = false;
        
        // Reset Form
        behaviorForm.value = { student_id: null, type: 'POSITIVE', title: '', points: 1, description: '' };
        
        // Refresh Data
        fetchStudents();

    } catch (error) {
        console.error(error);
        showMsg("ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ", "error");
    } finally {
        savingBehavior.value = false;
    }
};

const showMsg = (msg, type = 'success') => {
    snackbar.value = { show: true, message: msg, color: type === 'success' ? 'green-darken-1' : 'red-darken-1' };
};

onMounted(fetchClasses);
</script>