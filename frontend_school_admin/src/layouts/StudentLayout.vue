<template>
  <v-app>
    <v-app-bar color="white" elevation="0" border="b" class="px-2" density="comfortable">
      <div class="d-flex align-center">
        <v-avatar color="primary" variant="tonal" size="36" class="mr-2 rounded-lg">
          <v-icon icon="mdi-school" size="20"></v-icon>
        </v-avatar>
        <div>
          <div class="text-subtitle-2 font-weight-bold text-primary" style="line-height: 1.2;">School App</div>
          <div class="text-caption text-grey" style="font-size: 10px;">Student Tracking</div>
        </div>
      </div>

      <v-spacer></v-spacer>

      <div class="d-none d-sm-flex align-center mr-2">
        <div class="text-right mr-3">
          <div class="text-subtitle-2 font-weight-bold">{{ user.full_name || 'Student' }}</div>
          <div class="text-caption text-grey">{{ roleText }}</div>
        </div>
        <v-avatar color="grey-lighten-3" size="40">
           <v-img src="https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Prescription02&hairColor=Black&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Happy&eyebrowType=Default&mouthType=Smile&skinColor=Light"></v-img>
        </v-avatar>
      </div>

      <v-btn icon color="grey" variant="text" class="d-none d-sm-flex" @click="handleLogout">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer
      v-if="!mobile"
      v-model="drawer"
      :rail="rail"
      permanent
      @click="rail = false"
      elevation="1"
    >
      <v-list density="compact" nav class="mt-2">
        <template v-for="(item, i) in filteredMenuItems" :key="i">
           <v-list-item
            :prepend-icon="item.icon"
            :title="item.title"
            :to="item.route"
            active-color="primary"
            rounded="lg"
            class="mb-1"
          ></v-list-item>
        </template>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn block variant="text" icon="mdi-chevron-left" @click.stop="rail = !rail"></v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-5 pb-16"> 
      <router-view v-slot="{ Component }">
        <v-fade-transition mode="out-in">
          <component :is="Component" />
        </v-fade-transition>
      </router-view>
    </v-main>

    <v-bottom-navigation
      v-if="mobile"
      grow
      color="primary"
      mode="shift"
      elevation="4"
      class="rounded-t-xl"
    >
      <v-btn to="/student/dashboard">
        <v-icon>mdi-view-dashboard-outline</v-icon>
        <span>ພາບລວມ</span>
      </v-btn>

      <v-btn to="/student/schedule">
        <v-icon>mdi-calendar-clock-outline</v-icon>
        <span>ຕາຕະລາງ</span>
      </v-btn>

      <v-btn to="/student/assignments">
        <v-badge v-if="pendingCount > 0" color="error" dot>
          <v-icon>mdi-book-open-variant</v-icon>
        </v-badge>
        <v-icon v-else>mdi-book-open-page-variant-outline</v-icon>
        <span>ວຽກບ້ານ</span>
      </v-btn>

      <v-btn to="/student/grades">
        <v-icon>mdi-chart-line</v-icon>
        <span>ຜົນຮຽນ</span>
      </v-btn>

      <v-btn to="/student/profile">
        <v-icon>mdi-account-circle-outline</v-icon>
        <span>ໂປຣໄຟລ໌</span>
      </v-btn>
    </v-bottom-navigation>

  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplay } from 'vuetify';
import api from '../services/api';

const router = useRouter();
const { mobile } = useDisplay(); // Check screen size

// State
const drawer = ref(true);
const rail = ref(false);
const user = ref({});
const role = ref('');
const pendingCount = ref(0); // For assignment badge

// Menu Items (For Desktop Drawer)
const menuItems = [
  { title: 'ພາບລວມ (Dashboard)', icon: 'mdi-view-dashboard', route: '/student/dashboard', roles: ['student', 'parent'] },
  { title: 'ຕາຕະລາງຮຽນ', icon: 'mdi-calendar-clock', route: '/student/schedule', roles: ['student', 'parent'] },
  { title: 'ວຽກບ້ານ', icon: 'mdi-book-open-variant', route: '/student/assignments', roles: ['student', 'parent'] },
  { title: 'ຜົນການຮຽນ', icon: 'mdi-chart-line', route: '/student/grades', roles: ['student', 'parent'] },
  { title: 'ປະຫວັດສ່ວນຕົວ', icon: 'mdi-account-details', route: '/student/profile', roles: ['student'] },
];

onMounted(async () => {
  const userData = localStorage.getItem('user');
  const userRole = localStorage.getItem('role');
  
  if (userData) user.value = JSON.parse(userData);
  if (userRole) role.value = userRole;

  // Fetch pending assignments count for badge
  try {
      const res = await api.get('/lms/student/assignments');
      pendingCount.value = res.data.filter(x => !x.submission).length;
  } catch (e) {
      console.log("No assignments");
  }
});

const roleText = computed(() => {
    return role.value === 'parent' ? 'Parent View' : 'Student';
});

const filteredMenuItems = computed(() => {
    if (role.value === 'parent') {
        return menuItems.filter(item => item.roles.includes('parent'));
    }
    return menuItems;
});

const handleLogout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<style scoped>
/* App Bar styling */
.v-app-bar {
    backdrop-filter: blur(10px);
    background-color: rgba(255, 255, 255, 0.9) !important;
}

/* Bottom Nav Styling */
.v-bottom-navigation {
    position: fixed; 
    bottom: 0; 
    left: 0; 
    right: 0;
    z-index: 1000;
    border-top: 1px solid #eee;
}

.v-bottom-navigation .v-btn {
    font-size: 10px; /* Text small */
    letter-spacing: 0;
    font-weight: 500;
}

/* Animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>