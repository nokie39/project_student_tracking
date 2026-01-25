<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <div class="w-100 bg-gradient-primary pt-8 pb-16 px-6 rounded-b-xl shadow-lg position-relative">
      <div class="d-flex justify-space-between align-center">
        <div class="text-white">
          <div class="text-subtitle-1 opacity-80 mb-1">ຍິນດີຕ້ອນຮັບກັບມາ,</div>
          <div class="text-h4 font-weight-bold">{{ dashboardData.student_info?.name || 'Loading...' }}</div>
          <div class="d-flex align-center mt-2 opacity-90">
            <v-icon size="small" class="mr-1">mdi-card-account-details-outline</v-icon>
            <span class="mr-3">{{ dashboardData.student_info?.code }}</span>
            <v-icon size="small" class="mr-1">mdi-school-outline</v-icon>
            <span>{{ dashboardData.student_info?.class_name || '-' }}</span>
          </div>
        </div>
        
        <div style="width: 150px;" class="d-none d-sm-block">
           <v-select
              v-model="selectedSemester"
              :items="semesters"
              item-title="title"
              item-value="id"
              label="ສົກຮຽນ/ພາກ"
              variant="solo"
              density="compact"
              hide-details
              bg-color="white"
              class="rounded-lg text-body-2"
              @update:model-value="fetchDashboard"
           ></v-select>
        </div>
      </div>
    </div>

    <v-container class="mt-n12 px-4">
      <v-row>
        <v-col cols="12" sm="4">
          <v-card class="rounded-xl elevation-3 h-100">
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="green-lighten-5" size="56" class="mr-4 rounded-lg">
                <v-icon color="green" size="32">mdi-star-face</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-grey font-weight-bold text-uppercase">ຄະແນນພຶດຕິກຳ</div>
                <div class="text-h5 font-weight-bold text-green-darken-1">
                  {{ dashboardData.student_info?.total_points || 0 }}
                  <span class="text-caption text-grey">ຄະແນນ</span>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card class="rounded-xl elevation-3 h-100" @click="$router.push('/student/assignments')" v-ripple>
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="orange-lighten-5" size="56" class="mr-4 rounded-lg">
                <v-icon color="orange" size="32">mdi-clipboard-text-clock</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-grey font-weight-bold text-uppercase">ວຽກບ້ານຄ້າງສົ່ງ</div>
                <div class="text-h5 font-weight-bold text-orange-darken-2">
                  {{ dashboardData.assignments?.length || 0 }}
                  <span class="text-caption text-grey">ວຽກ</span>
                </div>
              </div>
              <v-spacer></v-spacer>
              <v-icon color="grey-lighten-1">mdi-chevron-right</v-icon>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card class="rounded-xl elevation-3 h-100" @click="$router.push('/student/grades')" v-ripple>
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="blue-lighten-5" size="56" class="mr-4 rounded-lg">
                <v-icon color="blue" size="32">mdi-chart-line</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-grey font-weight-bold text-uppercase">ຜົນການຮຽນ</div>
                <div class="text-h5 font-weight-bold text-blue-darken-2">
                  GPA
                  <span class="text-caption text-grey">View</span>
                </div>
              </div>
              <v-spacer></v-spacer>
              <v-icon color="grey-lighten-1">mdi-chevron-right</v-icon>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container class="mt-2 px-4 pb-10">
      <v-row>
        
        <v-col cols="12" md="7">
          <div class="d-flex justify-space-between align-center mb-3">
            <h3 class="text-h6 font-weight-bold text-grey-darken-3">
              <v-icon start color="primary">mdi-calendar-today</v-icon> ຕາຕະລາງມື້ນີ້
            </h3>
            <v-btn variant="text" color="primary" size="small" to="/student/schedule">ເບິ່ງທັງໝົດ</v-btn>
          </div>

          <v-card rounded="xl" elevation="2" class="overflow-hidden">
            <div v-if="loading" class="pa-6 text-center">
               <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
            
            <div v-else-if="dashboardData.schedule?.length > 0">
               <v-list lines="two" class="py-0">
                  <template v-for="(item, index) in dashboardData.schedule" :key="item.id">
                     <v-list-item class="py-3">
                        <template v-slot:prepend>
                           <div class="d-flex flex-column align-center justify-center mr-4 bg-blue-lighten-5 rounded-lg" style="width: 60px; height: 60px;">
                              <span class="text-body-2 font-weight-bold text-blue-darken-2">{{ formatTime(item.start_time) }}</span>
                              <span class="text-caption text-grey text-center" style="font-size: 10px; line-height: 1;">ເຖິງ<br>{{ formatTime(item.end_time) }}</span>
                           </div>
                        </template>
                        
                        <v-list-item-title class="text-subtitle-1 font-weight-bold text-primary mb-1">
                           {{ item.subject_name }}
                        </v-list-item-title>
                        <v-list-item-subtitle class="d-flex align-center">
                           <v-icon size="small" start>mdi-map-marker</v-icon> {{ item.room || 'N/A' }}
                           <span class="mx-2">•</span>
                           <v-icon size="small" start>mdi-account</v-icon> {{ item.teacher_name || 'N/A' }}
                        </v-list-item-subtitle>
                     </v-list-item>
                     <v-divider v-if="index < dashboardData.schedule.length - 1" inset></v-divider>
                  </template>
               </v-list>
            </div>

            <div v-else class="pa-8 text-center text-grey">
               <v-icon size="60" color="grey-lighten-3" class="mb-2">mdi-calendar-blank</v-icon>
               <div class="text-body-1">ມື້ນີ້ບໍ່ມີການຮຽນ-ການສອນ</div>
               <div class="text-caption">ພັກຜ່ອນໃຫ້ສະບາຍໃຈ!</div>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" md="5">
          <div class="d-flex justify-space-between align-center mb-3">
            <h3 class="text-h6 font-weight-bold text-grey-darken-3">
              <v-icon start color="orange">mdi-bell-ring</v-icon> ສົ່ງດ່ວນ (Upcoming)
            </h3>
            <v-btn variant="text" color="primary" size="small" to="/student/assignments">ທັງໝົດ</v-btn>
          </div>

          <div v-if="dashboardData.assignments?.length > 0">
             <v-card 
               v-for="assign in dashboardData.assignments" 
               :key="assign.id"
               rounded="xl" 
               elevation="2" 
               class="mb-3 border-s-lg pl-1"
               :style="{ 'border-left-color': isOverdue(assign.due_date) ? '#FF5252 !important' : '#FB8C00 !important' }"
               @click="$router.push('/student/assignments')"
               v-ripple
             >
                <v-card-text class="py-3">
                   <div class="d-flex justify-space-between align-start mb-1">
                      <div class="text-subtitle-2 font-weight-bold text-truncate pr-2">{{ assign.title }}</div>
                      <v-chip size="x-small" :color="isOverdue(assign.due_date) ? 'error' : 'warning'" variant="flat" class="font-weight-bold">
                         {{ getRelativeTime(assign.due_date) }}
                      </v-chip>
                   </div>
                   <div class="text-caption text-grey mb-2">{{ assign.class_name }}</div>
                   <div class="d-flex align-center text-caption text-grey-darken-1">
                      <v-icon size="small" start>mdi-clock-outline</v-icon>
                      ສົ່ງກ່ອນ: {{ formatDate(assign.due_date) }}
                   </div>
                </v-card-text>
             </v-card>
          </div>

          <div v-else class="text-center pa-6 border rounded-xl bg-white border-dashed">
             <v-icon size="40" color="success" class="mb-2">mdi-check-circle-outline</v-icon>
             <div class="text-subtitle-2 text-grey-darken-2">ບໍ່ມີວຽກຄ້າງສົ່ງ</div>
             <div class="text-caption text-grey">ທ່ານສົ່ງວຽກຄົບໝົດແລ້ວ!</div>
          </div>

        </v-col>
      </v-row>
    </v-container>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api'; // ໃຊ້ instance api ໂດຍກົງ ຫຼື import getStudentDashboardData

