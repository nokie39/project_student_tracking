<template>
  <v-container fluid class="fill-height bg-grey-lighten-5 align-center justify-center">
    
    <v-card max-width="500" width="100%" class="rounded-xl pa-4" elevation="0" color="transparent">
      
      <div class="text-center mb-8">
        <v-avatar color="primary" size="80" class="mb-4 elevation-5">
          <v-icon size="40" color="white">mdi-account-child-circle</v-icon>
        </v-avatar>
        <h2 class="text-h5 font-weight-bold text-primary">ເລືອກນັກຮຽນ</h2>
        <div class="text-body-2 text-grey-darken-1">ກະລຸນາເລືອກລູກຫຼານທີ່ທ່ານຕ້ອງການເບິ່ງຂໍ້ມູນ</div>
      </div>

      <div v-if="loading" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <v-row v-else>
        <v-col cols="12" v-for="child in children" :key="child.id">
          <v-hover v-slot="{ isHovering, props }">
            <v-card 
              v-bind="props"
              :elevation="isHovering ? 6 : 2"
              class="rounded-xl cursor-pointer transition-swing"
              @click="selectChild(child)"
            >
              <div class="d-flex align-center pa-4">
                <v-avatar size="60" color="blue-lighten-5" class="mr-4">
                  <v-img 
                    v-if="child.photo_url" 
                    :src="child.photo_url" 
                    alt="child"
                  ></v-img>
                  <span v-else class="text-h5 font-weight-bold text-primary">
                    {{ child.name.charAt(0) }}
                  </span>
                </v-avatar>

                <div class="flex-grow-1">
                  <div class="text-h6 font-weight-bold text-grey-darken-3">
                    {{ child.name }}
                  </div>
                  <div class="d-flex align-center text-caption text-grey-darken-1 mt-1">
                    <v-icon size="small" start>mdi-card-account-details</v-icon> 
                    {{ child.student_code }}
                    <span class="mx-2">|</span>
                    <v-icon size="small" start>mdi-school</v-icon> 
                    {{ child.class_name }}
                  </div>
                </div>

                <v-icon color="grey-lighten-1">mdi-chevron-right</v-icon>
              </div>
            </v-card>
          </v-hover>
        </v-col>
      </v-row>

      <div v-if="!loading && children.length === 0" class="text-center mt-6">
        <v-alert type="warning" variant="tonal" class="rounded-xl">
          ຍັງບໍ່ມີຂໍ້ມູນນັກຮຽນທີ່ເຊື່ອມໂຍງກັບບັນຊີຂອງທ່ານ.
        </v-alert>
        <v-btn variant="text" color="primary" class="mt-2">
          ຕິດຕໍ່ຫ້ອງການໂຮງຮຽນ
        </v-btn>
      </div>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getMyChildren } from '../../services/api';

const router = useRouter();
const loading = ref(true);
const children = ref([]);

const fetchChildren = async () => {
  try {
    const res = await getMyChildren();
    children.value = res.data;
  } catch (error) {
    console.error("Error fetching children:", error);
  } finally {
    loading.value = false;
  }
};

const selectChild = (child) => {
  // 1. ບັນທຶກ ID ຂອງລູກທີ່ເລືອກໄວ້ໃນ localStorage (ເພື່ອໃຊ້ໃນ API ຕໍ່ໄປ)
  localStorage.setItem('selectedChildId', child.id);
  localStorage.setItem('selectedChildName', child.name);

  // 2. ໄປໜ້າ Dashboard ຂອງຜູ້ປົກຄອງ
  router.push(`/parent/dashboard/${child.id}`);
};

onMounted(fetchChildren);
</script>

<style scoped>
.transition-swing {
  transition: 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}
</style>