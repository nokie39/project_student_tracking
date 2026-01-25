<template>
  <v-container>
    <v-card elevation="2" rounded="xl" class="report-card">
      <v-card-title class="bg-primary text-white py-4 d-flex align-center print-hide">
        <v-icon start>mdi-history</v-icon>
        ປະຫວັດການຮຽນລະອຽດ (Detailed History)
        <v-spacer></v-spacer>
        <v-btn variant="elevated" color="white" class="text-primary" @click="print">
          <v-icon start>mdi-printer</v-icon> ພິມລາຍງານ
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-4">
        <div class="text-center mb-6 student-header">
          <h2 class="text-h5 font-weight-bold">{{ info.full_name }}</h2>
          <p class="text-subtitle-1 text-grey-darken-1">ລະຫັດນັກຮຽນ: {{ info.code }}</p>
        </div>

        <div v-for="(year, yIndex) in history" :key="yIndex" class="mb-8 year-block">
          
          <h3 class="text-h6 font-weight-bold mb-3 text-primary bg-blue-lighten-5 pa-2 rounded year-title">
            <v-icon start class="print-hide">mdi-school</v-icon> ສົກຮຽນ: {{ year.year_info }}
          </h3>

          <v-expansion-panels variant="accordion" multiple class="month-panels">
            <v-expansion-panel v-for="(month, mIndex) in year.months" :key="mIndex" class="mb-2">
              <v-expansion-panel-title class="font-weight-bold">
                {{ month.month_name }}
              </v-expansion-panel-title>
              
              <v-expansion-panel-text>
                <v-table density="compact" class="grade-table">
                  <thead>
                    <tr>
                      <th class="text-left" style="width: 30%;">ວິຊາ</th>
                      <th class="text-center">ມາຮຽນ</th>
                      <th class="text-center">ວຽກບ້ານ/ເສັງຍ່ອຍ</th>
                      <th class="text-center">ກາງພາກ</th>
                      <th class="text-center">ທ້າຍພາກ</th>
                      <th class="text-center font-weight-bold bg-grey-lighten-4">ລວມ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(subj, sIndex) in month.subjects" :key="sIndex">
                      <td class="font-weight-medium">{{ subj.subject }}</td>
                      <td class="text-center">{{ subj.attendance || '-' }}</td>
                      <td class="text-center">{{ subj.homework || '-' }}</td>
                      <td class="text-center">{{ subj.midterm || '-' }}</td>
                      <td class="text-center">{{ subj.final || '-' }}</td>
                      <td class="text-center font-weight-bold bg-grey-lighten-5">
                        {{ subj.total ? subj.total.toFixed(2) : '0' }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

        </div>

        <div class="print-only signature-section mt-10">
            <div class="d-flex justify-space-between text-center">
                <div style="width: 200px;">
                    <p>ຜູ້ອຳນວຍການ</p>
                    <br><br><br>
                    <p>.......................................</p>
                </div>
                <div style="width: 200px;">
                    <p>ຄູປະຈຳຫ້ອງ</p>
                    <br><br><br>
                    <p>.......................................</p>
                </div>
            </div>
        </div>

      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getStudentDetailHistory } from '../services/api';

const route = useRoute();
const info = ref({});
const history = ref([]);

const fetchData = async () => {
  const studentId = route.params.id;
  try {
    const res = await getStudentDetailHistory(studentId);
    info.value = res.data.student;
    history.value = res.data.history;
  } catch (e) {
    console.error(e);
  }
};

const print = () => {
    window.print();
};

onMounted(fetchData);
</script>

<style scoped>
/* CSS ປົກກະຕິ */
.grade-table th { font-weight: bold !important; color: #1976D2; }

/* CSS ສຳລັບການ Print 🖨️ */
@media print {
  /* 1. ເຊື່ອງສິ່ງທີ່ບໍ່ຕ້ອງການ */
  .print-hide, 
  .v-navigation-drawer, 
  .v-app-bar, 
  .v-footer,
  .v-overlay-container,
  button {
    display: none !important;
  }

  /* 2. ຈັດ Format ໜ້າເຈ້ຍ */
  @page { size: A4; margin: 2cm; }
  body, .v-application { background: white !important; font-family: 'Phetsarath OT', sans-serif; }
  .v-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
  .v-card { box-shadow: none !important; border: none !important; }

  /* 3. ບັງຄັບເປີດ Accordion ທຸກອັນ */
  .v-expansion-panel { 
    break-inside: avoid; 
    border: 1px solid #ccc !important;
    margin-bottom: 15px !important;
    box-shadow: none !important;
  }
  .v-expansion-panel-title { 
    min-height: 40px !important; 
    padding: 8px 16px !important; 
    background-color: #f0f0f0 !important;
    border-bottom: 1px solid #ddd;
  }
  .v-expansion-panel-text { 
    display: block !important; /* Force Show Content */
    padding: 0 !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 10px !important;
  }

  /* 4. ຕາຕະລາງ */
  .grade-table { width: 100%; border-collapse: collapse; }
  .grade-table th, .grade-table td { 
    border: 1px solid black !important; 
    padding: 6px !important;
    font-size: 12px;
    color: black !important;
  }
  
  /* 5. ຫົວຂໍ້ */
  .year-title {
    background: none !important;
    color: black !important;
    border-bottom: 2px solid black;
    margin-top: 20px;
    padding: 5px 0 !important;
  }

  /* 6. Footer ລາຍເຊັນ */
  .print-only { display: block !important; }
}

.print-only { display: none; }
</style>