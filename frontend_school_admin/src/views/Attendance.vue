<template>
  <v-container>
    <v-card elevation="2" rounded="lg">
      <v-card-title class="bg-primary text-white py-4 px-4 d-flex align-center">
        <v-icon icon="mdi-calendar-check" start></v-icon>
        <span>ບັນທຶກການມາຮຽນ (Attendance)</span>
      </v-card-title>

      <v-card-text class="mt-4">
        <v-row align="center">
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
            <v-text-field
              v-model="date"
              type="date"
              label="ວັນທີ"
              variant="outlined"
              density="compact"
              hide-details
              @change="fetchData"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4" class="text-right">
             <div class="d-flex justify-end gap-2">
                <v-chip color="success" size="small">ມາ: {{ countStatus('PRESENT') }}</v-chip>
                <v-chip color="warning" size="small">ຊ້າ: {{ countStatus('LATE') }}</v-chip>
                <v-chip color="info" size="small">ລາ: {{ countStatus('LEAVE') }}</v-chip>
                <v-chip color="error" size="small">ຂາດ: {{ countStatus('ABSENT') }}</v-chip>     
             </div>
          </v-col>
        </v-row>

        <v-divider class="my-4"></v-divider>

        <v-data-table
          :headers="headers"
          :items="students"
          :loading="loading"
          items-per-page="-1"
          class="elevation-0 border rounded-lg"
          no-data-text="ກະລຸນາເລືອກຫ້ອງຮຽນ"
        >
          <template v-slot:item.status="{ item }">
            <v-btn-toggle
              v-model="item.status"
              mandatory
              density="compact"
              rounded="xl"
              divided
            >
              <v-btn value="PRESENT" color="success" size="small" variant="tonal">
                 ມາ
              </v-btn>
              <v-btn value="LATE" color="warning" size="small" variant="tonal">
                 ຊ້າ
              </v-btn>
              <v-btn value="LEAVE" color="info" size="small" variant="tonal">
                 ລາ
              </v-btn>
              <v-btn value="ABSENT" color="error" size="small" variant="tonal">
                 ຂາດ
              </v-btn>
            </v-btn-toggle>
          </template>
        </v-data-table>
      </v-card-text>

      <v-card-actions class="pa-4 bg-grey-lighten-5">
        <v-spacer></v-spacer>
        <v-btn 
            color="primary" 
            variant="elevated" 
            size="large" 
            prepend-icon="mdi-content-save"
            @click="save"
            :loading="saving"
            :disabled="students.length === 0"
        >
          ບັນທຶກການເຊັກຊື່
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getClasses, getAttendance, saveAttendance } from '../services/api';

const classes = ref([]);
const selectedClass = ref(null);
const date = ref(new Date().toISOString().substr(0, 10)); // ວັນທີປັດຈຸບັນ YYYY-MM-DD
const students = ref([]);
const loading = ref(false);
const saving = ref(false);

const headers = [
  { title: 'ລະຫັດ', key: 'student_code', width: '150px' },
  { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name' },
  { title: 'ສະຖານະການມາຮຽນ', key: 'status', align: 'center', sortable: false },
];

const loadClasses = async () => {
    try {
        const res = await getClasses();
        classes.value = res.data;
        if (classes.value.length > 0) {
            selectedClass.value = classes.value[0].id;
            fetchData();
        }
    } catch (error) {
        console.error(error);
    }
};

const fetchData = async () => {
    if (!selectedClass.value || !date.value) return;
    
    loading.value = true;
    try {
        const res = await getAttendance(selectedClass.value, date.value);
        students.value = res.data;
    } catch (error) {
        alert("Error loading attendance");
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
            students: students.value.map(s => ({
                student_id: s.student_id,
                status: s.status
            }))
        };
        
        await saveAttendance(payload);
        alert("ບັນທຶກສຳເລັດ! ✅");
    } catch (error) {
        alert("ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ");
    } finally {
        saving.value = false;
    }
};

onMounted(loadClasses);
</script>