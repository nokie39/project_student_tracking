<template>
  <v-container>
    <v-card elevation="2" rounded="xl" class="pa-4 print-card">
      
      <div class="d-flex justify-end mb-4 screen-only">
        <v-btn color="primary" prepend-icon="mdi-printer" @click="print">ພິມໃບເກຣດ</v-btn>
      </div>

      <div class="text-center mb-6">
        <div class="text-h6 font-weight-bold">ໃບຢັ້ງຢືນຜົນການຮຽນ (Transcript)</div>
        <div class="text-subtitle-1">{{ info.full_name }} ({{ info.student_code }})</div>
      </div>

      <div v-for="(year, index) in history" :key="index" class="mb-6">
        <v-card variant="outlined" class="mb-2">
          <v-card-title class="bg-grey-lighten-3 d-flex justify-space-between text-subtitle-2 font-weight-bold">
            <span>ສົກຮຽນ: {{ year.year_name }} ({{ year.class_name }})</span>
            <span class="text-primary">GPA: {{ year.gpa }}</span>
          </v-card-title>
          
          <v-table density="compact">
            <thead>
              <tr>
                <th class="text-left">ວິຊາ</th>
                <th class="text-center">ຄະແນນສະເລ່ຍ</th>
                <th class="text-center">ເກຣດ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subj in year.subjects" :key="subj.subject">
                <td>{{ subj.subject }}</td>
                <td class="text-center">{{ subj.score }}</td>
                <td class="text-center">
                  <v-chip size="x-small" :color="getGradeColor(subj.grade)" variant="flat">{{ subj.grade }}</v-chip>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </div>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getStudentTranscript } from '../services/api';

const route = useRoute();
const info = ref({});
const history = ref([]);

const fetchTranscript = async () => {
  const studentId = route.params.id;
  try {
    const res = await getStudentTranscript(studentId);
    info.value = res.data.student_info;
    history.value = res.data.academic_history;
  } catch (e) {
    console.error(e);
  }
};

const getGradeColor = (grade) => {
    if(['A', 'B'].includes(grade)) return 'success';
    if(['C', 'D'].includes(grade)) return 'warning';
    return 'error';
};

const print = () => window.print();

onMounted(fetchTranscript);
</script>

<style scoped>
@media print {
  .screen-only { display: none !important; }
  .v-card { border: none !important; box-shadow: none !important; }
  .print-card { width: 100%; }
}
</style>