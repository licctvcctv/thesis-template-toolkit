import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Layout from '@/layout/index.vue'
import DepartmentManage from '@/views/department/DepartmentManage.vue'
import DoctorManage from '@/views/doctor/DoctorManage.vue'
import PatientManage from '@/views/patient/PatientManage.vue'
import MedicineManage from '@/views/medicine/MedicineManage.vue'
import MedicalRecordManage from '@/views/medicalRecord/MedicalRecordManage.vue'
import FollowupTaskManage from '@/views/followupTask/FollowupTaskManage.vue'
import StatisticsManage from '@/views/statistics/StatisticsManage.vue'
import SystemSettings from '@/views/system/SystemSettings.vue'
import DoctorPatientManage from '@/views/doctor/DoctorPatientManage.vue'
import DoctorFollowupTask from '@/views/doctor/DoctorFollowupTask.vue'
import DoctorFollowupRecord from '@/views/doctor/DoctorFollowupRecord.vue'
import PersonalCenter from '@/views/doctor/PersonalCenter.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    component: Layout,
    redirect: (to) => {
      const role = localStorage.getItem('userRole')
      return role === 'doctor' ? '/doctor-patient' : '/department'
    },
    children: [
      {
        path: '/department',
        name: 'DepartmentManage',
        component: DepartmentManage,
        meta: { role: 'admin' }
      },
      {
        path: '/doctor',
        name: 'DoctorManage',
        component: DoctorManage,
        meta: { role: 'admin' }
      },
      {
        path: '/patient',
        name: 'PatientManage',
        component: PatientManage,
        meta: { role: 'admin' }
      },
      {
        path: '/medicine',
        name: 'MedicineManage',
        component: MedicineManage,
        meta: { role: 'admin' }
      },
      {
        path: '/medical-record',
        name: 'MedicalRecordManage',
        component: MedicalRecordManage,
        meta: { role: 'admin' }
      },
      {
        path: '/followup-task',
        name: 'FollowupTaskManage',
        component: FollowupTaskManage,
        meta: { role: 'admin' }
      },
      {
        path: '/statistics',
        name: 'StatisticsManage',
        component: StatisticsManage,
        meta: { role: 'admin' }
      },
      {
        path: '/system-settings',
        name: 'SystemSettings',
        component: SystemSettings,
        meta: { role: 'admin' }
      },
      {
        path: '/doctor-patient',
        name: 'DoctorPatientManage',
        component: DoctorPatientManage,
        meta: { role: 'doctor' }
      },
      {
        path: '/doctor-followup-task',
        name: 'DoctorFollowupTask',
        component: DoctorFollowupTask,
        meta: { role: 'doctor' }
      },
      {
        path: '/doctor-followup-record',
        name: 'DoctorFollowupRecord',
        component: DoctorFollowupRecord,
        meta: { role: 'doctor' }
      },
      {
        path: '/personal-center',
        name: 'PersonalCenter',
        component: PersonalCenter,
        meta: { role: 'doctor' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('userRole')
  
  if (to.path === '/login') {
    if (token) {
      const redirectPath = role === 'doctor' ? '/doctor-patient' : '/department'
      next(redirectPath)
    } else {
      next()
    }
  } else {
    if (token) {
      if (to.meta.role && to.meta.role !== role) {
        const redirectPath = role === 'doctor' ? '/doctor-patient' : '/department'
        next(redirectPath)
      } else {
        next()
      }
    } else {
      next('/login')
    }
  }
})

export default router
