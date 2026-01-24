<template>
  <v-container fluid class="fill-height align-start bg-grey-lighten-4">
    
    <v-row>
      <v-col cols="12">
        <h2 class="text-h4 font-weight-bold text-blue-grey-darken-3">
          Dashboard ຜູ້ບໍລິຫານ 🏫
        </h2>
        <div class="text-subtitle-1 text-grey-darken-1">
          ພາບລວມປະຈຳວັນທີ: {{ today }}
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl pa-4" elevation="2">
          <div class="d-flex align-center">
            <v-avatar color="blue-lighten-5" size="50" class="text-blue">
              <v-icon size="30">mdi-account-group</v-icon>
            </v-avatar>
            <div class="ml-3">
              <div class="text-caption text-grey">ນັກຮຽນທັງໝົດ</div>
              <div class="text-h5 font-weight-bold">{{ stats.total_students }}</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl pa-4" elevation="2">
          <div class="d-flex align-center">
            <v-avatar color="green-lighten-5" size="50" class="text-green">
              <v-icon size="30">mdi-check-circle</v-icon>
            </v-avatar>
            <div class="ml-3">
              <div class="text-caption text-grey">ມາຮຽນມື້ນີ້</div>
              <div class="text-h5 font-weight-bold">{{ stats.attendance_rate }}%</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl pa-4" elevation="2">
          <div class="d-flex align-center">
            <v-avatar color="orange-lighten-5" size="50" class="text-orange">
              <v-icon size="30">mdi-human-male-board</v-icon>
            </v-avatar>
            <div class="ml-3">
              <div class="text-caption text-grey">ຄູອາຈານ</div>
              <div class="text-h5 font-weight-bold">{{ stats.total_teachers }}</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="8">
        <v-card class="rounded-xl" elevation="2">
          <v-card-title class="d-flex align-center py-4 px-6 border-b">
            <span>📊 ສະຖານະການກວດກາປະຈຳວັນ</span>
            <v-spacer></v-spacer>
            <v-btn icon size="small" variant="text" @click="fetchData">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          
          <v-table>
            <thead>
              <tr class="bg-grey-lighten-5">
                <th class="text-left">ຫ້ອງຮຽນ</th>
                <th class="text-left">ຄູປະຈຳຫ້ອງ</th>
                <th class="text-center">ສະຖານະ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cls in classStatus" :key="cls.class_name">
                <td class="font-weight-bold">{{ cls.class_name }}</td>
                <td>
                  <div class="d-flex align-center">
                    <v-avatar size="30" color="grey-lighten-3" class="mr-2">
                      <v-icon size="16">mdi-account</v-icon>
                    </v-avatar>
                    {{ cls.teacher_name }}
                  </div>
                </td>
                <td class="text-center">
                  <v-chip 
                    v-if="cls.status === 'CHECKED'" 
                    color="success" 
                    variant="tonal" 
                    size="small"
                  >
                    <v-icon start size="small">mdi-check</v-icon> ກວດແລ້ວ
                  </v-chip>
                  <v-chip 
                    v-else 
                    color="error" 
                    variant="tonal" 
                    size="small"
                    class="ani-pulse"
                  >
                    <v-icon start size="small">mdi-alert</v-icon> ຍັງບໍ່ກວດ
                  </v-chip>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="rounded-xl h-100" elevation="2">
          <v-card-title class="py-4 px-6 border-b">🔔 ແຈ້ງເຕືອນລ່າສຸດ</v-card-title>
          <v-card-text class="pa-0">
             <div class="text-center py-10 text-grey">
               <v-icon size="40">mdi-bell-sleep</v-icon>
               <div class="mt-2 text-caption">ບໍ່ມີການແຈ້ງເຕືອນສຳຄັນ</div>
             </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../../services/api';

const stats = ref({ total_students: 0, attendance_rate: 0, total_teachers: 0 });
const classStatus = ref([]);

const today = computed(() => {
  return new Date().toLocaleDateString('lo-LA', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
});

const fetchData = async () => {
  try {
    const resStats = await api.get('/head/daily-stats');
    stats.value = resStats.data;

    const resMonitor = await api.get('/head/attendance-monitor');
    classStatus.value = resMonitor.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(fetchData);
</script>

<style scoped>
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
.ani-pulse {
  animation: pulse 2s infinite;
}
</style>