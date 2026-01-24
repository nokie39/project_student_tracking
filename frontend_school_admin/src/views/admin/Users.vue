<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2 class="text-primary mb-4">
          <v-icon icon="mdi-account-cog" class="mr-2"></v-icon>
          ຈັດການຜູ້ໃຊ້ (User Management)
        </h2>
      </v-col>
    </v-row>

    <v-card elevation="2" rounded="lg">
      <v-card-title class="d-flex flex-wrap align-center py-3 gap-2">
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="ຄົ້ນຫາ (ຊື່ ຫຼື Email)..."
          single-line
          hide-details
          density="compact"
          variant="outlined"
          class="flex-grow-1 flex-md-grow-0"
          style="min-width: 300px"
        ></v-text-field>
        
        <v-spacer></v-spacer>
        
        <v-btn color="primary" prepend-icon="mdi-account-plus" @click="openDialog()">
          ເພີ່ມຜູ້ໃຊ້ໃໝ່
        </v-btn>
      </v-card-title>

      <v-data-table :headers="headers" :items="users" :search="search" :loading="loading">
        <template v-slot:item.role="{ item }">
          <v-chip :color="getRoleColor(item.role)" size="small" class="text-uppercase font-weight-bold" label>
            {{ item.role }}
          </v-chip>
        </template>
        
        <template v-slot:item.is_active="{ item }">
          <v-switch
            v-model="item.is_active"
            color="success"
            density="compact"
            hide-details
            inset
            @update:model-value="toggleStatus(item)"
            :loading="item.updating"
          ></v-switch>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="primary" variant="text" @click="openDialog(item)"></v-btn>
          <v-btn icon="mdi-delete" size="small" color="error" variant="text" @click="deleteItem(item)"></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card rounded="lg">
        <v-card-title class="bg-primary text-white d-flex justify-space-between align-center">
          <span>{{ editedId ? 'ແກ້ໄຂຂໍ້ມູນຜູ້ໃຊ້' : 'ເພີ່ມຜູ້ໃຊ້ໃໝ່' }}</span>
          <v-btn icon="mdi-close" variant="text" color="white" @click="dialog = false"></v-btn>
        </v-card-title>

        <v-card-text class="pa-4 bg-grey-lighten-5">
          <v-form ref="form" v-model="valid" @submit.prevent="save">
            
            <v-card variant="outlined" class="bg-white mb-3">
              <v-card-text>
                <v-text-field 
                    v-model="editedItem.full_name" 
                    label="ຊື່ ແລະ ນາມສະກຸນ *" 
                    variant="outlined" 
                    class="mb-2"
                    prepend-inner-icon="mdi-account"
                    :rules="[v => !!v || 'ກະລຸນາໃສ່ຊື່']"
                ></v-text-field>
                
                <v-text-field 
                    v-model="editedItem.email" 
                    label="Email (Login) *" 
                    variant="outlined" 
                    class="mb-2"
                    prepend-inner-icon="mdi-email"
                    :rules="[v => !!v || 'ກະລຸນາໃສ່ Email', v => /.+@.+\..+/.test(v) || 'Email ບໍ່ຖືກຕ້ອງ']"
                    :disabled="!!editedId" 
                    hint="ໃຊ້ຮັບ OTP ເພື່ອເຂົ້າສູ່ລະບົບ"
                ></v-text-field>

                <v-select
                  v-model="editedItem.role"
                  :items="roles"
                  label="ສິດການໃຊ້ງານ (Role) *"
                  variant="outlined"
                  prepend-inner-icon="mdi-shield-account"
                  :rules="[v => !!v || 'ກະລຸນາເລືອກສິດ']"
                ></v-select>
              </v-card-text>
            </v-card>

            <v-expand-transition>
              <div v-if="editedItem.role === 'parent'">
                <v-card variant="outlined" class="bg-white border-primary">
                  <v-card-title class="text-subtitle-2 text-primary font-weight-bold">
                    <v-icon start size="small">mdi-face-man-profile</v-icon>
                    ເຊື່ອມໂຍງນັກຮຽນ (ລູກຫຼານ)
                  </v-card-title>
                  <v-card-text>
                    <v-alert type="info" variant="tonal" density="compact" class="mb-3 text-caption">
                      ເລືອກນັກຮຽນທີ່ຢູ່ໃນຄວາມປົກຄອງ. ລະບົບຈະອັບເດດຂໍ້ມູນນັກຮຽນໃຫ້ອັດຕະໂນມັດ.
                    </v-alert>
                    
                    <v-autocomplete
                      v-model="editedItem.student_ids"
                      :items="studentList"
                      item-title="full_name"
                      item-value="id"
                      label="ຄົ້ນຫາຊື່ນັກຮຽນ..."
                      variant="outlined"
                      multiple
                      chips
                      closable-chips
                      prepend-inner-icon="mdi-account-search"
                      :loading="loadingStudents"
                      no-data-text="ບໍ່ພົບຂໍ້ມູນນັກຮຽນ"
                    >
                      <template v-slot:item="{ props, item }">
                        <v-list-item v-bind="props" :subtitle="`ລະຫັດ: ${item.raw.student_code}`"></v-list-item>
                      </template>
                    </v-autocomplete>
                  </v-card-text>
                </v-card>
              </div>
            </v-expand-transition>

          </v-form>
        </v-card-text>

        <v-card-actions class="pa-4 pt-0 justify-end bg-grey-lighten-5">
          <v-btn variant="text" color="grey-darken-1" @click="dialog = false">ຍົກເລີກ</v-btn>
          <v-btn color="primary" variant="elevated" @click="save" :loading="saving">
            {{ editedId ? 'ອັບເດດຂໍ້ມູນ' : 'ບັນທຶກ' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// ✅ Import getAllStudents (ຫຼືຊື່ທີ່ທ່ານໃຊ້ໃນ api.js)
import { getAllUsers, createUser, updateUser, deleteUser, getAllStudents } from '../../services/api';

const users = ref([]);
const studentList = ref([]); // ✅ ເກັບລາຍຊື່ນັກຮຽນທັງໝົດ
const loading = ref(false);
const loadingStudents = ref(false);
const saving = ref(false);
const search = ref('');
const dialog = ref(false);
const valid = ref(false);
const form = ref(null);

const editedId = ref(null);
const editedItem = ref({ 
  full_name: '', 
  email: '', 
  role: 'teacher', 
  is_active: true,
  student_ids: [] // ✅ ເກັບ ID ນັກຮຽນ
});

const roles = [
  { title: 'ຄູປະຈຳວິຊາ (Teacher)', value: 'teacher' },
  { title: 'ຄູປະຈຳຫ້ອງ/ຫົວໜ້າ (Head Teacher)', value: 'head_teacher' },
  { title: 'ຜູ້ບໍລິຫານ (Admin)', value: 'admin' },
  { title: 'ຜູ້ປົກຄອງ (Parent)', value: 'parent' }
];

const headers = [
  { title: 'ID', key: 'id', align: 'start', width: '80px' },
  { title: 'ຊື່-ນາມສະກຸນ', key: 'full_name', align: 'start' },
  { title: 'Email', key: 'email', align: 'start' },
  { title: 'ສິດ (Role)', key: 'role', align: 'center' },
  { title: 'ສະຖານະ', key: 'is_active', align: 'center' },
  { title: 'ຈັດການ', key: 'actions', sortable: false, align: 'end' },
];

const getRoleColor = (role) => {
  const colors = {
    admin: 'red',
    head_teacher: 'orange',
    teacher: 'success',
    parent: 'purple',
    student: 'blue'
  };
  return colors[role] || 'grey';
};

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getAllUsers();
    users.value = res.data.map(u => ({ ...u, updating: false }));
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// ✅ ໂຫຼດນັກຮຽນມາໃສ່ Dropdown
const fetchStudents = async () => {
  loadingStudents.value = true;
  try {
    // ⚠️ ໃຫ້ແນ່ໃຈວ່າ API ນີ້ມີຢູ່ຈິງໃນ api.js ແລະ backend (GET /students/)
    const res = await getAllStudents(); 
    studentList.value = res.data;
  } catch (error) {
    console.error("Failed to load students:", error);
  } finally {
    loadingStudents.value = false;
  }
};

const openDialog = (item = null) => {
  fetchStudents(); // ໂຫຼດນັກຮຽນທຸກຄັ້ງທີ່ເປີດ Dialog
  
  if (item) {
    editedId.value = item.id;
    editedItem.value = { 
        ...item, 
        student_ids: [] // ⚠️ ປັດຈຸບັນ Backend ຍັງບໍ່ສົ່ງລາຍຊື່ລູກມາໃນ API User, ຈຶ່ງຕ້ອງເລືອກໃໝ່
    }; 
  } else {
    editedId.value = null;
    editedItem.value = { 
        full_name: '', 
        email: '', 
        role: 'parent', // Default Parent ເພື່ອໃຫ້ລອງໃຊ້ງ່າຍ
        is_active: true, 
        student_ids: [] 
    };
  }
  dialog.value = true;
};

const save = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

  saving.value = true;
  try {
    const payload = { ...editedItem.value };
    
    // ຖ້າບໍ່ແມ່ນ Parent ໃຫ້ລຶບ student_ids ອອກ (ບໍ່ຈຳເປັນ)
    if (payload.role !== 'parent') {
        delete payload.student_ids;
    }

    if (editedId.value) {
      // Update
      await updateUser(editedId.value, payload);
    } else {
      // Create (Password ຖືກຕັດອອກແລ້ວ ເພາະໃຊ້ OTP)
      await createUser(payload);
    }
    
    dialog.value = false;
    fetchData(); // Refresh list
    alert("ບັນທຶກຂໍ້ມູນສຳເລັດ! ✅");
  } catch (error) {
    alert("ເກີດຂໍ້ຜິດພາດ: " + (error.response?.data?.detail || error.message));
  } finally {
    saving.value = false;
  }
};

const toggleStatus = async (item) => {
  item.updating = true;
  try {
    await updateUser(item.id, { is_active: item.is_active });
  } catch (error) {
    item.is_active = !item.is_active; 
    alert("Update failed");
  } finally {
    item.updating = false;
  }
};

const deleteItem = async (item) => {
  if (confirm(`ຕ້ອງການລຶບ User: ${item.full_name} ແທ້ບໍ່?`)) {
    try {
      await deleteUser(item.id);
      fetchData();
    } catch (error) {
      alert("Error deleting user: " + error.message);
    }
  }
};

onMounted(fetchData);
</script>