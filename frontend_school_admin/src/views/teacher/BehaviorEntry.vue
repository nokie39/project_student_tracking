<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card elevation="3" rounded="xl">
          <v-card-title class="bg-indigo-darken-2 text-white py-4">
            <v-icon start>mdi-star-plus</v-icon>
            ບັນທຶກພຶດຕິກຳ ແລະ ພອນສະຫວັນ
          </v-card-title>

          <v-card-text class="pt-6">
            <v-form ref="form" v-model="valid">
              <v-autocomplete
                v-model="selectedStudentId"
                :items="students"
                item-title="full_name"
                item-value="id"
                label="ຄົ້ນຫາ ແລະ ເລືອກນັກຮຽນ *"
                prepend-inner-icon="mdi-account-search"
                variant="outlined"
                :rules="[v => !!v || 'ກະລຸນາເລືອກນັກຮຽນ']"
                @update:model-value="loadStudentInfo"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props" :subtitle="item.raw.student_code"></v-list-item>
                </template>
              </v-autocomplete>

              <v-divider class="my-4"></v-divider>

              <v-row>
                <v-col cols="12">
                  <div class="text-subtitle-1 font-weight-bold mb-2">
                    <v-icon color="orange" start>mdi-auto-fix</v-icon> ພອນສະຫວັນ (Talents)
                  </div>
                  <v-text-field
                    v-model="talents"
                    label="ພອນສະຫວັນຂອງນັກຮຽນ"
                    placeholder="ຕົວຢ່າງ: ເຕະບານ, ແຕ້ມຮູບ, ຄິດໄລ່ໄວ"
                    variant="outlined"
                    hint="ຂໍ້ມູນນີ້ຈະໄປປາກົດໃນ Portfolio ຂອງນັກຮຽນ"
                    persistent-hint
                  ></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-divider class="my-4"></v-divider>
                  <div class="text-subtitle-1 font-weight-bold mb-2">
                    <v-icon color="indigo" start>mdi-clipboard-text-clock</v-icon> ບັນທຶກພຶດຕິກຳໃໝ່
                  </div>
                </v-col>

                <v-col cols="12" sm="6">
                  <v-select
                    v-model="behaviorType"
                    :items="[
                      { title: 'ດ້ານບວກ (ຍ້ອງຍໍ)', value: 'POSITIVE' },
                      { title: 'ດ້ານລົບ (ຕັກເຕືອນ)', value: 'NEGATIVE' }
                    ]"
                    label="ປະເພດພຶດຕິກຳ *"
                    variant="outlined"
                    :rules="[v => !!v || 'ກະລຸນາເລືອກປະເພດ']"
                    @update:model-value="updatePointsDefault"
                  ></v-select>
                </v-col>

                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="points"
                    type="number"
                    label="ຄະແນນ (Points) *"
                    variant="outlined"
                    :color="behaviorType === 'POSITIVE' ? 'success' : 'error'"
                    :rules="[v => !!v || 'ກະລຸນາໃສ່ຄະແນນ']"
                  >
                    <template v-slot:prepend-inner>
                       <span :class="behaviorType === 'POSITIVE' ? 'text-success' : 'text-error'">
                         {{ behaviorType === 'POSITIVE' ? '+' : '-' }}
                       </span>
                    </template>
                  </v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field
                    v-model="behaviorTitle"
                    label="ຫົວຂໍ້ພຶດຕິກຳ *"
                    placeholder="ຕົວຢ່າງ: ຊ່ວຍເຫຼືອໝູ່ເພື່ອນ, ມາໂຮງຮຽນສາຍ..."
                    variant="outlined"
                    :rules="[v => !!v || 'ກະລຸນາໃສ່ຫົວຂໍ້']"
                  ></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-textarea
                    v-model="description"
                    label="ລາຍລະອຽດເພີ່ມເຕີມ"
                    variant="outlined"
                    rows="3"
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions class="pa-4 bg-grey-lighten-4">
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="resetForm">
              ລ້າງຂໍ້ມູນ
            </v-btn>
            <v-btn
              color="indigo-darken-2"
              variant="elevated"
              size="large"
              :loading="loading"
              @click="submitBehavior"
            >
              <v-icon start>mdi-content-save</v-icon> ບັນທຶກຂໍ້ມູນ
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="top">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn icon variant="text" @click="snackbar.show = false" color="white">
            <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api'; // ✅ Import ຫຼັກອັນດຽວພໍ

