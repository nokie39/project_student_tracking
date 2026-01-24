<template>
  <v-container fluid class="fill-height align-start bg-grey-lighten-5 pa-0">
    
    <v-card color="teal" rounded="b-xl" class="pa-6 pb-12 w-100 mb-n10" elevation="4">
      <div class="d-flex align-center text-white">
        <v-btn icon="mdi-arrow-left" variant="text" color="white" @click="$router.back()"></v-btn>
        <span class="text-h6 font-weight-bold ml-2">ຜົນການຮຽນ</span>
      </div>
      <div class="text-center mt-4 text-white">
        <div class="text-h3 font-weight-bold">3.85</div>
        <div class="text-caption opacity-80">GPA ສະເລ່ຍລວມ</div>
      </div>
    </v-card>

    <v-container class="px-4 mt-4">
      
      <div class="text-subtitle-1 font-weight-bold text-grey-darken-3 mb-3">ລາຍວິຊາ</div>
      
      <v-card v-if="grades.length > 0" class="rounded-xl" elevation="2">
        <v-list lines="two">
          <v-list-item v-for="(item, i) in grades" :key="i">
            <template v-slot:prepend>
              <v-avatar color="teal-lighten-5" size="50" class="text-teal font-weight-bold">
                {{ item.grade }}
              </v-avatar>
            </template>
            
            <v-list-item-title class="font-weight-bold">{{ item.subject_name }}</v-list-item-title>
            <v-list-item-subtitle>
              ຄະແນນລວມ: {{ item.score }} (ກາງພາກ: {{ item.midterm }} | ທ້າຍພາກ: {{ item.final }})
            </v-list-item-subtitle>

            <template v-slot:append>
              <v-icon color="grey-lighten-2">mdi-chevron-right</v-icon>
            </template>
          </v-list-item>
        </v-list>
      </v-card>

      <v-alert v-else type="info" variant="tonal" class="rounded-xl mt-4">
        ຍັງບໍ່ມີຂໍ້ມູນຄະແນນໃນພາກຮຽນນີ້.
      </v-alert>

    </v-container>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../../services/api';

const route = useRoute();
const grades = ref([]);
const studentName = ref("");

const fetchGrades = async () => {
  try {
    const studentId = route.params.studentId;
    const res = await api.get(`/parents/student/${studentId}/grades`);
    grades.value = res.data.grades;
    studentName.value = res.data.student_name;
  } catch (error) {
    console.error(error);
  }
};

onMounted(fetchGrades);
</script>