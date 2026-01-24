<template>
  <v-container>
    <v-card elevation="2" rounded="xl">
      <v-card-title class="bg-primary text-white py-4 px-6 d-flex align-center">
        <v-icon icon="mdi-calendar-check" start size="28"></v-icon>
        <span class="text-h6 font-weight-bold">ບັນທຶກການມາຮຽນ (Attendance)</span>
      </v-card-title>

      <v-card-text class="mt-6">
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedClass"
              :items="classes"
              item-title="name"
              item-value="id"
              label="ເລືອກຫ້ອງຮຽນ"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-google-classroom"
              hide-details
              class="rounded-lg"
              @update:model-value="fetchData"
            ></v-select>
          </v-col>

          <v-col cols="12" md="3">
            <v-text-field
              v-model="date"
              type="date"
              label="ວັນທີ"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-calendar"
              hide-details
              class="rounded-lg"
              @change="fetchData"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="period"
              :items="periodOptions"
              label="ຊົ່ວໂມງ/ວິຊາ"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-clock-outline"
              hide-details
              class="rounded-lg"
              @update:model-value="fetchData"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="2" class="text-right">
             <div class="d-flex flex-column align-end gap-2">
                <v-chip color="success" variant="flat" size="x-small" class="font-weight-bold">
                  ມາ: {{ countStatus('PRESENT') }}
                </v-chip>
                <v-chip color="error" variant="flat" size="x-small" class="font-weight-bold">
                  ຂາດ: {{ countStatus('ABSENT') }}
                </v-chip>     
             </div>
          </v-col>
        </v-row>

        <v-divider class="my-6"></v-divider>

        <v-data-table
          :headers="headers"
          :items="students"
          :loading="loading"
          items-per-page="-1"
          class="elevation-0 border rounded-lg"
          no-data-text="ກະລຸນາເລືອກຫ້ອງຮຽນ"
          hover
        >
          <template v-slot:item.full_name="{ item }">
            <div class="font-weight-bold text-primary">{{ item.full_name }}</div>
            <div class="text-caption text-grey">{{ item.student_code }}</div>
          </template>

          <template v-slot:item.status="{ item }">
            <v-btn-toggle
              v-model="item.status"
              mandatory
              density="compact"
              rounded="xl"
              divided
              class="my-1 border"
            >
              <v-btn value="PRESENT" color="success" size="small" variant="tonal" class="font-weight-bold">ມາ</v-btn>
              <v-btn value="LATE" color="warning" size="small" variant="tonal" class="font-weight-bold">ຊ້າ</v-btn>
              <v-btn value="PERMISSION" color="info" size="small" variant="tonal" class="font-weight-bold">ລາ</v-btn>
              <v-btn value="ABSENT" color="error" size="small" variant="tonal" class="font-weight-bold">ຂາດ</v-btn>
            </v-btn-toggle>
          </template>

          <template v-slot:item.remark="{ item }">
             <v-text-field
                v-model="item.remark"
                placeholder="ໝາຍເຫດ..."
                variant="plain"
                density="compact"
                hide-details
                single-line
             ></v-text-field>
          </template>
        </v-data-table>
      </v-card-text>

      <v-card-actions class="pa-6 bg-grey-lighten-5 d-flex justify-end">
        <v-btn 
            color="primary" 
            variant="elevated" 
            size="large" 
            prepend-icon="mdi-content-save"
            @click="save"
            :loading="saving"
            :disabled="students.length === 0"
            class="px-6"
        >
          ບັນທຶກ ({{ period }})
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top">
       <v-icon start>{{ snackbar.icon }}</v-icon> {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getClasses, getAttendance, saveAttendance, getMyClasses } from '../services/api';

const classes = ref([]);
const selectedClass = ref(null);
const date = ref(new Date().toISOString().substr(0, 10)); // YYYY-MM-DD
const period = ref('DAILY'); // ✅ Default Period
const students = ref([]);
const loading = ref(false);
const saving = ref(false);

// ✅ ຕົວເລືອກ Period (ທ່ານສາມາດປັບປ່ຽນໄດ້ຕາມໃຈ)
const periodOptions = [
  { title: 'ປະຈຳວັນ (Homeroom)', value: 'DAILY' },
  { title: 'ຕອນເຊົ້າ (Morning)', value: 'MORNING' },
  { title: 'ຕອນແລງ (Afternoon)', value: 'AFTERNOON' },
  { title: 'ຄະນິດສາດ (Math)', value: 'MATH' },
  { title: 'ພາສາລາວ (Lao)', value: 'LAO' },
  { title: 'ພາສາອັງກິດ (English)', value: 'ENGLISH' },
  { title: 'ຟີຊິກ (Physics)', value: 'PHYSICS' },
  { title: 'ເຄມີ (Chemistry)', value: 'CHEMISTRY' },
];

const snackbar = ref({
    show: false,
    message: '',
    color: 'success',
    icon: 'mdi-check-circle'
});

const headers = [
  { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name', width: '250px' },
  { title: 'ສະຖານະ', key: 'status', align: 'center', sortable: false, width: '300px' },
  { title: 'ໝາຍເຫດ', key: 'remark', sortable: false },
];

const loadClasses = async () => {
    try {
        // ໃຊ້ getMyClasses ຖ້າເປັນຄູ, ຫຼື getClasses ຖ້າເປັນ Admin (API ຈະຈັດການເອງຖ້າທ່ານໃຊ້ Token ຖືກ)
        // ໃນທີ່ນີ້ລອງໃຊ້ getMyClasses ເພື່ອຄວາມຊົວສຳລັບ Teacher
        const res = await getMyClasses().catch(() => getClasses()); 
        classes.value = res.data;
        if (classes.value.length > 0) {
            selectedClass.value = classes.value[0].id;
            fetchData();
        }
    } catch (error) {
        console.error(error);
        showMsg("ບໍ່ສາມາດໂຫຼດຂໍ້ມູນຫ້ອງຮຽນໄດ້", "error");
    }
};

const fetchData = async () => {
    if (!selectedClass.value || !date.value) return;
    
    loading.value = true;
    try {
        // ✅ ສົ່ງ period ໄປນຳ
        const res = await getAttendance(selectedClass.value, date.value, period.value);
        students.value = res.data;
    } catch (error) {
        showMsg("ເກີດຂໍ້ຜິດພາດໃນການໂຫຼດຂໍ້ມູນ", "error");
    } finally {
        loading.value = false;
    }
};

const countStatus = (status) => {
    return students.value.filter(s => s.status === status).length;
};

const save = async () => {
    saving.value = true;
    try {
        const payload = {
            class_id: selectedClass.value,
            date: date.value,
            period: period.value, // ✅ ສົ່ງ period ໄປບັນທຶກ
            students: students.value.map(s => ({
                student_id: s.student_id,
                status: s.status,
                remark: s.remark
            }))
        };
        
        await saveAttendance(payload);
        showMsg(`ບັນທຶກສຳເລັດ! (${period.value})`, "success");
    } catch (error) {
        showMsg("ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ", "error");
    } finally {
        saving.value = false;
    }
};

const showMsg = (msg, type = 'success') => {
    snackbar.value = {
        show: true,
        message: msg,
        color: type === 'success' ? 'green-darken-1' : 'red-darken-1',
        icon: type === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'
    };
};

onMounted(loadClasses);
</script>