<template>
  <div v-if="loading" class="d-flex justify-center align-center" style="height: 400px;">
    <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
  </div>

  <v-container v-else-if="error" class="py-6 text-center">
    <v-alert type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>
    <v-btn color="primary" @click="$router.go(-1)">ຍ້ອນກັບ</v-btn>
  </v-container>

  <v-container v-else-if="student" class="py-6">
    <v-btn variant="text" color="grey-darken-1" class="mb-4" @click="$router.go(-1)">
      <v-icon start>mdi-arrow-left</v-icon> ຍ້ອນກັບ
    </v-btn>

    <v-row>
      <v-col cols="12" md="4">
        <v-card class="text-center pa-5" rounded="xl" elevation="3">
          <v-avatar size="150" color="grey-lighten-3" class="mb-4 border">
            <v-img v-if="student.profile_image" :src="student.profile_image" cover></v-img>
            <v-icon v-else size="100" color="grey-darken-1">mdi-account-school</v-icon>
          </v-avatar>
          
          <div class="text-h5 font-weight-bold">{{ student.full_name }}</div>
          <div class="text-subtitle-1 text-grey mb-2">ລະຫັດ: {{ student.student_code }}</div>
          
          <v-chip color="primary" variant="flat" class="px-4">
            ຫ້ອງ {{ student.class_name || 'N/A' }}
          </v-chip>
          
          <v-divider class="my-6"></v-divider>

          <div class="text-left">
            <div class="text-subtitle-2 text-primary mb-2">
              <v-icon start size="small">mdi-star</v-icon> ພອນສະຫວັນໂດດເດັ່ນ
            </div>
            <div class="d-flex flex-wrap gap-2">
              <v-chip
                v-for="(talent, index) in student.talents_list"
                :key="index"
                size="small"
                color="orange-darken-2"
                variant="tonal"
                class="ma-1"
              >
                {{ talent }}
              </v-chip>
              <div v-if="!student.talents_list.length" class="text-caption text-grey">ຍັງບໍ່ມີຂໍ້ມູນພອນສະຫວັນ</div>
            </div>
          </div>

          <v-divider class="my-6"></v-divider>

          <div class="d-flex justify-space-around">
            <div class="text-center">
              <div class="text-h6 text-success font-weight-bold">
                {{ student.total_merit_points > 0 ? '+' + student.total_merit_points : student.total_merit_points }}
              </div>
              <div class="text-caption text-grey">ຄະແນນພຶດຕິກຳລວມ</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card rounded="xl" elevation="3">
          <v-tabs v-model="tab" color="primary" grow bg-color="grey-lighten-4">
            <v-tab value="profile"><v-icon start>mdi-account-details</v-icon> ປະຫວັດສ່ວນຕົວ</v-tab>
            <v-tab value="behavior"><v-icon start>mdi-medal</v-icon> ພຶດຕິກຳ</v-tab>
            <v-tab value="health"><v-icon start>mdi-heart-pulse</v-icon> ສຸຂະພາບ</v-tab>
          </v-tabs>

          <v-window v-model="tab" class="pa-6">
            <v-window-item value="profile">
              <div class="text-h6 mb-4 text-primary font-weight-bold">ຂໍ້ມູນການຕິດຕໍ່ & ທີ່ຢູ່</div>
              <v-row>
                <v-col cols="12" sm="6">
                  <div class="text-caption text-grey">ຊື່ຜູ້ປົກຄອງ</div>
                  <div class="text-body-1">{{ student.parent_name || '-' }}</div>
                </v-col>
                <v-col cols="12" sm="6">
                  <div class="text-caption text-grey">ເບີໂທຕິດຕໍ່ສຸກເສີນ</div>
                  <div class="text-body-1 text-primary font-weight-bold">
                    <v-icon size="small">mdi-phone</v-icon> {{ student.parent_phone || '-' }}
                  </div>
                </v-col>
                <v-col cols="12">
                  <div class="text-caption text-grey">ທີ່ຢູ່ປັດຈຸບັນ</div>
                  <div class="text-body-1">
                    {{ student.address_summary || '-' }}
                  </div>
                </v-col>
                <v-col cols="12">
                   <div class="text-caption text-grey">ວັນເດືອນປີເກີດ</div>
                   <div class="text-body-1">{{ formatDate(student.date_of_birth) }}</div>
                </v-col>
              </v-row>
            </v-window-item>

            <v-window-item value="behavior">
              <div class="text-h6 mb-4 text-primary font-weight-bold">ປະຫວັດພຶດຕິກຳ ແລະ ຄຳຍ້ອງຍໍ</div>
              
              <v-timeline density="compact" align="start" v-if="behaviorLogs.length > 0">
                <v-timeline-item
                  v-for="log in behaviorLogs"
                  :key="log.id"
                  :dot-color="log.type === 'POSITIVE' ? 'success' : 'error'"
                  size="x-small"
                >
                  <div class="mb-4">
                    <div class="d-flex justify-space-between align-center">
                      <strong :class="log.type === 'POSITIVE' ? 'text-success' : 'text-error'">
                        {{ log.title }}
                      </strong>
                      <span class="text-caption text-grey">{{ formatDateTime(log.created_at) }}</span>
                    </div>
                    <div class="text-body-2 text-grey-darken-1">{{ log.description }}</div>
                    <div class="text-caption font-italic text-grey mt-1">
                        ຄະແນນ: {{ log.points > 0 ? '+' + log.points : log.points }}
                    </div>
                  </div>
                </v-timeline-item>
              </v-timeline>

              <v-alert v-else type="info" variant="tonal" class="mt-4">
                <v-icon start>mdi-information</v-icon>
                ຍັງບໍ່ມີບັນທຶກພຶດຕິກຳສຳລັບນັກຮຽນຄົນນີ້
              </v-alert>
            </v-window-item>

            <v-window-item value="health">
              <div class="text-h6 mb-4 text-primary font-weight-bold">ຂໍ້ມູນທາງການແພດ</div>
              <v-card variant="tonal" color="red-lighten-5" class="pa-4 border-dashed mb-4">
                <v-row>
                  <v-col cols="6">
                    <div class="text-caption text-grey-darken-2">ໝູ່ເລືອດ</div>
                    <div class="text-h5 font-weight-bold text-error">{{ student.blood_type || 'N/A' }}</div>
                  </v-col>
                  <v-col cols="6">
                    <div class="text-caption text-grey-darken-2">ພະຍາດປະຈຳຕົວ/ແພ້ຢາ</div>
                    <div class="text-body-1 font-weight-bold">{{ student.allergies || 'ບໍ່ມີ' }}</div>
                  </v-col>
                </v-row>
              </v-card>
              <div class="text-caption text-grey mt-2">
                * ຂໍ້ມູນນີ້ຖືກນຳໃຊ້ເພື່ອການຊ່ວຍເຫຼືອສຸກເສີນເທົ່ານັ້ນ
              </div>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getStudentPortfolio } from '../../services/api';

