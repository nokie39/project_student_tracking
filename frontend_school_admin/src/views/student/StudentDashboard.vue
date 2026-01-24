<template>
  <v-container class="py-6">
    <div v-if="loading" class="d-flex justify-center align-center" style="height: 400px;">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <div v-else>
      <v-row class="mb-4">
        <v-col cols="12">
          <v-card class="bg-primary text-white pa-6" rounded="xl" elevation="4">
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h4 font-weight-bold">ສະບາຍດີ, {{ dashboardData.student_info.name }} 👋</div>
                <div class="text-subtitle-1 mt-1 opacity-80">
                  ຫ້ອງ: {{ dashboardData.student_info.class_name }} | ລະຫັດ: {{ dashboardData.student_info.code }}
                </div>
              </div>
              <div class="text-center bg-white text-primary pa-4 rounded-lg">
                <div class="text-h4 font-weight-black">{{ dashboardData.student_info.total_points }}</div>
                <div class="text-caption font-weight-bold">ຄະແນນພຶດຕິກຳ</div>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <v-card height="100%" rounded="lg" elevation="2">
            <v-card-title class="d-flex align-center">
              <v-icon start color="error">mdi-alert-circle</v-icon>
              ວຽກບ້ານທີ່ໃກ້ຮອດກຳນົດ
            </v-card-title>
            <v-divider></v-divider>
            
            <v-list v-if="dashboardData.assignments.length > 0" lines="two">
              <v-list-item
                v-for="work in dashboardData.assignments"
                :key="work.id"
                :prepend-icon="'mdi-file-document-edit'"
              >
                <v-list-item-title class="font-weight-bold">{{ work.title }}</v-list-item-title>
                <v-list-item-subtitle>
                  ກຳນົດສົ່ງ: <span class="text-error">{{ formatDate(work.due_date) }}</span>
                </v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn size="small" variant="tonal" color="primary" :to="'/student/assignments'">
                    ເບິ່ງ
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>

            <div v-else class="text-center pa-6 text-grey">
              <v-icon size="50" class="mb-2">mdi-check-circle-outline</v-icon>
              <div>ສຸດຍອດ! ບໍ່ມີວຽກບ້ານຄ້າງ</div>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card height="100%" rounded="lg" elevation="2">
            <v-card-title class="d-flex align-center">
              <v-icon start color="info">mdi-calendar-clock</v-icon>
              ຕາຕະລາງຮຽນ ({{ getDayName() }})
            </v-card-title>
            <v-divider></v-divider>

            <v-timeline density="compact" align="start" side="end" class="pa-4" v-if="dashboardData.schedule.length > 0">
              <v-timeline-item
                v-for="sub in dashboardData.schedule"
                :key="sub.id"
                dot-color="info"
                size="small"
              >
                <div class="d-flex justify-space-between">
                  <strong>{{ sub.subject_name }}</strong>
                  <span class="text-caption">{{ formatTime(sub.start_time) }} - {{ formatTime(sub.end_time) }}</span>
                </div>
                <div class="text-caption text-grey">{{ sub.teacher_name }} | ຫ້ອງ {{ sub.room }}</div>
              </v-timeline-item>
            </v-timeline>

            <div v-else class="text-center pa-6 text-grey">
              <v-icon size="50" class="mb-2">mdi-school-outline</v-icon>
              <div>ມື້ນີ້ບໍ່ມີຕາຕະລາງຮຽນ</div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api'; // ⚠️ ກວດເບິ່ງ path ຂອງ api service ເຈົ້າ

const loading = ref(true);
const dashboardData = ref({
  student_info: {},
  assignments: [],
  schedule: []
});

const fetchDashboard = async () => {
  try {
    // ຍິງໄປ API ທີ່ເຮົາຫາກໍ່ສ້າງໃນ Backend (/students/dashboard)
    const res = await api.get('/students/dashboard');
    dashboardData.value = res.data;
  } catch (error) {
    console.error("Error fetching dashboard:", error);
  } finally {
    loading.value = false;
  }
};

// Helpers
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('lo-LA', { day: 'numeric', month: 'short' });
};
const formatTime = (timeStr) => {
  return timeStr ? timeStr.substring(0, 5) : '';
};
const getDayName = () => {
  const days = ['ອາທິດ', 'ຈັນ', 'ອັງຄານ', 'ພຸດ', 'ພະຫັດ', 'ສຸກ', 'ເສົາ'];
  return days[new Date().getDay()];
};

onMounted(fetchDashboard);
</script>