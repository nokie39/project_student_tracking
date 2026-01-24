<template>
  <v-container fluid class="fill-height align-start bg-grey-lighten-5 pa-0">
    
    <div class="w-100 bg-primary pt-10 pb-16 text-center rounded-b-xl elevation-4 position-relative">
      <v-avatar size="100" class="border-4 border-white elevation-5">
        <v-img src="https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Prescription02&hairColor=Black&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Happy&eyebrowType=Default&mouthType=Smile&skinColor=Light"></v-img>
      </v-avatar>
      <div class="text-h5 font-weight-bold text-white mt-3">{{ profile.full_name }}</div>
      <div class="text-subtitle-2 text-blue-lighten-4">ລະຫັດ: {{ profile.student_code }}</div>
      
      <v-btn icon="mdi-arrow-left" variant="text" color="white" class="position-absolute top-0 left-0 mt-2 ml-2" @click="$router.back()"></v-btn>
    </div>

    <v-container class="mt-n12 px-4">
      <v-card class="rounded-xl pa-4 mb-4" elevation="2">
        <div class="text-subtitle-2 text-grey mb-2 font-weight-bold">ຂໍ້ມູນການຮຽນ</div>
        <v-divider class="mb-3"></v-divider>
        
        <v-row dense>
          <v-col cols="6">
            <div class="text-caption text-grey">ຫ້ອງຮຽນ</div>
            <div class="text-body-1 font-weight-bold">{{ profile.class_name || 'N/A' }}</div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption text-grey">ຄູປະຈຳຫ້ອງ</div>
            <div class="text-body-1 font-weight-bold">{{ profile.teacher_name || 'N/A' }}</div>
          </v-col>
        </v-row>
      </v-card>

      <v-card class="rounded-xl elevation-2 overflow-hidden">
        <v-list lines="one">
          <v-list-item prepend-icon="mdi-lock-reset" title="ປ່ຽນລະຫັດຜ່ານ" link></v-list-item>
          <v-divider></v-divider>
          <v-list-item prepend-icon="mdi-earth" title="ປ່ຽນພາສາ" value="la">
            <template v-slot:append>
              <span class="text-caption text-primary font-weight-bold">ລາວ (LA)</span>
            </template>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item prepend-icon="mdi-help-circle-outline" title="ຊ່ວຍເຫຼືອ & ແຈ້ງບັນຫາ" link></v-list-item>
        </v-list>
      </v-card>

      <v-btn 
        block 
        color="error" 
        size="large" 
        variant="flat" 
        class="rounded-xl mt-6 font-weight-bold"
        prepend-icon="mdi-logout"
        @click="handleLogout"
      >
        ອອກຈາກລະບົບ
      </v-btn>
      
      <div class="text-center text-caption text-grey-lighten-1 mt-4">
        Version 1.0.0 (Beta)
      </div>

    </v-container>

    <v-dialog v-model="dialog" max-width="300">
      <v-card class="rounded-xl pa-4 text-center">
        <v-icon size="50" color="warning" class="mb-2">mdi-alert-circle-outline</v-icon>
        <div class="text-h6 font-weight-bold">ຢືນຢັນການອອກ?</div>
        <div class="text-body-2 text-grey mb-4">ທ່ານຕ້ອງການອອກຈາກລະບົບແທ້ບໍ່?</div>
        <div class="d-flex justify-space-between">
          <v-btn variant="text" @click="dialog = false" class="flex-grow-1">ຍົກເລີກ</v-btn>
          <v-btn color="error" variant="flat" @click="confirmLogout" class="flex-grow-1 rounded-lg">ອອກເລີຍ</v-btn>
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
const profile = ref({});

const fetchProfile = async () => {
  try {
    // ໃຊ້ API Dashboard ເພື່ອດຶງຂໍ້ມູນພື້ນຖານມາກ່ອນ (ຫຼືຈະສ້າງ API /me ໃໝ່ກໍໄດ້)
    const res = await api.get('/students/dashboard');
    profile.value = {
      full_name: res.data.student_info.name,
      student_code: res.data.student_info.code,
      class_name: res.data.student_info.class_name,
      // teacher_name: ... (ຖ້າ API ສົ່ງມາ)
    };
  } catch (error) {
    console.error(error);
  }
};

const handleLogout = () => {
  dialog.value = true;
};

const confirmLogout = () => {
  // 1. ລຶບ Token
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('user');
  
  // 2. ກັບໄປໜ້າ Login
  dialog.value = false;
  router.replace('/login');
};

onMounted(fetchProfile);
</script>