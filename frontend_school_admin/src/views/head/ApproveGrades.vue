<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" rounded="xl" class="pa-4 bg-indigo-darken-3 text-white">
          <div class="d-flex align-center">
            <v-icon size="40" class="mr-4">mdi-check-decagram</v-icon>
            <div>
              <h2 class="text-h5 font-weight-bold">ອະນຸມັດ ແລະ ລັອກຄະແນນ</h2>
              <p class="text-subtitle-2 opacity-80">ກວດສອບຄວາມຖືກຕ້ອງ ແລະ ປິດການປ້ອນຄະແນນປະຈຳເດືອນ</p>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-select
          v-model="selectedMonthId"
          :items="months"
          item-title="name"
          item-value="id"
          label="ເລືອກເດືອນ"
          variant="outlined"
          rounded="lg"
          @update:model-value="fetchMonitorData"
        ></v-select>
      </v-col>

      <v-col cols="12">
        <v-card rounded="xl" elevation="3">
          <v-table>
            <thead>
              <tr class="bg-grey-lighten-4">
                <th class="font-weight-bold">ຫ້ອງຮຽນ</th>
                <th class="font-weight-bold">ຄູປະຈຳຫ້ອງ</th>
                <th class="font-weight-bold text-center">ຄວາມຄືບໜ້າການປ້ອນ</th>
                <th class="font-weight-bold text-center">ສະຖານະ</th>
                <th class="font-weight-bold text-center">ການຈັດການ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in monitorData" :key="item.teacher_id">
                <td><span class="font-weight-bold text-primary">{{ item.class_name }}</span></td>
                <td>{{ item.full_name }}</td>
                <td width="250">
                  <v-progress-linear
                    v-model="item.grade_progress"
                    :color="item.grade_progress === 100 ? 'success' : 'orange'"
                    height="20"
                    rounded
                  >
                    <template v-slot:default="{ value }">
                      <span class="text-caption font-weight-bold">{{ Math.ceil(value) }}%</span>
                    </template>
                  </v-progress-linear>
                </td>
                <td class="text-center">
                  <v-chip
                    :color="item.is_locked ? 'error' : 'success'"
                    size="small"
                    variant="flat"
                  >
                    <v-icon start :icon="item.is_locked ? 'mdi-lock' : 'mdi-lock-open-variant'"></v-icon>
                    {{ item.is_locked ? 'Locked' : 'Open' }}
                  </v-chip>
                </td>
                <td class="text-center">
                  <v-btn
                    :color="item.is_locked ? 'success' : 'error'"
                    :variant="item.is_locked ? 'outlined' : 'elevated'"
                    size="small"
                    rounded="pill"
                    :disabled="item.grade_progress < 100 && !item.is_locked"
                    @click="toggleLock(item)"
                  >
                    {{ item.is_locked ? 'ປົດລັອກ' : 'ລັອກຄະແນນ' }}
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card rounded="xl" class="pa-4 text-center">
        <v-icon :color="targetItem?.is_locked ? 'success' : 'error'" size="64" class="mb-4">
          {{ targetItem?.is_locked ? 'mdi-lock-open-variant' : 'mdi-lock' }}
        </v-icon>
        <h3 class="text-h6 mb-2">{{ targetItem?.is_locked ? 'ຢືນຢັນການປົດລັອກ?' : 'ຢືນຢັນການລັອກຄະແນນ?' }}</h3>
        <p class="text-body-2 text-grey mb-6">
          {{ targetItem?.is_locked 
            ? 'ຄູປະຈຳຫ້ອງຈະສາມາດກັບມາແກ້ໄຂຄະແນນໄດ້ອີກຄັ້ງ.' 
            : 'ເມື່ອລັອກແລ້ວ ຄູຈະບໍ່ສາມາດແກ້ໄຂຄະແນນໄດ້ ນອກຈາກຈະໄດ້ຮັບການປົດລັອກ.' 
          }}
        </p>
        <div class="d-flex gap-2">
          <v-btn block variant="text" @click="confirmDialog = false">ຍົກເລີກ</v-btn>
          <v-btn block :color="targetItem?.is_locked ? 'success' : 'error'" @click="processToggle">ຢືນຢັນ</v-btn>
        </div>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getMonitorSummary, lockGradeMonth } from '../../services/api';

const selectedMonthId = ref(1);
const months = ref([
  { id: 1, name: 'September' },
  { id: 2, name: 'October' }
]);
const monitorData = ref([]);
const confirmDialog = ref(false);
const targetItem = ref(null);

const fetchMonitorData = async () => {
  try {
    const res = await getMonitorSummary(); // ໃຊ້ API monitor ທີ່ເຮົາເຮັດໄວ້
    monitorData.value = res.data;
  } catch (error) {
    console.error("Fetch error:", error);
  }
};

const toggleLock = (item) => {
  targetItem.value = item;
  confirmDialog.value = true;
};

const processToggle = async () => {
  try {
    // ສົ່ງຄ່າກົງກັນຂ້າມກັບຄ່າປັດຈຸບັນ
    await lockGradeMonth(selectedMonthId.value, !targetItem.value.is_locked);
    confirmDialog.value = false;
    fetchMonitorData(); // Refresh Data
  } catch (error) {
    alert("ເກີດຂໍ້ຜິດພາດໃນການປ່ຽນສະຖານະ");
  }
};

onMounted(fetchMonitorData);
</script>