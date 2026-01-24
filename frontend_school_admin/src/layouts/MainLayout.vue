<template>
  <v-layout>
    <v-navigation-drawer v-model="drawer" color="primary">
      <div class="d-flex flex-column align-center pa-4">
        <v-avatar color="white" size="64">
          <span class="text-h5 text-primary font-weight-bold">ST</span>
        </v-avatar>
        <div class="text-white mt-3 font-weight-bold">Student Tracking</div>
        <div class="text-white text-caption">{{ userRole.toUpperCase() }}</div>
      </div>

      <v-divider class="border-opacity-50"></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          v-for="(item, i) in filteredMenus"
          :key="i"
          :to="item.path"
          color="white" 
          rounded="xl"
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon"></v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn block color="error" variant="tonal" @click="logout">
            <v-icon start>mdi-logout</v-icon>
            ອອກຈາກລະບົບ
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>{{ currentPageTitle }}</v-app-bar-title>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const drawer = ref(true);
const router = useRouter();
const route = useRoute();
const userRole = localStorage.getItem('role') || 'guest';

/**
 * 💡 ຈຸດປັບປຸງ: ອັບເດດ Path ໃຫ້ມີ /admin/ ນຳໜ້າ 
 * ເພື່ອໃຫ້ກົງກັບ children routes ໃນ router/index.js
 */
const allMenus = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', path: '/admin/dashboard', roles: ['admin', 'teacher'] },
  { title: 'ຈັດການປີການສຶກສາ', icon: 'mdi-calendar-range', path: '/admin/years', roles: ['admin'] },
  { title: 'ຈັດການຫ້ອງຮຽນ', icon: 'mdi-google-classroom', path: '/admin/classes', roles: ['admin'] },
  { title: 'ຈັດການຜູ້ໃຊ້', icon: 'mdi-account-cog', path: '/admin/users', roles: ['admin'] },
  { title: 'ຈັດການນັກຮຽນ', icon: 'mdi-account-school', path: '/admin/students', roles: ['admin', 'teacher'] },
  { title: 'ຈັດການວິຊາການ', icon: 'mdi-school', path: '/admin/academic', roles: ['admin'] },
  { title: 'ເຊັກຊື່', icon: 'mdi-calendar-check', path: '/admin/attendance', roles: ['admin', 'teacher'] },
  { title: 'ຄະແນນ', icon: 'mdi-clipboard-list-outline', path: '/admin/grades', roles: ['admin', 'teacher'] },
  { title: 'ພຶດຕິກຳ/ຈິດພິໄສ', icon: 'mdi-star-circle', path: '/admin/behavior', roles: ['admin', 'teacher'] },
  { title: 'ສັ່ງວຽກບ້ານ (LMS)', icon: 'mdi-book-open-variant', path: '/admin/lms', roles: ['admin', 'teacher'] },
];

// ກອງເມນູຕາມສິດ (Role)
const filteredMenus = computed(() => {
  return allMenus.filter(item => item.roles.includes(userRole));
});

// ຊື່ໜ້າປັດຈຸບັນ
const currentPageTitle = computed(() => {
  const current = allMenus.find(m => m.path === route.path);
  return current ? current.title : 'Student Tracking';
});

const logout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>