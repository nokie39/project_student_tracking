<template>
  <v-container fluid> <v-card elevation="2" rounded="lg" class="h-100">
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
          <v-col cols="12" md="4" lg="3">
            <v-select
              v-model="selectedClass"
              :items="classes"
              item-title="name"
              item-value="id"
              label="ເລືອກຫ້ອງຮຽນ (Class)"
              variant="solo-filled" 
              density="comfortable"
              prepend-inner-icon="mdi-google-classroom"
              hide-details
              @update:model-value="fetchStudents"
              :loading="loadingClasses"
              class="rounded-lg"
            ></v-select>
          </v-col>

          <v-col cols="12" md="5" lg="6">
            <v-text-field
              v-model="search"
              label="ຄົ້ນຫາ (ຊື່, ລະຫັດ, ເບີໂທ...)"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
              class="rounded-lg"
              placeholder="ພິມຊື່ ຫຼື ລະຫັດນັກຮຽນ..."
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="3" lg="3" class="text-right d-none d-md-block">
             <v-chip v-if="selectedClass" color="primary" variant="tonal" size="large" class="font-weight-bold">
                <v-icon start>mdi-account-group</v-icon>
                ທັງໝົດ: {{ students.length }} ຄົນ
             </v-chip>
          </v-col>
        </v-row>

        <v-divider class="mb-4"></v-divider>

        <v-data-table
          :headers="headers"
          :items="students"
          :loading="loading"
          :search="search" 
          class="elevation-0 border rounded-lg student-table"
          fixed-header
          height="calc(100vh - 280px)" 
          hover
          items-per-page="25"
          :items-per-page-options="[10, 25, 50, 100, { value: -1, title: 'ທັງໝົດ' }]"
          items-per-page-text="ສະແດງແຖວຕໍ່ໜ້າ:"
          no-data-text="⚠️ ບໍ່ພົບຂໍ້ມູນ (ກະລຸນາເລືອກຫ້ອງຮຽນ)"
        >
          <template v-slot:item.student_code="{ item }">
            <v-chip size="small" color="blue-grey-lighten-4" class="text-blue-grey-darken-3 font-weight-bold">
              {{ item.student_code }}
            </v-chip>
          </template>

          <template v-slot:item.full_name="{ item }">
             <div class="d-flex align-center py-2">
                <v-avatar color="primary" size="32" class="mr-2" variant="tonal">
                  <span class="text-subtitle-2">{{ item.full_name.charAt(0) }}</span>
                </v-avatar>
                <div>
                    <div class="font-weight-bold text-body-1">{{ item.full_name }}</div>
                    <div class="text-caption text-grey" v-if="item.parent_name">
                        <v-icon size="x-small" start>mdi-human-male-child</v-icon> {{ item.parent_name }}
                    </div>
                </div>
             </div>
          </template>

          <template v-slot:item.email="{ item }">
             <div class="text-body-2 text-grey-darken-1">
               {{ item.email || '-' }}
             </div>
          </template>

          <template v-slot:item.actions="{ item }">
            <div class="d-flex gap-1 justify-end align-center">
              
              <v-tooltip text="ໃຫ້ຄະແນນພຶດຕິກຳ" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    size="small"
                    color="purple"
                    variant="text"
                    icon="mdi-star-circle"
                    @click="openBehaviorDialog(item)"
                  ></v-btn>
                </template>
              </v-tooltip>

              <v-menu location="bottom end">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    size="small"
                    color="indigo"
                    variant="text"
                    icon="mdi-file-document-multiple-outline"
                  ></v-btn>
                </template>
                <v-list density="compact" elevation="3">
                  <v-list-subheader>ເລືອກລາຍງານ</v-list-subheader>
                  <v-list-item @click="goToReport('detailed', item.id)" prepend-icon="mdi-history" title="ປະຫວັດການຮຽນລະອຽດ"></v-list-item>
                  <v-list-item @click="goToReport('transcript', item.id)" prepend-icon="mdi-file-certificate" title="ໃບຢັ້ງຢືນຜົນການຮຽນ"></v-list-item>
                </v-list>
              </v-menu>

              <v-tooltip text="ເບິ່ງປະຫວັດ/Portfolio" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    size="small"
                    color="info"
                    variant="text"
                    icon="mdi-account-details"
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
                    variant="text"
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

      <v-dialog v-model="behaviorDialog" max-width="500px">
        <v-card rounded="xl">
          <v-card-title class="bg-purple-darken-2 text-white d-flex align-center">
             <v-icon start>mdi-star-face</v-icon> ບັນທຶກພຶດຕິກຳ
          </v-card-title>
          <v-card-text class="pt-4">
             <div class="text-center mb-4">
                <v-avatar color="purple-lighten-5" size="60" class="mb-2">
                   <span class="text-h5 font-weight-bold text-purple">{{ selectedStudentBehavior?.full_name?.charAt(0) }}</span>
                </v-avatar>
                <div class="text-h6 font-weight-bold">{{ selectedStudentBehavior?.full_name }}</div>
                <div class="text-caption text-grey">ລະຫັດ: {{ selectedStudentBehavior?.student_code }}</div>
             </div>

             <v-form ref="behaviorFormRef" v-model="behaviorValid">
               <v-radio-group v-model="behaviorItem.type" inline density="compact" class="justify-center">
                  <v-radio label="ຊົມເຊີຍ (+)" value="POSITIVE" color="success"></v-radio>
                  <v-radio label="ຕັກເຕືອນ (-)" value="NEGATIVE" color="error"></v-radio>
               </v-radio-group>

               <v-text-field
                  v-model="behaviorItem.title"
                  label="ຫົວຂໍ້ (ເຊັ່ນ: ຊ່ວຍເຫຼືອໝູ່, ມາຊ້າ) *"
                  variant="outlined"
                  :rules="[v => !!v || 'ກະລຸນາໃສ່ຫົວຂໍ້']"
               ></v-text-field>

               <v-text-field
                  v-model.number="behaviorItem.points"
                  label="ຄະແນນ (Points)"
                  type="number"
                  variant="outlined"
                  prepend-inner-icon="mdi-numeric"
                  :rules="[v => !!v || 'ກະລຸນາໃສ່ຄະແນນ']"
               ></v-text-field>

               <v-textarea
                  v-model="behaviorItem.description"
                  label="ລາຍລະອຽດເພີ່ມເຕີມ"
                  variant="outlined"
                  rows="2"
                  auto-grow
               ></v-textarea>
             </v-form>
          </v-card-text>
          <v-card-actions class="justify-end px-4 pb-4">
             <v-btn variant="text" @click="behaviorDialog = false">ຍົກເລີກ</v-btn>
             <v-btn color="purple" variant="elevated" @click="saveBehavior" :loading="savingBehavior">ບັນທຶກ</v-btn>
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
  updateStudent,
  addBehaviorLog,
  getMyClasses
} from '../../services/api';