const valid = ref(false);
const loading = ref(false);
const form = ref(null);
const students = ref([]);

const selectedStudentId = ref(null);
const talents = ref('');
const behaviorType = ref('POSITIVE');
const points = ref(5);
const behaviorTitle = ref('');
const description = ref('');

const snackbar = ref({ show: false, text: '', color: '' });

// 1. ດຶງຂໍ້ມູນນັກຮຽນໃນຫ້ອງ (Mock Class ID = 1)
const fetchStudents = async () => {
  try {
    // ໃຊ້ Endpoint ທີ່ເຮົາສ້າງໃນ behavior.py
    const res = await api.get('/behavior/class/1/students');
    students.value = res.data;
  } catch (error) {
    console.error("Failed to fetch students", error);
    snackbar.value = { show: true, text: 'ບໍ່ສາມາດດຶງຂໍ້ມູນນັກຮຽນໄດ້', color: 'error' };
  }
};

// 2. ໂຫຼດຂໍ້ມູນພອນສະຫວັນເກົ່າ
const loadStudentInfo = async (studentId) => {
  if (!studentId) return;
  try {
    // ດຶງຂໍ້ມູນນັກຮຽນໂດຍກົງ (ລວມທັງ talents)
    // ⚠️ ຕ້ອງມີ API endpoint /students/{id} ຫຼືໃຊ້ວິທີ filter ຈາກ list ທີ່ມີຢູ່
    // ໃນທີ່ນີ້ຂໍໃຊ້ການ filter ຈາກ students list ທີ່ໂຫລດມາແລ້ວ (ຖ້າມີ field talents)
    // ແຕ່ຖ້າ API /behavior/class/1/students ບໍ່ສົ່ງ talents ມາ, ຕ້ອງຍິງ API student detail
    
    // ຕົວຢ່າງ: ຍິງ API ຫາ detail
    // const res = await api.get(`/students/${studentId}`); 
    // talents.value = res.data.talents || '';
    
    talents.value = ''; // Reset ກ່ອນ
  } catch (error) {
    console.error("Failed to load student info");
  }
};

const updatePointsDefault = (type) => {
    points.value = type === 'POSITIVE' ? 5 : 5;
}

// 3. ບັນທຶກຂໍ້ມູນ
const submitBehavior = async () => {
  const { valid: isFormValid } = await form.value.validate();
  if (!isFormValid) return;

  loading.value = true;
  try {
    // ກ. ອັບເດດພອນສະຫວັນ (Backend: PUT /behavior/talents/{id})
    if (talents.value) {
        await api.put(`/behavior/talents/${selectedStudentId.value}`, {
            talents: talents.value
        });
    }

    // ຂ. ຈັດການຄະແນນ (ຖ້າເປັນ Negative ຕ້ອງປ່ຽນເປັນຄ່າລົບ)
    let finalPoints = Math.abs(parseInt(points.value));
    if (behaviorType.value === 'NEGATIVE') {
        finalPoints = -finalPoints;
    }

    // ຄ. ບັນທຶກພຶດຕິກຳ (Backend: POST /behavior/add)
    await api.post('/behavior/add', {
      student_id: selectedStudentId.value,
      type: behaviorType.value,
      title: behaviorTitle.value,
      description: description.value || "",
      points: finalPoints
    });

    snackbar.value = { show: true, text: 'ບັນທຶກຂໍ້ມູນສຳເລັດແລ້ວ! ✅', color: 'success' };
    resetForm();
    
    // ໂຫຼດຂໍ້ມູນນັກຮຽນໃໝ່ (ເພື່ອອັບເດດຄະແນນຖ້າມີຕາຕະລາງໂຊ)
    fetchStudents();

  } catch (error) {
    console.error(error);
    snackbar.value = { show: true, text: 'ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ ❌', color: 'error' };
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.value.reset();
  behaviorType.value = 'POSITIVE';
  points.value = 5;
  talents.value = '';
};

onMounted(fetchStudents);
</script>