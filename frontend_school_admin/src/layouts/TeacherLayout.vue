<template>
  <v-layout>
    <v-navigation-drawer v-model="drawer" color="teal-darken-1" elevation="2">
      <div class="d-flex flex-column align-center pa-6">
        <v-avatar color="white" size="70" class="elevation-2">
          <v-icon icon="mdi-account-tie" size="40" color="teal-darken-1"></v-icon>
        </v-avatar>
        <div class="text-white mt-3 font-weight-bold text-h6">Teacher Portal</div>
        <div class="text-teal-lighten-4 text-caption">{{ teacherName }}</div>
      </div>

      <v-divider class="border-opacity-25 mb-2"></v-divider>

      <v-list density="compact" nav class="pa-2">
        <v-list-item
          v-for="(item, i) in teacherMenus"
          :key="i"
          :to="item.path"
          active-class="bg-white text-teal-darken-2 font-weight-bold elevation-1"
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
          <v-btn block color="red-lighten-4" class="text-red-darken-4" variant="flat" @click="logout">
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
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" icon>
              <v-avatar color="teal-lighten-5" size="36">
                <span class="text-teal font-weight-bold">{{ teacherInitial }}</span>
              </v-avatar>
            </v-btn>
          </template>
          <v-list width="200" density="compact" class="rounded-lg elevation-4">
            <v-list-item prepend-icon="mdi-account-circle" title="ໂປຣໄຟລ໌"></v-list-item>
            <v-divider></v-divider>
            <v-list-item prepend-icon="mdi-logout" title="ອອກຈາກລະບົບ" @click="logout" class="text-error"></v-list-item>
          </v-list>
        </v-menu>
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

// Get User Info from LocalStorage
const teacherName = localStorage.getItem('user') || 'Teacher';
const teacherInitial = computed(() => teacherName.charAt(0).toUpperCase());

// ✅ Teacher Specific Menu
const teacherMenus = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', path: '/teacher/dashboard' },
  // { title: 'ຕາຕະລາງສອນ', icon: 'mdi-calendar-clock', path: '/teacher/schedule' }, // Future feature
  // { title: 'ຈັດການນັກຮຽນ', icon: 'mdi-account-school-outline', path: '/teacher/students' }, // Usually inside Dashboard now
  // { title: 'ເຊັກຊື່', icon: 'mdi-calendar-check', path: '/teacher/attendance' }, // Moved to Dashboard tabs
  // { title: 'ຄະແນນ & ເກຣດ', icon: 'mdi-clipboard-text-outline', path: '/teacher/grades' }, // Future feature
  // { title: 'ວຽກບ້ານ (LMS)', icon: 'mdi-book-open-page-variant-outline', path: '/teacher/lms' }, // Future feature
];

// Determine Current Page Title
const currentPageTitle = computed(() => {
  const current = teacherMenus.find(m => m.path === route.path);
  return current ? current.title : 'Teacher Portal';
});

const logout = () => {
  if(confirm("ຕ້ອງການອອກຈາກລະບົບແທ້ບໍ່?")) {
    localStorage.clear();
    router.push('/login');
  }
};
</script>

<style scoped>
/* Optional: Soft shadow for sidebar */
.v-navigation-drawer {
  border: none;
}
</style>