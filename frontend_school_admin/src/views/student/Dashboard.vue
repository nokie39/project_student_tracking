<template>
  <v-container fluid class="bg-grey-lighten-4 fill-height align-start pa-0">
    
    <div v-if="loading" class="d-flex justify-center align-center w-100" style="height: 100vh;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <div v-else class="w-100">
      <v-card color="primary" rounded="b-xl" class="pa-6 pb-10 w-100" elevation="4">
        <div class="d-flex align-center">
          <v-avatar size="60" class="border-2 mr-4" color="white">
            <v-img src="https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Prescription02&hairColor=Black&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Happy&eyebrowType=Default&mouthType=Smile&skinColor=Light" alt="Profile"></v-img>
          </v-avatar>
          <div>
            <div class="text-caption text-blue-lighten-4">ສະບາຍດີ, ນັກຮຽນເກັ່ງ!</div>
            <div class="text-h5 font-weight-bold text-white">
              {{ dashboardData.student_info?.name || 'Loading...' }}
            </div>
            <div class="text-caption text-white opacity-80">
              {{ dashboardData.student_info?.class_name || '...' }} | {{ dashboardData.student_info?.code }}
            </div>
          </div>
          <v-spacer></v-spacer>
          <v-btn icon="mdi-bell-outline" variant="text" color="white"></v-btn>
        </div>
      </v-card>

      <v-row class="px-4 mt-n8" no-gutters>
        <v-col cols="12">
          <v-card class="mx-auto rounded-xl" elevation="3">
            <v-row no-gutters class="py-3">
              <v-col cols="4" class="text-center border-e">
                <div class="text-h6 font-weight-bold text-success">98%</div>
                <div class="text-caption text-grey">ການມາຮຽນ</div>
              </v-col>
              
              <v-col cols="4" class="text-center border-e">
                <div class="text-h6 font-weight-bold text-warning">
                  {{ dashboardData.assignments?.length || 0 }}
                </div>
                <div class="text-caption text-grey">ວຽກຄ້າງສົ່ງ</div>
              </v-col>
              
              <v-col cols="4" class="text-center">
                <div class="text-h6 font-weight-bold text-primary">
                  {{ dashboardData.student_info?.total_points || 0 }}
                </div>
                <div class="text-caption text-grey">ຄະແນນພຶດຕິກຳ</div>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <v-container class="mt-4 px-4">
        <div class="text-subtitle-1 font-weight-bold mb-3 text-grey-darken-3">ເມນູຫຼັກ</div>
        <v-row>
          <v-col cols="6" v-for="(menu, i) in menus" :key="i">
            <v-card 
              @click="$router.push(menu.route)" 
              class="pa-4 text-center rounded-xl d-flex flex-column align-center justify-center menu-card"
              elevation="1"
              height="120"
              color="white"
            >
              <v-avatar :color="menu.color" size="50" class="mb-2">
                <v-icon color="white" size="28">{{ menu.icon }}</v-icon>
              </v-avatar>
              <div class="text-body-2 font-weight-bold text-grey-darken-2">{{ menu.title }}</div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-container class="px-4 pb-6">
        <div class="d-flex justify-space-between align-center mb-3">
          <div class="text-subtitle-1 font-weight-bold text-grey-darken-3">
            ຕາຕະລາງມື້ນີ້ ({{ getDayName() }})
          </div>
          <v-btn variant="text" size="small" color="primary" @click="$router.push('/student/schedule')">
            ເບິ່ງທັງໝົດ
          </v-btn>
        </div>

        <v-card v-if="dashboardData.schedule && dashboardData.schedule.length > 0" class="rounded-xl" elevation="1">
          <v-list lines="two" class="rounded-xl">
            <v-list-item 
              v-for="sub in dashboardData.schedule" 
              :key="sub.id" 
              :title="sub.subject_name"
            >
              <template v-slot:subtitle>
                <div class="d-flex align-center mt-1">
                  <v-icon size="small" start class="mr-1">mdi-clock-outline</v-icon>
                  {{ formatTime(sub.start_time) }} - {{ formatTime(sub.end_time) }}
                  <span class="mx-2">|</span>
                  <v-icon size="small" start class="mr-1">mdi-door-open</v-icon>
                  {{ sub.room }}
                </div>
              </template>
              <template v-slot:prepend>
                <v-avatar color="primary" variant="tonal" rounded>
                  <v-icon color="primary">mdi-book-open-variant</v-icon>
                </v-avatar>
              </template>
            </v-list-item>
          </v-list>
        </v-card>

        <v-alert v-else type="info" variant="tonal" class="rounded-xl text-center">
          <v-icon size="40" class="mb-2">mdi-emoticon-happy-outline</v-icon>
          <div>ມື້ນີ້ບໍ່ມີຕາຕະລາງຮຽນ (ຫຼື ວັນພັກ) 🎉</div>
        </v-alert>
      </v-container>
    </div>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// ✅ Import API
import api from '../../services/api'; 

const loading = ref(true);
const dashboardData = ref({
  student_info: {},
  assignments: [],
  schedule: []
});

const menus = [
  { title: 'ວຽກບ້ານ', icon: 'mdi-book-edit', color: 'orange', route: '/student/assignments' },
  { title: 'ຕາຕະລາງຮຽນ', icon: 'mdi-calendar-clock', color: 'blue', route: '/student/schedule' },
  { title: 'ປະຫວັດຄະແນນ', icon: 'mdi-chart-line', color: 'green', route: '/student/grades' }, // ໜ້ານີ້ຍັງບໍ່ສ້າງ
  { title: 'ຂໍ້ມູນສ່ວນໂຕ', icon: 'mdi-account', color: 'purple', route: '/student/profile' }, // ໜ້ານີ້ຍັງບໍ່ສ້າງ
];

// Fetch Data ຈາກ Backend
const fetchData = async () => {
  try {
    const res = await api.get('/students/dashboard');
    dashboardData.value = res.data;
  } catch (error) {
    console.error("Error fetching dashboard:", error);
  } finally {
    loading.value = false;
  }
};

// Utils
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  return timeStr.substring(0, 5); // ຕັດວິນາທີອອກ (08:30:00 -> 08:30)
};

const getDayName = () => {
  const days = ['ອາທິດ', 'ຈັນ', 'ອັງຄານ', 'ພຸດ', 'ພະຫັດ', 'ສຸກ', 'ເສົາ'];
  return days[new Date().getDay()];
};

onMounted(fetchData);
</script>

<style scoped>
.v-card--rounded-b-xl {
  border-bottom-left-radius: 32px !important;
  border-bottom-right-radius: 32px !important;
}

.menu-card {
  transition: transform 0.2s;
}
.menu-card:active {
  transform: scale(0.95);
}
</style>