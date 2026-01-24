<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2 class="text-primary mb-4">
          <v-icon icon="mdi-account-group" class="mr-2"></v-icon>
          ລາຍຊື່ຄູໃນສັງກັດ (Teachers List)
        </h2>
      </v-col>
    </v-row>

    <v-card elevation="2" rounded="lg">
      <v-card-title class="d-flex align-center py-3">
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="ຄົ້ນຫາລາຍຊື່..."
          single-line
          hide-details
          density="compact"
          variant="outlined"
          class="mr-4"
          style="max-width: 300px"
        ></v-text-field>
        <v-spacer></v-spacer>
        <v-btn color="primary" prepend-icon="mdi-account-plus" variant="elevated" @click="showAddAlert">
          ເພີ່ມຄູໃໝ່
        </v-btn>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="teachers"
        :search="search"
        :loading="loading"
        no-data-text="ບໍ່ພົບຂໍ້ມູນຄູໃນລະບົບ"
      >
        <template v-slot:item.full_name="{ item }">
          <div class="d-flex align-center py-2">
            <v-avatar color="indigo-lighten-4" size="36" class="mr-3">
              <span class="text-indigo font-weight-bold">{{ item.full_name ? item.full_name.charAt(0) : '?' }}</span>
            </v-avatar>
            <div>
              <div class="font-weight-bold">{{ item.full_name }}</div>
              <div class="text-caption text-grey">ID: {{ item.id }}</div>
            </div>
          </div>
        </template>

        <template v-slot:item.email="{ item }">
          <v-chip size="small" variant="outlined" color="grey-darken-1">
            <v-icon start size="x-small">mdi-email</v-icon>
            {{ item.email }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn 
            icon="mdi-eye" 
            size="small" 
            color="info" 
            variant="text" 
            class="mr-1"
            @click="openDetail(item)"
          ></v-btn>
          <v-btn 
            icon="mdi-pencil" 
            size="small" 
            color="primary" 
            variant="text"
            @click="editTeacher(item)"
          ></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="500px">
      <v-card rounded="xl">
        <v-card-title class="bg-indigo text-white pa-4">
          ຂໍ້ມູນຄູ-ອາຈານ
        </v-card-title>
        <v-card-text class="pa-4">
          <div class="text-center mb-4">
            <v-avatar color="indigo-lighten-4" size="80">
              <span class="text-h3 text-indigo font-weight-bold">
                {{ selectedTeacher.full_name ? selectedTeacher.full_name.charAt(0) : '' }}
              </span>
            </v-avatar>
            <h3 class="mt-2">{{ selectedTeacher.full_name }}</h3>
            <div class="text-grey">{{ selectedTeacher.email }}</div>
          </div>
          
          <v-divider class="mb-3"></v-divider>
          
          <v-list density="compact">
            <v-list-item prepend-icon="mdi-identifier" title="ລະຫັດຜູ້ໃຊ້ (ID)" :subtitle="selectedTeacher.id"></v-list-item>
            <v-list-item prepend-icon="mdi-account-tie" title="ສະຖານະ" subtitle="ຄູປະຈຳການ (Teacher)"></v-list-item>
            <v-list-item prepend-icon="mdi-phone" title="ເບີໂທ" subtitle="- ບໍ່ມີຂໍ້ມູນ -"></v-list-item>
          </v-list>

        </v-card-text>
        <v-card-actions class="justify-end pa-4 bg-grey-lighten-5">
          <v-btn color="grey-darken-1" variant="text" @click="dialog = false">ປິດ</v-btn>
          <v-btn color="indigo" variant="elevated" @click="dialog = false">ຮັບຊາບ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getAllTeachers } from '../../services/api';

const teachers = ref([]);
const loading = ref(false);
const search = ref('');

// Dialog state
const dialog = ref(false);
const selectedTeacher = ref({});

const headers = [
  { title: 'ຊື່ ແລະ ນາມສະກຸນ', key: 'full_name', align: 'start' },
  { title: 'Email', key: 'email', align: 'start' },
  { title: 'ຈັດການ', key: 'actions', sortable: false, align: 'end' },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getAllTeachers();
    teachers.value = res.data;
  } catch (error) {
    console.error("Error fetching teachers:", error);
  } finally {
    loading.value = false;
  }
};

// 🔥 Functions ສຳລັບປຸ່ມ
const openDetail = (item) => {
  selectedTeacher.value = item;
  dialog.value = true;
};

const editTeacher = (item) => {
  alert(`ກຳລັງພັດທະນາລະບົບແກ້ໄຂຂໍ້ມູນຂອງ: ${item.full_name}`);
};

const showAddAlert = () => {
  alert("ຟັງຊັນເພີ່ມຄູໃໝ່ ຈະຢູ່ໃນ Phase ຖັດໄປ (Admin Management)");
};

onMounted(fetchData);
</script>