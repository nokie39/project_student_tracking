<template>
  <v-container>
    <v-card elevation="2" rounded="xl" class="report-card">
      
      <v-card-title class="d-flex align-center bg-primary text-white py-4 screen-only">
        <v-icon start>mdi-file-chart-outline</v-icon>
        ສະຫຼຸບຜົນການຮຽນປະຈຳພາກ (Semester Report)
        <v-spacer></v-spacer>
        <v-btn variant="elevated" color="white" class="text-primary" prepend-icon="mdi-printer" @click="printReport">
          ພິມບົດສະຫຼຸບ
        </v-btn>
      </v-card-title>

      <div class="print-header text-center mb-4" style="display: none;">
        <h2>ສາທາລະນະລັດ ປະຊາທິປະໄຕ ປະຊາຊົນລາວ</h2>
        <h3>ສັນຕິພາບ ເອກະລາດ ປະຊາທິປະໄຕ ເອກະພາບ ວັດທະນະຖາວອນ</h3>
        <br>
        <h1>ໃບສະຫຼຸບຜົນການຮຽນ</h1>
        <p>ສົກຮຽນ: 2025-2026 | ຫ້ອງ: {{ className }} | ພາກຮຽນທີ: {{ selectedSemester }}</p>
      </div>

      <v-card-text>
        <v-row class="mb-4 screen-only" align="center">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedClass"
              :items="classes"
              item-title="name"
              item-value="id"
              label="ເລືອກຫ້ອງຮຽນ"
              variant="outlined"
              density="compact"
              prepend-inner-icon="mdi-google-classroom"
              @update:model-value="fetchData"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedSemester"
              :items="[1, 2]"
              label="ເລືອກພາກຮຽນ"
              variant="outlined"
              density="compact"
              prepend-inner-icon="mdi-calendar-range"
              @update:model-value="fetchData"
            ></v-select>
          </v-col>
        </v-row>

        <v-divider class="mb-4 screen-only"></v-divider>

        <v-data-table
          :headers="headers"
          :items="students"
          :loading="loading"
          class="elevation-0 border"
          items-per-page="-1"
          no-data-text="ກະລຸນາເລືອກຫ້ອງແລະພາກຮຽນ"
        >
          <template v-slot:item.subjects="{ item }">
            <div class="py-2">
              <v-table density="compact" class="subject-table">
                <thead>
                  <tr>
                    <th class="text-left" width="120px">ວິຊາ</th>
                    <th class="text-center">ເກັບ</th>
                    <th class="text-center">ກາງ</th>
                    <th class="text-center">ທ້າຍ</th>
                    <th class="text-center">ລວມ</th>
                    <th class="text-center">ເກຣດ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(sub, index) in item.subjects" :key="index">
                    <td class="font-weight-medium">{{ sub.subject }}</td>
                    <td class="text-center text-caption">{{ sub.avg_regular }}</td>
                    <td class="text-center text-caption">{{ sub.midterm }}</td>
                    <td class="text-center text-caption">{{ sub.final }}</td>
                    <td class="text-center font-weight-bold">{{ sub.total }}</td>
                    <td class="text-center">
                      <v-chip size="x-small" :color="getGradeColor(sub.grade)" variant="flat">
                        {{ sub.grade }}
                      </v-chip>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </template>

          <template v-slot:item.gpa="{ item }">
            <div class="text-center">
              <h3 class="text-h6 font-weight-bold text-primary">{{ calculateGPA(item.subjects) }}</h3>
              <span class="text-caption">ສະເລ່ຍລວມ</span>
            </div>
          </template>

        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getClasses, getSemesterSummary } from '../services/api';

const students = ref([]);
const classes = ref([]);
const selectedClass = ref(null);
const selectedSemester = ref(1);
const loading = ref(false);

const headers = [
  { title: 'ລະຫັດ', key: 'student_code', width: '100px' },
  { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name', width: '200px' },
  { title: 'ຜົນການຮຽນແຕ່ລະວິຊາ', key: 'subjects', sortable: false },
  { title: 'ຄະແນນສະເລ່ຍ (GPA)', key: 'gpa', align: 'center', width: '150px' },
];

const className = computed(() => {
    const cls = classes.value.find(c => c.id === selectedClass.value);
    return cls ? cls.name : '';
});

// 1. ໂຫຼດຫ້ອງຮຽນ
const fetchClasses = async () => {
  try {
    const res = await getClasses();
    classes.value = res.data;
    if(classes.value.length > 0) selectedClass.value = classes.value[0].id;
    fetchData();
  } catch (error) {
    console.error(error);
  }
};

// 2. ໂຫຼດບົດສະຫຼຸບ
const fetchData = async () => {
  if (!selectedClass.value) return;
  loading.value = true;
  try {
    const res = await getSemesterSummary(selectedClass.value, selectedSemester.value);
    students.value = res.data;
  } catch (error) {
    console.error("Error loading report:", error);
  }
  loading.value = false;
};

// 3. Helper Functions
const getGradeColor = (grade) => {
  if (['A', 'B+'].includes(grade)) return 'green-lighten-1';
  if (['B', 'C+'].includes(grade)) return 'blue-lighten-1';
  if (['C', 'D+'].includes(grade)) return 'orange-lighten-1';
  return 'red-lighten-1';
};

const calculateGPA = (subjects) => {
  if (!subjects || subjects.length === 0) return "0.00";
  // ນີ້ແມ່ນຕົວຢ່າງການຫາຄ່າສະເລ່ຍຂອງຄະແນນ total (0-100)
  // ຖ້າຢາກຄິດເປັນ GPA 4.00 ຕ້ອງຂຽນສູດແປງຄະແນນເພີ່ມ
  const sum = subjects.reduce((acc, curr) => acc + curr.total, 0);
  return (sum / subjects.length).toFixed(2);
};

// 4. Print Function
const printReport = () => {
  window.print();
};

onMounted(fetchClasses);
</script>

<style scoped>
/* Table Styling */
.subject-table {
  background-color: transparent !important;
  border: 1px solid #eee;
  border-radius: 8px;
}

/* 🖨️ PRINT STYLES: CSS ສຳລັບຕອນສັ່ງພິມເທົ່ານັ້ນ */
@media print {
  /* ເຊື່ອງອົງປະກອບທີ່ບໍ່ຕ້ອງການ */
  .screen-only, 
  .v-navigation-drawer, 
  .v-app-bar,
  .v-footer {
    display: none !important;
  }

  /* ສະແດງ Header ພິມ */
  .print-header {
    display: block !important;
  }

  /* ຈັດ format ໃຫ້ເຕັມໜ້າເຈ້ຍ */
  .v-container, .v-card, .v-card-text {
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    width: 100% !important;
  }

  /* ບັງຄັບໃຫ້ Table ມີເສັ້ນຂອບຊັດເຈນ */
  .v-data-table {
    border: 1px solid black !important;
  }
  
  th, td {
    border: 1px solid #ddd !important;
    font-size: 12px !important;
    color: black !important;
  }
  
  /* ✅ ແກ້ໄຂແລ້ວ: ບັງຄັບສີພື້ນຫຼັງ */
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>