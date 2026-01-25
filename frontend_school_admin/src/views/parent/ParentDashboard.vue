<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <div class="w-100 bg-gradient-indigo pt-8 pb-16 px-6 rounded-b-xl shadow-lg position-relative">
      <div class="text-white">
        <div class="text-subtitle-1 opacity-80 mb-1">ຕິດຕາມການຮຽນຂອງ:</div>
        <div class="text-h4 font-weight-bold">{{ dashboardData.student_info?.name || '...' }}</div>
        <div class="d-flex align-center mt-2 opacity-90">
           <v-chip size="small" color="white" variant="flat" class="text-indigo font-weight-bold mr-2">
              {{ dashboardData.student_info?.class_name || 'N/A' }}
           </v-chip>
           <span class="text-caption">ລະຫັດ: {{ dashboardData.student_info?.code }}</span>
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
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card class="rounded-xl elevation-3 h-100" @click="$router.push('/parent/assignments')" v-ripple>
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="orange-lighten-5" size="56" class="mr-4 rounded-lg">
                <v-icon color="orange" size="32">mdi-clipboard-alert</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-grey font-weight-bold text-uppercase">ວຽກຄ້າງສົ່ງ</div>
                <div class="text-h5 font-weight-bold text-orange-darken-2">
                  {{ dashboardData.assignments?.length || 0 }} <span class="text-caption text-grey">ລາຍການ</span>
                </div>
              </div>
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
                <v-icon start color="indigo">mdi-calendar-today</v-icon> ຕາຕະລາງມື້ນີ້
             </h3>
          </div>

          <v-card rounded="xl" elevation="2">
            <div v-if="loading" class="pa-6 text-center"><v-progress-circular indeterminate color="indigo"></v-progress-circular></div>
            
            <v-list v-else-if="dashboardData.schedule?.length > 0" lines="two" class="py-0 rounded-xl">
                <template v-for="(item, index) in dashboardData.schedule" :key="item.id">
                    <v-list-item class="py-3">
                        <template v-slot:prepend>
                           <div class="d-flex flex-column align-center justify-center mr-4 bg-indigo-lighten-5 rounded-lg" style="width: 60px; height: 60px;">
                              <span class="text-body-2 font-weight-bold text-indigo-darken-2">{{ formatTime(item.start_time) }}</span>
                           </div>
                        </template>
                        <v-list-item-title class="text-subtitle-1 font-weight-bold text-indigo mb-1">{{ item.subject_name }}</v-list-item-title>
                        <v-list-item-subtitle>
                           <v-icon size="small" start>mdi-map-marker</v-icon> {{ item.room || '-' }} • 
                           <v-icon size="small" start>mdi-account</v-icon> {{ item.teacher_name || '-' }}
                        </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider v-if="index < dashboardData.schedule.length - 1" inset></v-divider>
                </template>
            </v-list>

            <div v-else class="pa-8 text-center text-grey">
               <v-icon size="60" color="grey-lighten-3" class="mb-2">mdi-school-outline</v-icon>
               <div class="text-body-1">ມື້ນີ້ບໍ່ມີການຮຽນ-ການສອນ</div>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" md="5">
          <div class="d-flex justify-space-between align-center mb-3">
             <h3 class="text-h6 font-weight-bold text-grey-darken-3">
                <v-icon start color="orange">mdi-bell-ring</v-icon> ວຽກທີ່ຕ້ອງສົ່ງ
             </h3>
             <v-btn variant="text" color="indigo" size="small" to="/parent/assignments">ເບິ່ງທັງໝົດ</v-btn>
          </div>

          <div v-if="dashboardData.assignments?.length > 0">
             <v-card 
               v-for="assign in dashboardData.assignments" 
               :key="assign.id"
               rounded="xl" 
               elevation="2" 
               class="mb-3 border-s-lg pl-1"
               style="border-left-color: #FF5252 !important;"
             >
                <v-card-text class="py-3">
                   <div class="text-subtitle-2 font-weight-bold text-truncate">{{ assign.title }}</div>
                   <div class="d-flex justify-space-between align-center mt-1">
                      <div class="text-caption text-grey">ສົ່ງກ່ອນ: {{ formatDate(assign.due_date) }}</div>
                      <v-chip size="x-small" color="error" variant="flat">ຄ້າງສົ່ງ</v-chip>
                   </div>
                </v-card-text>
             </v-card>
          </div>
          
          <div v-else class="text-center pa-6 border rounded-xl bg-white border-dashed">
             <v-icon size="40" color="success" class="mb-2">mdi-check-circle-outline</v-icon>
             <div class="text-subtitle-2">ລູກຂອງທ່ານສົ່ງວຽກຄົບແລ້ວ</div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getChildDashboard } from '../../services/api';

const loading = ref(true);
const dashboardData = ref({ student_info: {}, assignments: [], schedule: [] });

onMounted(async () => {
    const childId = localStorage.getItem('selectedChildId');
    if (!childId) return; // ຖ້າຍັງບໍ່ເລືອກລູກ (Layout ຈະຈັດການໃຫ້)

    try {
        const res = await getChildDashboard(childId);
        dashboardData.value = res.data;
    } catch (error) {
        console.error("Error:", error);
    } finally {
        loading.value = false;
    }
});

const formatTime = (t) => t ? t.substring(0, 5) : '';
const formatDate = (d) => d ? new Date(d).toLocaleDateString('lo-LA', {day: 'numeric', month: 'short'}) : '';
</script>

<style scoped>
.bg-gradient-indigo { background: linear-gradient(135deg, #3949AB 0%, #5C6BC0 100%); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05); }
.border-s-lg { border-left-width: 4px !important; }
</style>