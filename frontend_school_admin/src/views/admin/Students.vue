<template>
  <v-container>
    <v-card elevation="2" rounded="lg">
      <v-card-title class="d-flex flex-wrap justify-space-between align-center py-4 px-4 bg-primary text-white">
        <div class="text-h6 d-flex align-center">
          <v-icon icon="mdi-account-school" start></v-icon>
          ຈັດການຂໍ້ມູນນັກຮຽນ
        </div>
        <v-btn 
          color="white" 
          variant="elevated" 
          class="text-primary font-weight-bold"
          prepend-icon="mdi-plus" 
          @click="openRegisterDialog"
          :disabled="!selectedClass"
        >
          ລົງທະບຽນໃໝ່
        </v-btn>
      </v-card-title>

      <v-card-text class="mt-4">
        <v-row align="center" class="mb-2">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedClass"
              :items="classes"
              item-title="name"
              item-value="id"
              label="ເລືອກຫ້ອງຮຽນ"
              variant="outlined"
              density="compact"
              prepend-inner-icon="mdi-google-classroom"
              hide-details
              @update:model-value="fetchStudents"
              :loading="loadingClasses"
            ></v-select>
          </v-col>
          <v-col cols="12" md="8" class="text-right">
             <v-chip v-if="selectedClass" color="primary" variant="tonal">
                <v-icon start>mdi-account-group</v-icon>
                ຈຳນວນນັກຮຽນ: {{ students.length }} ຄົນ
             </v-chip>
          </v-col>
        </v-row>

        <v-divider class="mb-4"></v-divider>

        <v-data-table
          :headers="headers"
          :items="students"
          :loading="loading"
          class="elevation-0 border rounded-lg"
          no-data-text="ບໍ່ພົບຂໍ້ມູນນັກຮຽນໃນຫ້ອງນີ້ (ຫຼື ຍັງບໍ່ໄດ້ເລືອກຫ້ອງ)"
        >
          <template v-slot:item.student_code="{ item }">
            <v-chip size="small" color="blue-grey" variant="outlined" class="font-weight-bold">
              {{ item.student_code }}
            </v-chip>
          </template>

          <template v-slot:item.email="{ item }">
             <div class="text-body-2 text-grey-darken-1">
               <v-icon size="x-small" class="mr-1">mdi-email-outline</v-icon>
               {{ item.email || '-' }}
             </div>
          </template>

          <template v-slot:item.full_name="{ item }">
             <div class="font-weight-bold text-primary">{{ item.full_name }}</div>
             <div class="text-caption text-grey" v-if="item.parent_name">
               <v-icon size="x-small">mdi-human-male-child</v-icon> ຜູ້ປົກຄອງ: {{ item.parent_name }}
             </div>
          </template>

          <template v-slot:item.actions="{ item }">
            <div class="d-flex gap-2 justify-end">
              <v-tooltip text="ເບິ່ງປະຫວັດ" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    size="small"
                    color="info"
                    variant="tonal"
                    icon="mdi-file-account"
                    @click="viewPortfolio(item.id)"
                  ></v-btn>
                </template>
              </v-tooltip>

              <v-tooltip text="ແກ້ໄຂຂໍ້ມູນ" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    size="small"
                    color="warning"
                    variant="tonal"
                    icon="mdi-pencil"
                    @click="openEditDialog(item)"
                  ></v-btn>
                </template>
              </v-tooltip>
            </div>
          </template>
        </v-data-table>
      </v-card-text>

      <v-dialog v-model="dialog" max-width="800px" scrollable persistent>
        <v-card rounded="xl">
          <v-card-title class="bg-primary text-white pa-4 d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon start>{{ isEditing ? 'mdi-account-edit' : 'mdi-account-plus' }}</v-icon>
              {{ isEditing ? 'ແກ້ໄຂຂໍ້ມູນນັກຮຽນ' : `ລົງທະບຽນນັກຮຽນໃໝ່ (ເຂົ້າຫ້ອງ ${getClassName(selectedClass)})` }}
            </div>
            <v-btn icon="mdi-close" variant="text" color="white" @click="closeDialog"></v-btn>
          </v-card-title>
          
          <v-card-text class="pt-4 bg-grey-lighten-5">
            <v-form ref="form" v-model="valid">
              
              <v-card variant="outlined" class="mb-4 bg-white border-primary">
                <v-card-title class="text-subtitle-1 font-weight-bold text-primary">
                    <v-icon start size="small" color="primary">mdi-card-account-details</v-icon>
                    1. ຂໍ້ມູນພື້ນຖານ
                </v-card-title>
                <v-card-text>
                    <v-row dense>
                        <v-col cols="12" md="6">
                        <v-text-field 
                          v-model="newItem.email" 
                          label="Email (Login) *" 
                          variant="outlined" 
                          density="compact" 
                          :rules="rules.email" 
                          prepend-inner-icon="mdi-email"
                          hint="ໃຊ້ສຳລັບ Login ເຂົ້າລະບົບ"
                        ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                        <v-text-field v-model="newItem.full_name" label="ຊື່ ແລະ ນາມສະກຸນ *" variant="outlined" density="compact" :rules="rules.required" prepend-inner-icon="mdi-account"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                        <v-text-field v-model="newItem.student_code" label="ລະຫັດນັກຮຽນ *" variant="outlined" density="compact" :rules="rules.required" prepend-inner-icon="mdi-barcode"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                        <v-text-field v-model="newItem.date_of_birth" type="date" label="ວັນເດືອນປີເກີດ" variant="outlined" density="compact"></v-text-field>
                        </v-col>
                    </v-row>
                </v-card-text>
              </v-card>

              <v-card variant="outlined" class="mb-4 bg-white border-primary">
                <v-card-title class="text-subtitle-1 font-weight-bold text-primary">
                    <v-icon start size="small" color="primary">mdi-home-map-marker</v-icon>
                    2. ຜູ້ປົກຄອງ ແລະ ທີ່ຢູ່
                </v-card-title>
                <v-card-text>
                    <v-alert type="info" variant="tonal" density="compact" class="mb-3" v-if="!isEditing">
                        <span class="text-caption">ຫາກໃສ່ <b>Email ຜູ້ປົກຄອງ</b>, ລະບົບຈະສ້າງບັນຊີຜູ້ປົກຄອງໃຫ້ອັດຕະໂນມັດ (ຖ້າຍັງບໍ່ມີ).</span>
                    </v-alert>
                    <v-row dense>
                        <v-col cols="12" md="6">
                          <v-text-field 
                            v-model="newItem.parent_email" 
                            label="ອີເມວຜູ້ປົກຄອງ (Parent Email)" 
                            variant="outlined" 
                            density="compact" 
                            prepend-inner-icon="mdi-email-outline"
                            :rules="newItem.parent_email ? rules.email : []"
                            hint="ສຳຄັນ: ໃຊ້ເຊື່ອມຕໍ່ກັບ App ຜູ້ປົກຄອງ"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field v-model="newItem.parent_name" label="ຊື່ຜູ້ປົກຄອງ" variant="outlined" density="compact"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                        <v-text-field v-model="newItem.parent_phone" label="ເບີໂທຕິດຕໍ່" variant="outlined" density="compact" prepend-inner-icon="mdi-phone"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field v-model="newItem.province" label="ແຂວງ" variant="outlined" density="compact"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="4">
                          <v-text-field v-model="newItem.district" label="ເມືອງ" variant="outlined" density="compact"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="4">
                          <v-text-field v-model="newItem.village" label="ບ້ານ" variant="outlined" density="compact"></v-text-field>
                        </v-col>
                    </v-row>
                </v-card-text>
              </v-card>

              <v-card variant="outlined" class="bg-white border-primary">
                <v-card-title class="text-subtitle-1 font-weight-bold text-primary">
                    <v-icon start size="small" color="primary">mdi-heart-pulse</v-icon>
                    3. ສຸຂະພາບ ແລະ ພອນສະຫວັນ
                </v-card-title>
                <v-card-text>
                    <v-row dense>
                        <v-col cols="12" md="4">
                        <v-select v-model="newItem.blood_type" :items="['A', 'B', 'AB', 'O']" label="ໝູ່ເລືອດ" variant="outlined" density="compact"></v-select>
                        </v-col>
                        <v-col cols="12" md="8">
                        <v-text-field v-model="newItem.allergies" label="ສິ່ງທີ່ແພ້ (ອາຫານ/ຢາ)" variant="outlined" density="compact"></v-text-field>
                        </v-col>
                        <v-col cols="12">
                        <v-textarea v-model="newItem.talents" label="ພອນສະຫວັນ ຫຼື ຈຸດເດັ່ນ" variant="outlined" density="compact" rows="2" placeholder="ຕົວຢ່າງ: ເຕະບານ, ແຕ້ມຮູບ..."></v-textarea>
                        </v-col>
                    </v-row>
                </v-card-text>
              </v-card>

            </v-form>
          </v-card-text>

          <v-card-actions class="pb-4 px-4 bg-white">
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="closeDialog">ຍົກເລີກ</v-btn>
            <v-btn 
              color="primary" 
              variant="elevated" 
              @click="save" 
              :loading="saving" 
              prepend-icon="mdi-content-save"
            >
              {{ isEditing ? 'ອັບເດດຂໍ້ມູນ' : 'ບັນທຶກຂໍ້ມູນ' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top" timeout="3000">
        <v-icon start>{{ snackbar.icon }}</v-icon>
        {{ snackbar.message }}
        <template v-slot:actions>
            <v-btn variant="text" @click="snackbar.show = false">ປິດ</v-btn>
        </template>
      </v-snackbar>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  getStudentsInClass, 
  registerStudent, 
  enrollStudent, 
  getClasses,
  updateStudent 
} from '../../services/api';

const router = useRouter();
const students = ref([]);
const classes = ref([]); 
const selectedClass = ref(null); 

const loading = ref(false);
const loadingClasses = ref(false);
const dialog = ref(false);
const saving = ref(false);
const valid = ref(false);
const form = ref(null);
const isEditing = ref(false); 

// Snackbar State
const snackbar = ref({
    show: false,
    message: '',
    color: 'success',
    icon: 'mdi-check-circle'
});

const showSnackbar = (msg, type = 'success') => {
    snackbar.value = {
        show: true,
        message: msg,
        color: type === 'success' ? 'green-darken-1' : 'red-darken-1',
        icon: type === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'
    };
};

const headers = [
  { title: 'ລະຫັດ', key: 'student_code', align: 'start' },
  { title: 'Email (Login)', key: 'email', align: 'start' }, 
  { title: 'ຊື່ ແລະ ນາມສະກຸນ', key: 'full_name', align: 'start' },
  { title: 'ຈັດການ', key: 'actions', sortable: false, align: 'end' },
];

const rules = {
   required: [v => !!v || 'ຈຳເປັນຕ້ອງໃສ່ຂໍ້ມູນນີ້'],
   email: [
     v => !v || /.+@.+\..+/.test(v) || 'ຮູບແບບ Email ບໍ່ຖືກຕ້ອງ'
   ]
};

const defaultItem = {
  id: null,
  email: '',
  full_name: '',
  student_code: '',
  date_of_birth: '2010-01-01',
  parent_name: '',
  parent_phone: '',
  parent_email: '',
  blood_type: null,
  allergies: '',
  province: 'ນະຄອນຫຼວງວຽງຈັນ',
  district: '',
  village: '',
  talents: '',
  health_info: '-'
};

const newItem = ref({ ...defaultItem });

const init = async () => {
    loadingClasses.value = true;
    try {
        const res = await getClasses();
        classes.value = res.data;
        if (classes.value.length > 0) {
            selectedClass.value = classes.value[0].id;
            fetchStudents(); 
        }
    } catch (error) {
        console.error("Error fetching classes:", error);
    } finally {
        loadingClasses.value = false;
    }
};

const fetchStudents = async () => {
  if (!selectedClass.value) return;

  loading.value = true;
  try {
    const response = await getStudentsInClass(selectedClass.value);
    students.value = response.data;
  } catch (error) {
    console.error("Error loading students:", error);
    if (error.response && error.response.status === 401) {
       router.push('/login');
    } else if (error.response && error.response.status === 403) {
       showSnackbar('ທ່ານບໍ່ມີສິດເຂົ້າເຖິງຫ້ອງຮຽນນີ້', 'error');
       students.value = [];
    }
  } finally {
    loading.value = false;
  }
};

const openRegisterDialog = () => {
    if (!selectedClass.value) {
        showSnackbar("ກະລຸນາເລືອກຫ້ອງຮຽນກ່ອນ", "error");
        return;
    }
    newItem.value = { ...defaultItem };
    isEditing.value = false;
    dialog.value = true;
};

const openEditDialog = (item) => {
    newItem.value = { 
        ...defaultItem, 
        ...item,
        date_of_birth: item.date_of_birth || '2010-01-01'
    }; 
    isEditing.value = true;
    dialog.value = true;
};

const closeDialog = () => {
    dialog.value = false;
    setTimeout(() => {
        newItem.value = { ...defaultItem };
        isEditing.value = false;
    }, 300);
};

const getClassName = (id) => {
    const c = classes.value.find(x => x.id === id);
    return c ? c.name : '';
};

const save = async () => {
  const { valid } = await form.value.validate();
  if (!valid) {
      showSnackbar("ກະລຸນາປ້ອນຂໍ້ມູນໃຫ້ຄົບຖ້ວນ", "error");
      return;
  }

  saving.value = true;
  try {
    const payload = { ...newItem.value };

    if (!payload.date_of_birth) {
        payload.date_of_birth = "2010-01-01";
    }

    // Convert empty strings to null for optional fields
    ['parent_email', 'parent_name', 'parent_phone', 'allergies', 'talents', 'health_info'].forEach(k => {
        if (!payload[k]) payload[k] = null;
    });

    if (isEditing.value) {
        await updateStudent(payload.id, payload);
        showSnackbar('ອັບເດດຂໍ້ມູນສຳເລັດ! ✅');
    } else {
        const regRes = await registerStudent(payload);
        const newStudentId = regRes.data.id;

        await enrollStudent({
            student_id: newStudentId,
            class_id: selectedClass.value 
        });
        showSnackbar(`ລົງທະບຽນສຳເລັດ! ເຂົ້າຫ້ອງ ${getClassName(selectedClass.value)} 🎉`);
    }

    closeDialog();
    fetchStudents(); 

  } catch (error) {
    console.error(error);
    const msg = error.response?.data?.detail || 'ເກີດຂໍ້ຜິດພາດໃນການບັນທຶກ';
    showSnackbar('ເກີດຂໍ້ຜິດພາດ: ' + msg, 'error');
  } finally {
    saving.value = false;
  }
};

const viewPortfolio = (studentId) => {
  router.push({ name: 'StudentDetail', params: { id: studentId } });
};

onMounted(init);
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
.border-primary {
    border-color: rgba(var(--v-theme-primary), 0.2) !important;
}
</style>