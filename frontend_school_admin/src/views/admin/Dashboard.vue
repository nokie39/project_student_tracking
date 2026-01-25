<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <div class="w-100 bg-white pt-6 pb-6 px-6 rounded-xl elevation-1 mb-6">
      <div class="d-flex flex-wrap justify-space-between align-center">
        <div>
          <h2 class="text-h5 font-weight-bold text-grey-darken-3">
             <v-icon start color="primary">mdi-view-dashboard</v-icon> Admin Dashboard
          </h2>
          <div class="text-body-2 text-grey mt-1">
             ຍິນດີຕ້ອນຮັບສູ່ລະບົບຈັດການໂຮງຮຽນ (School Management System)
          </div>
        </div>
        <div class="text-right d-none d-sm-block">
           <div class="text-h6 font-weight-bold text-primary">{{ currentTime }}</div>
           <div class="text-caption text-grey">{{ currentDate }}</div>
        </div>
      </div>
    </div>

    <v-row>
       <v-col cols="12" sm="6" md="3">
          <v-card class="rounded-xl elevation-2 h-100 card-hover" color="blue-lighten-5">
             <v-card-text class="d-flex align-center pa-4">
                <v-avatar color="blue" size="56" class="rounded-lg elevation-2 mr-4">
                   <v-icon color="white" size="30">mdi-account-school</v-icon>
                </v-avatar>
                <div>
                   <div class="text-caption font-weight-bold text-blue-darken-3 text-uppercase">ນັກຮຽນທັງໝົດ</div>
                   <div class="text-h4 font-weight-bold text-grey-darken-3">
                      {{ stats.students }}
                   </div>
                </div>
             </v-card-text>
          </v-card>
       </v-col>

       <v-col cols="12" sm="6" md="3">
          <v-card class="rounded-xl elevation-2 h-100 card-hover" color="green-lighten-5">
             <v-card-text class="d-flex align-center pa-4">
                <v-avatar color="green" size="56" class="rounded-lg elevation-2 mr-4">
                   <v-icon color="white" size="30">mdi-human-male-board</v-icon>
                </v-avatar>
                <div>
                   <div class="text-caption font-weight-bold text-green-darken-3 text-uppercase">ຄູອາຈານ</div>
                   <div class="text-h4 font-weight-bold text-grey-darken-3">
                      {{ stats.teachers }}
                   </div>
                </div>
             </v-card-text>
          </v-card>
       </v-col>

       <v-col cols="12" sm="6" md="3">
          <v-card class="rounded-xl elevation-2 h-100 card-hover" color="orange-lighten-5">
             <v-card-text class="d-flex align-center pa-4">
                <v-avatar color="orange" size="56" class="rounded-lg elevation-2 mr-4">
                   <v-icon color="white" size="30">mdi-google-classroom</v-icon>
                </v-avatar>
                <div>
                   <div class="text-caption font-weight-bold text-orange-darken-3 text-uppercase">ຫ້ອງຮຽນ</div>
                   <div class="text-h4 font-weight-bold text-grey-darken-3">
                      {{ stats.classes }}
                   </div>
                </div>
             </v-card-text>
          </v-card>
       </v-col>

       <v-col cols="12" sm="6" md="3">
          <v-card class="rounded-xl elevation-2 h-100 card-hover" color="purple-lighten-5">
             <v-card-text class="d-flex align-center pa-4">
                <v-avatar color="purple" size="56" class="rounded-lg elevation-2 mr-4">
                   <v-icon color="white" size="30">mdi-account-group</v-icon>
                </v-avatar>
                <div>
                   <div class="text-caption font-weight-bold text-purple-darken-3 text-uppercase">ຜູ້ໃຊ້ລະບົບ</div>
                   <div class="text-h4 font-weight-bold text-grey-darken-3">
                      {{ stats.users }}
                   </div>
                </div>
             </v-card-text>
          </v-card>
       </v-col>
    </v-row>

    <v-row class="mt-4">
       
       <v-col cols="12" md="4">
          <v-card rounded="xl" elevation="2" class="h-100">
             <v-card-title class="font-weight-bold text-grey-darken-3 px-4 pt-4">
                <v-icon start color="grey">mdi-lightning-bolt</v-icon> ຈັດການດ່ວນ
             </v-card-title>
             <v-card-text class="pt-4">
                <v-btn block color="primary" variant="tonal" class="mb-3 justify-start" size="large" to="/admin/students">
                   <v-icon start>mdi-account-plus</v-icon> ເພີ່ມນັກຮຽນໃໝ່
                </v-btn>
                <v-btn block color="success" variant="tonal" class="mb-3 justify-start" size="large" to="/admin/users">
                   <v-icon start>mdi-account-key</v-icon> ຈັດການຜູ້ໃຊ້ (Users)
                </v-btn>
                <v-btn block color="orange" variant="tonal" class="mb-3 justify-start" size="large" to="/admin/classes">
                   <v-icon start>mdi-domain</v-icon> ຈັດການຫ້ອງຮຽນ
                </v-btn>
                <v-btn block color="info" variant="tonal" class="justify-start" size="large" to="/admin/academic">
                   <v-icon start>mdi-calendar-clock</v-icon> ຈັດຕາຕະລາງຮຽນ
                </v-btn>
             </v-card-text>
          </v-card>
       </v-col>

       <v-col cols="12" md="8">
          <v-card rounded="xl" elevation="2" class="h-100">
             <div class="d-flex justify-space-between align-center px-4 pt-4 mb-2">
                <v-card-title class="font-weight-bold text-grey-darken-3 pa-0">
                   <v-icon start color="grey">mdi-history</v-icon> ຜູ້ໃຊ້ງານຫຼ້າສຸດ
                </v-card-title>
                <v-btn variant="text" size="small" color="primary" to="/admin/users">ເບິ່ງທັງໝົດ</v-btn>
             </div>

             <v-divider></v-divider>

             <v-table class="bg-transparent">
                <thead>
                   <tr>
                      <th class="text-left font-weight-bold">ຊື່-ນາມສະກຸນ</th>
                      <th class="text-left font-weight-bold">ສິດ (Role)</th>
                      <th class="text-left font-weight-bold">ສະຖານະ</th>
                   </tr>
                </thead>
                <tbody>
                   <tr v-for="user in recentUsers" :key="user.id">
                      <td>
                         <div class="d-flex align-center py-2">
                            <v-avatar color="grey-lighten-3" size="32" class="mr-3">
                               <span class="text-subtitle-2 font-weight-bold text-grey-darken-3">{{ user.full_name?.charAt(0) || 'U' }}</span>
                            </v-avatar>
                            <div>
                               <div class="font-weight-bold text-body-2">{{ user.full_name }}</div>
                               <div class="text-caption text-grey">{{ user.username }}</div>
                            </div>
                         </div>
                      </td>
                      <td>
                         <v-chip size="x-small" :color="getRoleColor(user.role)" class="font-weight-bold text-uppercase">
                            {{ user.role }}
                         </v-chip>
                      </td>
                      <td>
                         <v-icon color="success" size="small">mdi-circle-medium</v-icon> Active
                      </td>
                   </tr>
                   <tr v-if="recentUsers.length === 0">
                      <td colspan="3" class="text-center py-4 text-grey">
                         <v-progress-circular indeterminate size="24" color="primary" v-if="loading"></v-progress-circular>
                         <span v-else>ບໍ່ມີຂໍ້ມູນ</span>
                      </td>
                   </tr>
                </tbody>
             </v-table>
          </v-card>
       </v-col>
    </v-row>

  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../../services/api';

