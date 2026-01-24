import { createRouter, createWebHistory } from 'vue-router'

// --- Auth & Layouts ---
import Login from '../views/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'
import StudentLayout from '../layouts/StudentLayout.vue'
import HeadLayout from '../layouts/HeadLayout.vue'

// --- Admin / Teacher Views ---
import Dashboard from '../views/admin/Dashboard.vue'
import Students from '../views/admin/Students.vue'
import Attendance from '../views/Attendance.vue' 
import Grades from '../views/Grades.vue'
import LMS from '../views/LMS.vue'
import ScheduleAdmin from '../views/ScheduleAdmin.vue'
import BehaviorEntry from '../views/teacher/BehaviorEntry.vue'
import StudentDetail from '../views/student/StudentDetail.vue' 

// --- Student Side Views ---
import MyAssignments from '../views/student/MyAssignments.vue'
import MySchedule from '../views/student/Schedule.vue'
import StudentDashboard from '../views/student/Dashboard.vue'

// --- Head Teacher Views ---
import TeacherMonitor from '../views/head/TeacherMonitor.vue'
import Reports from '../views/head/Reports.vue'

// --- Teacher Views 
import TeacherLayout from '../layouts/TeacherLayout.vue';
import TeacherDashboard from '../views/teacher/TeacherDashboard.vue';

// --- Parent Views (✅ ເພີ່ມໃໝ່) ---
const ParentSelectChild = () => import('../views/parent/SelectChild.vue')
const ParentDashboard = () => import('../views/parent/ParentDashboard.vue')

const routes = [
  // 0. ໜ້າ Login
  { path: '/login', component: Login, name: 'Login' },
  { path: '/', redirect: '/login' },

  // 1. ທາງຂອງ Admin / Teacher
  { 
    path: '/admin',
    component: MainLayout, 
    meta: { requiresAuth: true, roles: ['admin', 'teacher'] },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: Dashboard },
      
      // ຈັດການຂໍ້ມູນພື້ນຖານ (Admin Only)
      { 
        path: 'years', 
        name: 'AcademicYears', 
        component: () => import('../views/admin/AcademicYears.vue'),
        meta: { roles: ['admin'] } 
      },
      { 
        path: 'classes', 
        name: 'AdminClasses', 
        component: () => import('../views/admin/Classes.vue'),
        meta: { roles: ['admin'] } 
      },
      { 
        path: 'users', 
        name: 'AdminUsers', 
        component: () => import('../views/admin/Users.vue'), 
        meta: { roles: ['admin'] } 
      },

      // ຈັດການການຮຽນການສອນ (Admin & Teacher)
      { path: 'students', name: 'AdminStudents', component: Students },
      { path: 'student-detail/:id', name: 'StudentDetail', component: StudentDetail },
      
      { path: 'academic', name: 'AdminAcademic', component: ScheduleAdmin },
      
      { path: 'attendance', name: 'AdminAttendance', component: Attendance },
      { path: 'grades', name: 'AdminGrades', component: Grades },
      { path: 'behavior', name: 'AdminBehavior', component: BehaviorEntry },
      { path: 'lms', name: 'AdminLMS', component: LMS },
    ]
  },

  {
    path: '/teacher',
    component: TeacherLayout, // ✅ ໃຊ້ Layout ໃໝ່ທີ່ສ້າງຂຶ້ນ
    meta: { requiresAuth: true, roles: ['teacher'] },
    children: [
      { 
        path: 'dashboard', 
        name: 'TeacherDashboard', 
        component: TeacherDashboard 
      },
    ]
  },

  // 2. ທາງຂອງ Head Teacher
  {
    path: '/head',
    component: HeadLayout,
    meta: { requiresAuth: true, roles: ['head_teacher'] },
    children: [
      { path: 'monitor', name: 'HeadMonitor', component: TeacherMonitor },
      { path: 'reports', name: 'HeadReports', component: Reports },
      { path: 'teachers', name: 'HeadTeachers', component: () => import('../views/head/TeachersList.vue') },
      { path: 'student-detail/:id', name: 'HeadStudentDetail', component: StudentDetail },
    ]
  },

  // 3. ທາງຂອງ Student
  {
    path: '/student',
    component: StudentLayout,
    meta: { requiresAuth: true, roles: ['student'] },
    children: [
      { path: 'dashboard', name: 'StudentDashboard', component: StudentDashboard },
      { path: 'assignments', name: 'StudentAssignments', component: MyAssignments },
      { path: 'schedule', name: 'StudentSchedule', component: MySchedule },
      { path: 'my-portfolio', name: 'MyPortfolio', component: StudentDetail },
      { 
        path: 'profile', 
        name: 'StudentProfile', 
        component: () => import('../views/student/Profile.vue') 
      },
      { 
      path: 'grades', 
      name: 'StudentGrades', 
      component: () => import('../views/student/MyGrades.vue') 
    },
    ]
  },

  // 4. ທາງຂອງ Parent (✅ ເພີ່ມໃໝ່)
  {
    path: '/parent',
    // ໃຊ້ StudentLayout ເພື່ອໃຫ້ຮອງຮັບ Mobile View (ແຕ່ຕ້ອງເຊື່ອງ Nav ບາງອັນໃນ Layout ເອົາ)
    component: StudentLayout, 
    meta: { requiresAuth: true, roles: ['parent'] },
    children: [
      { 
        path: 'select-child', 
        name: 'ParentSelectChild', 
        component: ParentSelectChild,
        meta: { hideNavbar: true } // ສຳລັບເຊື່ອງ Navbar ໃນໜ້າເລືອກລູກ
      },
      { 
        path: 'dashboard/:studentId', 
        name: 'ParentDashboard', 
        component: ParentDashboard 
      },
      { 
        path: 'grades/:studentId', 
        name: 'ParentChildGrades', 
        component: () => import('../views/parent/ChildGrades.vue') 
      },
      { 
        path: 'assignments/:studentId', 
        name: 'ParentChildAssignments', 
        component: () => import('../views/parent/ChildAssignments.vue') 
      },
    ]
  },

  // Catch-all route
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// --- Security & Role Guard ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  // 1. ກວດສອບ Auth
  if (to.meta.requiresAuth && !token) {
    return next('/login');
  }

  // 2. ຖ້າ Login ແລ້ວແຕ່ຈະໄປໜ້າ Login ຄືນ -> ເຕະໄປ Dashboard ຕາມ Role
  if (to.path === '/login' && token) {
    if (userRole === 'student') return next('/student/dashboard');
    if (userRole === 'head_teacher') return next('/head/monitor');
    if (userRole === 'parent') return next('/parent/select-child'); // ✅ Parent ໄປໜ້າເລືອກລູກ
    return next('/admin/dashboard');
  }

  // 3. ກວດສອບ Role-based Access
  if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    // ຖ້າສິດບໍ່ເຖິງ ໃຫ້ສົ່ງໄປໜ້າ Dashboard ຂອງ Role ຕົນເອງ
    if (userRole === 'student') return next('/student/dashboard');
    if (userRole === 'head_teacher') return next('/head/monitor');
    if (userRole === 'parent') return next('/parent/select-child'); // ✅
    return next('/admin/dashboard');
  }

  next();
});

export default router;