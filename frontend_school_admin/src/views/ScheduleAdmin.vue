<template>
  <v-card elevation="2" class="ma-4">
    <v-card-title class="bg-primary text-white py-4 d-flex justify-space-between align-center">
      <div>
        <v-icon icon="mdi-calendar-clock" start></v-icon>
        ຈັດຕາຕະລາງຮຽນ (ຫ້ອງ ມ.4/1)
      </div>
      <v-btn color="white" variant="outlined" prepend-icon="mdi-plus" @click="dialog = true">
        ເພີ່ມວິຊາຮຽນ
      </v-btn>
    </v-card-title>

    <v-card-text class="mt-4">
      <v-row>
        <v-col cols="12" md="4" v-for="(dayName, dayIndex) in days" :key="dayIndex">
          <v-card variant="outlined" class="h-100">
            <v-card-title class="text-subtitle-1 font-weight-bold bg-grey-lighten-3">
              {{ dayName }}
            </v-card-title>
            <v-list density="compact">
              <v-list-item v-for="item in getItemsByDay(dayIndex + 1)" :key="item.id">
                <template v-slot:prepend>
                  <v-chip size="small" color="primary" class="mr-2">
                    {{ formatTime(item.start_time) }}
                  </v-chip>
                </template>
                <v-list-item-title class="font-weight-bold">{{ item.subject_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  <div><v-icon size="x-small" icon="mdi-account-tie"></v-icon> {{ item.teacher_name || 'ບໍ່ມີຊື່ຄູ' }}</div>
                  <div><v-icon size="x-small" icon="mdi-map-marker"></v-icon> {{ item.room }}</div>
                </v-list-item-subtitle>
              </v-list-item>
              
              <div v-if="getItemsByDay(dayIndex + 1).length === 0" class="text-center text-grey py-4 text-caption">
                - ຫວ່າງ -
              </div>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="550">
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-3">ເພີ່ມວິຊາຮຽນໃໝ່</v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newItem.day_of_week"
                  :items="dayOptions"
                  item-title="text"
                  item-value="value"
                  label="ວັນຮຽນ *"
                  variant="outlined"
                  density="compact"
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field 
                  v-model="newItem.subject_name" 
                  label="ຊື່ວິຊາ *" 
                  variant="outlined" 
                  density="compact"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field 
                  v-model="newItem.teacher_name" 
                  label="ຊື່ຄູສອນ" 
                  variant="outlined" 
                  density="compact"
                  prepend-inner-icon="mdi-account"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field 
                  v-model="newItem.room" 
                  label="ຫ້ອງຮຽນ" 
                  variant="outlined" 
                  density="compact"
                  prepend-inner-icon="mdi-door"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="newItem.start_time" type="time" label="ເວລາເລີ່ມ" variant="outlined" density="compact"></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="newItem.end_time" type="time" label="ເວລາເລີກ" variant="outlined" density="compact"></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field 
                  v-model="newItem.note" 
                  label="ໝາຍເຫດ (ເພີ່ມເຕີມ)" 
                  variant="outlined" 
                  density="compact"
                  placeholder="ຕົວຢ່າງ: ກຽມປຶ້ມແບບຮຽນມາພ້ອມ"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">ຍົກເລີກ</v-btn>
          <v-btn color="primary" variant="elevated" @click="save" :loading="saving">ບັນທຶກຕາຕະລາງ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getClassSchedule, createSchedule } from '../services/api';

const schedules = ref([]);
const dialog = ref(false);
const saving = ref(false);
const valid = ref(false);
const currentClassId = 1;

const days = ['ວັນຈັນ', 'ວັນຄານ', 'ວັນພຸດ', 'ວັນພະຫັດ', 'ວັນສຸກ'];
const dayOptions = days.map((d, i) => ({ text: d, value: i + 1 }));

const newItem = ref({
  day_of_week: 1,
  subject_name: '',
  teacher_name: '', // ເພີ່ມໃໝ່
  start_time: '08:00',
  end_time: '09:30',
  room: 'A101',
  note: '' // ເພີ່ມໃໝ່
});

const fetchData = async () => {
  try {
    const res = await getClassSchedule(currentClassId);
    schedules.value = res.data;
  } catch (error) {
    console.error(error);
  }
};

const save = async () => {
  saving.value = true;
  try {
    const payload = {
      class_id: currentClassId,
      subject_name: newItem.value.subject_name,
      teacher_name: newItem.value.teacher_name, // ສົ່ງໄປ Backend
      day_of_week: newItem.value.day_of_week,
      start_time: newItem.value.start_time + ":00",
      end_time: newItem.value.end_time + ":00",
      room: newItem.value.room,
      note: newItem.value.note // ສົ່ງໄປ Backend
    };

    await createSchedule(payload);
    alert('ບັນທຶກຕາຕະລາງສຳເລັດ! ✅');
    dialog.value = false;
    
    // Reset form
    newItem.value = { 
      day_of_week: 1, subject_name: '', teacher_name: '', 
      start_time: '08:00', end_time: '09:30', room: 'A101', note: '' 
    };
    
    fetchData();
  } catch (error) {
    alert('ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ');
  }
  saving.value = false;
};

const getItemsByDay = (dayIndex) => {
  return schedules.value.filter(s => s.day_of_week === dayIndex);
};

const formatTime = (timeStr) => {
  return timeStr ? timeStr.slice(0, 5) : '--:--';
};

onMounted(fetchData);
</script>