<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2 class="text-indigo-darken-3 mb-4">
          <v-icon icon="mdi-chart-box" class="mr-2"></v-icon>
          ລາຍງານສະຖິຕິລວມ (Academic Reports)
        </h2>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center mt-5">
        <v-progress-circular indeterminate color="primary" size="50"></v-progress-circular>
        <div class="mt-2 text-grey">ກຳລັງຄິດໄລ່ສະຖິຕິ...</div>
      </v-col>
    </v-row>

    <div v-else>
      <v-row>
        <v-col cols="12" sm="6" md="3">
            <v-card elevation="2" rounded="lg" class="pa-2 h-100">
                <v-card-item>
                    <template v-slot:prepend>
                        <v-icon icon="mdi-school" color="indigo" size="large"></v-icon>
                    </template>
                    <v-card-title class="text-h5 font-weight-bold">{{ summary.total_students }}</v-card-title>
                    <v-card-subtitle>ນັກຮຽນທັງໝົດ</v-card-subtitle>
                </v-card-item>
            </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
            <v-card elevation="2" rounded="lg" class="pa-2 h-100">
                <v-card-item>
                    <template v-slot:prepend>
                        <v-icon icon="mdi-account-tie" color="teal" size="large"></v-icon>
                    </template>
                    <v-card-title class="text-h5 font-weight-bold">{{ summary.total_teachers }}</v-card-title>
                    <v-card-subtitle>ຄູສອນທັງໝົດ</v-card-subtitle>
                </v-card-item>
            </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
            <v-card elevation="2" rounded="lg" class="pa-2 h-100">
                <v-card-item>
                    <template v-slot:prepend>
                        <v-icon icon="mdi-calendar-check" color="success" size="large"></v-icon>
                    </template>
                    <v-card-title class="text-h5 font-weight-bold">{{ summary.attendance_rate }}%</v-card-title>
                    <v-card-subtitle>ອັດຕາການມາຮຽນມື້ນີ້</v-card-subtitle>
                </v-card-item>
            </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
            <v-card elevation="2" rounded="lg" class="pa-2 h-100">
                <v-card-item>
                    <template v-slot:prepend>
                        <v-icon icon="mdi-file-document-edit" color="orange" size="large"></v-icon>
                    </template>
                    <v-card-title class="text-h5 font-weight-bold">{{ summary.total_assignments }}</v-card-title>
                    <v-card-subtitle>ວຽກບ້ານສະສົມ</v-card-subtitle>
                </v-card-item>
            </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <v-col cols="12" md="7">
          <v-card elevation="2" rounded="lg" class="h-100">
            <v-card-title class="d-flex justify-space-between align-center">
              <span>ອັດຕາການມາຮຽນແຍກຕາມຫ້ອງ (%)</span>
              <v-btn icon="mdi-refresh" variant="text" @click="fetchData"></v-btn>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-6">
              <div v-for="cls in classStats" :key="cls.class_name" class="mb-5">
                <div class="d-flex justify-space-between mb-1">
                  <span class="font-weight-medium">{{ cls.class_name }}</span>
                  <span :class="getColorText(cls.attendance_rate)">{{ cls.attendance_rate }}%</span>
                </div>
                <v-progress-linear
                  :model-value="cls.attendance_rate"
                  :color="getColor(cls.attendance_rate)"
                  height="12"
                  rounded
                  striped
                ></v-progress-linear>
              </div>
              <div v-if="classStats.length === 0" class="text-center text-grey">
                  ບໍ່ມີຂໍ້ມູນການເຊັກຊື່ສຳລັບມື້ນີ້
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="5">
          <v-card elevation="2" rounded="lg" class="h-100">
            <v-card-title>ລະດັບຄະແນນລວມທັງໝົດ</v-card-title>
            <v-divider></v-divider>
            <v-card-text class="d-flex flex-column align-center justify-center py-10">
              <v-progress-circular
                :model-value="75"
                :size="180"
                :width="25"
                color="indigo"
              >
                <div class="text-center">
                  <div class="text-h4 font-weight-bold">75%</div>
                  <div class="text-caption">ຄະແນນສະເລ່ຍ</div>
                </div>
              </v-progress-circular>
              
              <v-list class="mt-6 w-100" density="compact">
                <v-list-item title="ດີເລີດ (A/B)" prepend-icon="mdi-circle" base-color="indigo"></v-list-item>
                <v-list-item title="ປານກາງ (C/D)" prepend-icon="mdi-circle" base-color="orange"></v-list-item>
                <v-list-item title="ອ່ອນ (F)" prepend-icon="mdi-circle" base-color="red"></v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// Import API ທີ່ເຮົາຫາກໍ່ສ້າງ
import { getDashboardSummary, getClassAttendanceStats } from '../../services/api';

const loading = ref(false);
const summary = ref({
  total_students: 0,
  total_teachers: 0,
  attendance_rate: 0,
  total_assignments: 0
});
const classStats = ref([]);

const fetchData = async () => {
  loading.value = true;
  try {
    // 1. ດຶງຂໍ້ມູນສັງລວມ (Summary)
    const sumRes = await getDashboardSummary();
    summary.value = sumRes.data;

    // 2. ດຶງຂໍ້ມູນການມາຮຽນແຍກຫ້ອງ
    const classRes = await getClassAttendanceStats();
    classStats.value = classRes.data;

  } catch (error) {
    console.error("Failed to load dashboard data:", error);
  } finally {
    loading.value = false;
  }
};

const getColor = (rate) => {
    if (rate >= 90) return 'success';
    if (rate >= 70) return 'warning';
    return 'error';
};

const getColorText = (rate) => {
    if (rate >= 90) return 'text-success';
    if (rate >= 70) return 'text-warning';
    return 'text-error';
};

onMounted(fetchData);
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}
.v-card:hover {
  transform: translateY(-4px);
}
</style>