const route = useRoute();
const tab = ref('profile');
const student = ref(null);
const behaviorLogs = ref([]);
const loading = ref(true); // ✅ ເພີ່ມ Loading state
const error = ref(null); // ✅ ເພີ່ມ Error handling

const fetchData = async () => {
  const studentId = route.params.id;
  loading.value = true;
  error.value = null;
  
  try {
    const res = await getStudentPortfolio(studentId);
    
    // ກວດສອບໂຄງສ້າງຂໍ້ມູນ (Axios ມັກຈະສົ່ງມາໃນ res.data)
    const data = res.data ? res.data : res;

    student.value = {
      ...data, 
      // ແຍກ Talents ໃຫ້ປອດໄພ (ກັນ null)
      talents_list: data.talents ? data.talents.split(',').map(t => t.trim()) : []
    };
    
    behaviorLogs.value = data.behavior_logs || [];
    
  } catch (err) {
    console.error("Error loading student details:", err);
    error.value = "ບໍ່ສາມາດໂຫຼດຂໍ້ມູນນັກຮຽນໄດ້ ຫຼື ບໍ່ພົບຂໍ້ມູນນັກຮຽນ";
  } finally {
    loading.value = false; // ✅ ປິດ Loading ສະເໝີ
  }
};

// Format ວັນທີ
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('lo-LA', {
    day: 'numeric', month: 'long', year: 'numeric'
  });
};

// Format ວັນທີ + ເວລາ
const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('lo-LA', {
    day: 'numeric', month: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};

onMounted(fetchData);
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
.border-dashed {
  border: 1px dashed #ef5350 !important; /* ສີແດງອ່ອນໆໃຫ້ເຫັນຊັດເຈນ */
}
</style>