const router = useRouter();
const students = ref([]);
const classes = ref([]); 
const selectedClass = ref(null); 
const search = ref(''); // ✅ ຕົວແປ Search

const loading = ref(false);
const loadingClasses = ref(false);
const dialog = ref(false);
const saving = ref(false);
const valid = ref(false);
const form = ref(null);
const isEditing = ref(false); 

// Behavior Dialog States
const behaviorDialog = ref(false);
const behaviorValid = ref(false);
const behaviorFormRef = ref(null);
const savingBehavior = ref(false);
const selectedStudentBehavior = ref(null);
const behaviorItem = ref({
    type: 'POSITIVE',
    title: '',
    points: 5,
    description: ''
});

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
  { title: 'ລະຫັດ', key: 'student_code', align: 'start', width: '120px' },
  { title: 'ຊື່ ແລະ ນາມສະກຸນ', key: 'full_name', align: 'start' },
  { title: 'Email (Login)', key: 'email', align: 'start' }, 
  { title: 'ຈັດການ', key: 'actions', sortable: false, align: 'end', width: '180px' },
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
        const role = localStorage.getItem('role');
        const res = role === 'teacher' ? await getMyClasses() : await getClasses();
        
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

const openBehaviorDialog = (item) => {
    selectedStudentBehavior.value = item;
    behaviorItem.value = {
        type: 'POSITIVE',
        title: '',
        points: 5,
        description: ''
    };
    behaviorDialog.value = true;
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

const saveBehavior = async () => {
    const { valid } = await behaviorFormRef.value.validate();
    if (!valid) return;

    savingBehavior.value = true;
    try {
        let pts = Math.abs(behaviorItem.value.points);
        if (behaviorItem.value.type === 'NEGATIVE') pts = -pts;

        await addBehaviorLog({
            student_id: selectedStudentBehavior.value.id,
            type: behaviorItem.value.type,
            title: behaviorItem.value.title,
            description: behaviorItem.value.description,
            points: pts
        });

        showSnackbar("ບັນທຶກພຶດຕິກຳສຳເລັດ! ✅");
        behaviorDialog.value = false;
        
    } catch (error) {
        console.error(error);
        showSnackbar("ເກີດຂໍ້ຜິດພາດ: " + (error.response?.data?.detail || error.message), "error");
    } finally {
        savingBehavior.value = false;
    }
};

const viewPortfolio = (studentId) => {
  const role = localStorage.getItem('role');
  let routeName = 'StudentDetailAdmin'; 

  if (role === 'teacher') {
    routeName = 'TeacherStudentDetail';
  } else if (role === 'head_teacher') {
    routeName = 'HeadStudentDetail';
  }

  router.push({ name: routeName, params: { id: studentId } });
};

const goToReport = (type, studentId) => {
  const role = localStorage.getItem('role');
  let routeName = '';

  if (type === 'detailed') {
      if (role === 'admin') routeName = 'AdminDetailedReport';
      else if (role === 'teacher') routeName = 'TeacherDetailedReport';
      else if (role === 'head_teacher') routeName = 'HeadDetailedReport';
  } else if (type === 'transcript') {
      if (role === 'admin') routeName = 'AdminStudentTranscript';
      else if (role === 'teacher') routeName = 'TeacherStudentTranscript';
      else if (role === 'head_teacher') routeName = 'HeadStudentTranscript';
  }

  if (routeName) {
      router.push({ name: routeName, params: { id: studentId } });
  }
};

onMounted(init);
</script>

<style scoped>
.gap-1 { gap: 4px; }
.border-primary { border-color: rgba(var(--v-theme-primary), 0.2) !important; }
/* ປັບແຕ່ງຕາຕະລາງໃຫ້ເບິ່ງງ່າຍ */
.student-table :deep(th) {
    font-weight: bold !important;
    color: var(--v-theme-primary) !important;
    background-color: #f5f5f5 !important;
}
.student-table :deep(tr:hover) {
    background-color: #f0f7ff !important; /* ສີຟ້າອ່ອນເວລາເອົາເມົ້າໄປຊີ້ */
    cursor: pointer;
}
</style>