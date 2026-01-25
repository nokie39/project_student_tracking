<template>
  <v-container fluid class="fill-height align-start bg-grey-lighten-5 pa-0">
    
    <div class="w-100 bg-gradient-primary pt-12 pb-16 text-center rounded-b-xxl elevation-3 position-relative">
      
      <v-btn 
        icon="mdi-arrow-left" 
        variant="text" 
        color="white" 
        class="position-absolute top-0 left-0 mt-4 ml-2" 
        @click="$router.back()"
      ></v-btn>

      <div class="position-relative d-inline-block">
        <v-avatar size="110" class="border-4 border-white elevation-5 bg-white">
           <v-img 
             :src="`https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Prescription02&hairColor=Black&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Happy&eyebrowType=Default&mouthType=Smile&skinColor=Light`"
             alt="Avatar"
           ></v-img>
        </v-avatar>
        <v-badge
          color="success"
          icon="mdi-check"
          location="bottom end"
          offset-x="10"
          offset-y="10"
          class="position-absolute bottom-0 right-0"
        ></v-badge>
      </div>

      <div class="text-h5 font-weight-bold text-white mt-3 text-shadow">
        {{ profile.full_name || 'Loading...' }}
      </div>
      <div class="text-subtitle-2 text-blue-lighten-4 font-weight-medium">
        ID: {{ profile.student_code || '...' }}
      </div>
    </div>

    <v-container class="mt-n16 px-4" style="max-width: 600px;">
      
      <v-card class="rounded-xl pa-0 mb-4 overflow-hidden" elevation="2">
         <v-row no-gutters>
            <v-col cols="6" class="border-e">
               <div class="pa-4 text-center">
                  <div class="text-caption text-grey font-weight-bold text-uppercase">ຫ້ອງຮຽນ</div>
                  <div class="text-h6 font-weight-bold text-primary">{{ profile.class_name || '-' }}</div>
                  <div class="text-caption text-grey-lighten-1">{{ profile.academic_year || 'ສົກຮຽນປັດຈຸບັນ' }}</div>
               </div>
            </v-col>
            <v-col cols="6">
               <div class="pa-4 text-center">
                  <div class="text-caption text-grey font-weight-bold text-uppercase">ຄະແນນພຶດຕິກຳ</div>
                  <div class="text-h6 font-weight-bold text-success">{{ profile.total_points }}</div>
                  <div class="text-caption text-grey-lighten-1">ຄະແນນສະສົມ</div>
               </div>
            </v-col>
         </v-row>
      </v-card>

      <div class="text-subtitle-2 text-grey-darken-1 font-weight-bold ml-1 mb-2">ຂໍ້ມູນສ່ວນຕົວ</div>
      <v-card class="rounded-xl pa-4 mb-4" elevation="1">
        <v-list density="compact" class="pa-0">
           
           <v-list-item class="px-0">
              <template v-slot:prepend>
                 <v-avatar color="blue-lighten-5" size="40" class="mr-3">
                    <v-icon color="blue" size="20">mdi-human-male-child</v-icon>
                 </v-avatar>
              </template>
              <v-list-item-title class="font-weight-bold">ຜູ້ປົກຄອງ</v-list-item-title>
              <v-list-item-subtitle>{{ profile.details?.parent || 'ບໍ່ມີຂໍ້ມູນ' }}</v-list-item-subtitle>
           </v-list-item>

           <v-divider class="my-2 border-dashed"></v-divider>

           <v-list-item class="px-0">
              <template v-slot:prepend>
                 <v-avatar color="red-lighten-5" size="40" class="mr-3">
                    <v-icon color="red" size="20">mdi-heart-pulse</v-icon>
                 </v-avatar>
              </template>
              <v-list-item-title class="font-weight-bold">ສຸຂະພາບ/ໝູ່ເລືອດ</v-list-item-title>
              <v-list-item-subtitle>{{ profile.details?.health || '-' }}</v-list-item-subtitle>
           </v-list-item>

           <v-divider class="my-2 border-dashed"></v-divider>

           <v-list-item class="px-0">
              <template v-slot:prepend>
                 <v-avatar color="orange-lighten-5" size="40" class="mr-3">
                    <v-icon color="orange" size="20">mdi-star-face</v-icon>
                 </v-avatar>
              </template>
              <v-list-item-title class="font-weight-bold">ພອນສະຫວັນ</v-list-item-title>
              <v-list-item-subtitle>{{ profile.details?.talents || '-' }}</v-list-item-subtitle>
           </v-list-item>

        </v-list>
      </v-card>

      <div class="text-subtitle-2 text-grey-darken-1 font-weight-bold ml-1 mb-2">ການຕັ້ງຄ່າ</div>
      <v-card class="rounded-xl elevation-1 overflow-hidden mb-6">
        <v-list lines="one" class="py-0">
          
          <v-list-item link>
            <template v-slot:prepend><v-icon color="indigo">mdi-earth</v-icon></template>
            <v-list-item-title>ພາສາ (Language)</v-list-item-title>
            <template v-slot:append>
              <span class="text-caption text-primary font-weight-bold bg-indigo-lighten-5 px-2 py-1 rounded">ລາວ (LA)</span>
            </template>
          </v-list-item>
          
          <v-divider></v-divider>
          
          <v-list-item link>
            <template v-slot:prepend><v-icon color="grey-darken-1">mdi-information-outline</v-icon></template>
            <v-list-item-title>ກ່ຽວກັບລະບົບ</v-list-item-title>
            <template v-slot:append><v-icon size="small" color="grey">mdi-chevron-right</v-icon></template>
          </v-list-item>
          
          <v-divider></v-divider>
          
          <v-list-item @click="handleLogout" class="text-error">
            <template v-slot:prepend><v-icon color="error">mdi-logout</v-icon></template>
            <v-list-item-title class="font-weight-bold">ອອກຈາກລະບົບ</v-list-item-title>
          </v-list-item>

        </v-list>
      </v-card>

      <div class="text-center text-caption text-grey-lighten-1 mb-4">
        Student Tracking App v1.0.0 (Beta)
      </div>

    </v-container>

    <v-dialog v-model="dialog" max-width="320">
      <v-card class="rounded-xl pa-5 text-center">
        <v-avatar color="red-lighten-5" size="60" class="mb-3">
            <v-icon size="30" color="error">mdi-logout-variant</v-icon>
        </v-avatar>
        <div class="text-h6 font-weight-bold mb-1">ອອກຈາກລະບົບ?</div>
        <div class="text-body-2 text-grey mb-5">ທ່ານຕ້ອງການອອກຈາກບັນຊີນີ້ແທ້ບໍ່?</div>
        <div class="d-flex justify-space-between gap-3">
          <v-btn variant="tonal" color="grey-darken-1" size="large" @click="dialog = false" class="flex-grow-1 rounded-lg">ຍົກເລີກ</v-btn>
          <v-btn color="error" variant="flat" size="large" @click="confirmLogout" class="flex-grow-1 rounded-lg">ອອກເລີຍ</v-btn>
        </div>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';