const loading = ref(false);
const stats = ref({
    students: 0,
    teachers: 0,
    classes: 0,
    users: 0
});
const recentUsers = ref([]);

// Time Display
const currentTime = ref('');
const currentDate = ref('');
let timerInterval = null;

const updateTime = () => {
    const now = new Date();
    currentTime.value = now.toLocaleTimeString('lo-LA', { hour: '2-digit', minute: '2-digit' });
    currentDate.value = now.toLocaleDateString('lo-LA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
};

// Fetch Dashboard Data
const fetchData = async () => {
    loading.value = true;
    try {
        // 1. Get Users count & Recent users
        const usersRes = await api.get('/users'); 
        const allUsers = usersRes.data;
        
        // Calculate Stats manually
        stats.value.users = allUsers.length;
        stats.value.students = allUsers.filter(u => u.role === 'student').length;
        stats.value.teachers = allUsers.filter(u => u.role === 'teacher').length;
        
        // Recent Users (Take last 5)
        recentUsers.value = allUsers.slice(-5).reverse();

        // 2. Get Classes count (✅ ແກ້ໄຂ URL ໃຫ້ຖືກຕ້ອງ)
        const classesRes = await api.get('/academic/classes');
        stats.value.classes = classesRes.data.length;

    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    } finally {
        loading.value = false;
    }
};

const getRoleColor = (role) => {
    switch(role) {
        case 'admin': return 'red';
        case 'teacher': return 'green';
        case 'student': return 'blue';
        case 'parent': return 'purple';
        default: return 'grey';
    }
};

onMounted(() => {
    updateTime();
    timerInterval = setInterval(updateTime, 1000);
    fetchData();
});

onUnmounted(() => {
    if (timerInterval) clearInterval(timerInterval);
});
</script>

<style scoped>
.card-hover {
    transition: transform 0.2s, box-shadow 0.2s;
}
.card-hover:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}
</style>