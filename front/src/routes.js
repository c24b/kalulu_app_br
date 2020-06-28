import HeatmapsPage from './components/HeatmapsPage.vue'
import SelectSubject from './components/SelectSubject.vue'
import ClassroomPage from './components/ClassroomPage.vue'
import SelectClassroom from './components/SelectClassroom.vue'
import StudentPage from './components/StudentPage.vue'
import AdminPage from './components/AdminPage.vue'
export const routes = [
    { 
      path: '', 
      component: SelectClassroom,
      name:"classroomSelect"
    },
    { 
      path: '/classroom/:cid/', 
      component: SelectSubject, 
      name: 'subjectSelect'
    },

    { 
      path: '/classroom/:cid/subject/:sub/', 
      component: ClassroomPage, 
      name: 'classroomPage' },

    { 
      path: '/student/:stid/', 
      component: SelectSubject, 
    },
    { 
      path: '/student/:stid/subject/:sub/', //'/classroom/:cid/subject/:sub/student/:stid/'
      component: StudentPage, 
      name: 'studentPage', 
    },
    { 
      path: '/confusion', 
      component: HeatmapsPage, 
      name: 'confusion', 
    }, 
    { 
      path: '/confusion/subject/:sub', 
      component: HeatmapsPage, 
      name: 'confusionSubject', 
    },
    { 
      path: '/confusion/student/:stid', 
      component: HeatmapsPage, 
      name: 'confusionStudent', 
    },
    { 
      path: '/confusion/subject/:sub/student/:stid', 
      component: HeatmapsPage, 
      name: 'confusionStudentSubject', 
    },
    // { 
    //   path: '/admin', 
    //   component: AdminPage, 
    //   name: 'admin', 
    // }
]