const router = useRouter();
const dialog = ref(false);
const profile = ref({
    full_name: '',
    student_code: '',
    class_name: '',
    academic_year: '',
    total_points: 0,
    details: {}
});

const fetchProfile = async () => {
  try {
    // 1. ດຶງຂໍ້ມູນຄະແນນ ແລະ ຫ້ອງຮຽນຈາກ Dashboard
    const dashboardRes = await api.get('/students/dashboard');
    const dData = dashboardRes.data.student_info;
    
    // 2. ດຶງຂໍ້ມູນລາຍລະອຽດສ່ວນຕົວຈາກ /students/me
    const meRes = await api.get('/students/me');
    const meData = meRes.data;

    // Combine Data
    profile.value = {
      full_name: dData.name,
      student_code: dData.code,
      class_name: dData.class_name,
      total_points: dData.total_points,
      academic_year: meData.academic_year,
      details: meData.details // parent, talents, health
    };

  } catch (error) {
    console.error("Failed to load profile:", error);
  }
};

const handleLogout = () => {
  dialog.value = true;
};

const confirmLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('user');
  dialog.value = false;
  router.replace('/login');
};

onMounted(fetchProfile);
</script>

<style scoped>
.bg-gradient-primary {
    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
}
.text-shadow {
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.border-4 {
    border-width: 4px !important;
}
.gap-3 {
    gap: 12px;
}
.border-dashed {
    border-style: dashed;
    border-color: #E0E0E0;
}
</style>