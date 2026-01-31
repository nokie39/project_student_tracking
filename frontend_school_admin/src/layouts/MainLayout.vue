<template>
  <v-layout>
    <v-navigation-drawer v-model="drawer" color="primary" elevation="2" class="border-none">
      <div class="d-flex flex-column align-center pa-6">
        <v-avatar color="white" size="70" class="elevation-3 mb-3">
          <span class="text-h4 font-weight-bold text-primary">{{ userInitial }}</span>
        </v-avatar>
        <div class="text-white font-weight-bold text-h6">Admin Portal</div>
        <div class="text-blue-lighten-4 text-caption">{{ userName }}</div>
      </div>

      <v-divider class="border-opacity-25 mb-2"></v-divider>

      <v-list density="compact" nav class="pa-2">
        <v-list-item
          v-for="(item, i) in adminMenus"
          :key="i"
          :to="item.path"
          active-class="bg-white text-primary font-weight-bold elevation-1"
          rounded="lg"
          class="mb-1"
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon"></v-icon>
          </template>
          <v-list-item-title class="text-body-2">{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-4">
          <v-btn block color="white" variant="outlined" class="text-white" @click="logout">
            <v-icon start>mdi-logout</v-icon>
            ອອກຈາກລະບົບ
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar elevation="0" class="border-b bg-white">
      <v-app-bar-nav-icon @click="drawer = !drawer" color="grey-darken-2"></v-app-bar-nav-icon>
      
      <v-app-bar-title class="text-grey-darken-2 font-weight-bold">
        {{ currentPageTitle }}
      </v-app-bar-title>

      <template v-slot:append>
        <v-chip color="primary" variant="flat" size="small" class="mr-4">
          <v-icon start icon="mdi-shield-account"></v-icon>
          Administrator
        </v-chip>
      </template>
    </v-app-bar>

    <v-main class="bg-grey-lighten-5">
      <v-container fluid class="pa-6 h-100">
        <router-view v-slot="{ Component }">
          <v-fade-transition mode="out-in">
            <component :is="Component" />
          </v-fade-transition>
        </router-view>
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

// User Info from LocalStorage
const userName = localStorage.getItem('user') || 'Admin';
const userInitial = computed(() => userName.charAt(0).toUpperCase());

// ✅ Admin Specific Menu (ລວມທຸກເມນູໃຫ້ Admin ເຫັນໝົດ)
const adminMenus = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', path: '/admin/dashboard' },
  
  // 1. ຈັດການຂໍ້ມູນຫຼັກ
  { title: 'ຈັດການປີການສຶກສາ', icon: 'mdi-calendar-range', path: '/admin/years' },
  { title: 'ຈັດການຜູ້ໃຊ້', icon: 'mdi-account-cog-outline', path: '/admin/users' },
  { title: 'ຈັດການຫ້ອງຮຽນ', icon: 'mdi-google-classroom', path: '/admin/classes' },
  { title: 'ຈັດການນັກຮຽນ', icon: 'mdi-account-school-outline', path: '/admin/students' },

  // 2. ຈັດການການຮຽນ-ການສອນ (Admin ກໍຄວນເຫັນ)
  { title: 'ຈັດຕາຕະລາງ', icon: 'mdi-calendar-import', path: '/admin/academic' },
  { title: 'ເຊັກຊື່', icon: 'mdi-calendar-check-outline', path: '/admin/attendance' },
  { title: 'ຄະແນນ', icon: 'mdi-clipboard-list-outline', path: '/admin/grades' },
  //{ title: 'ພຶດຕິກຳ (Behavior)', icon: 'mdi-star-circle-outline', path: '/admin/behavior' },
  { title: 'ສັ່ງວຽກບ້ານ', icon: 'mdi-book-open-variant-outline', path: '/admin/lms' },
];

// Current Page Title Logic
const currentPageTitle = computed(() => {
  const current = adminMenus.find(m => m.path === route.path);
  return current ? current.title : 'Admin Dashboard';
});

const logout = () => {
  if(confirm("ຕ້ອງການອອກຈາກລະບົບແທ້ບໍ່?")) {
    localStorage.clear();
    router.push('/login');
  }
};
</script>

<style scoped>
.v-navigation-drawer {
  border: none;
}
</style>