const loading = ref(true);
const dashboardData = ref({
    student_info: {},
    assignments: [],
    schedule: []
});

const semesters = [
  { id: 1, title: 'ພາກຮຽນ 1' },
  { id: 2, title: 'ພາກຮຽນ 2' }
];
const selectedSemester = ref(1);

const fetchDashboard = async () => {
  loading.value = true;
  try {
    // ✅ ສົ່ງ semester_id ໄປນຳ
    const res = await api.get(`/students/dashboard?semester_id=${selectedSemester.value}`);
    dashboardData.value = res.data;
  } catch (error) {
    console.error("Error loading dashboard:", error);
  } finally {
    loading.value = false;
  }
};

// --- Helpers ---
const formatTime = (timeStr) => timeStr ? timeStr.substring(0, 5) : '';

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('lo-LA', { day: 'numeric', month: 'short' });
};

const getRelativeTime = (dateStr) => {
    const due = new Date(dateStr);
    const now = new Date();
    const diff = due - now;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));

    if (diff < 0) return 'ກາຍກຳນົດ';
    if (days === 0) return 'ມື້ນີ້';
    if (days === 1) return 'ມື້ອື່ນ';
    return `ອີກ ${days} ມື້`;
};

const isOverdue = (dateStr) => new Date() > new Date(dateStr);

onMounted(fetchDashboard);
</script>

<style scoped>
.bg-gradient-primary {
    background: linear-gradient(135deg, #1565C0 0%, #42A5F5 100%);
}
.shadow-lg {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
.border-s-lg {
    border-left-width: 4px !important;
}
.border-dashed {
    border-style: dashed !important;
    border-color: #E0E0E0 !important;
}
</style>