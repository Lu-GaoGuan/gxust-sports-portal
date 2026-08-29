import { createRouter, createWebHistory } from 'vue-router'

import ActivitiesView from '../views/ActivitiesView.vue'
import CurrentTeamView from '../views/CurrentTeamView.vue'
import DepartmentView from '../views/DepartmentView.vue'
import FaqView from '../views/FaqView.vue'
import HomeView from '../views/HomeView.vue'
import LegacyView from '../views/LegacyView.vue'
import MessagesView from '../views/MessagesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    { path: '/department', name: 'department', component: DepartmentView },
    { path: '/legacy', name: 'legacy', component: LegacyView },
    { path: '/team-six', name: 'team-six', component: CurrentTeamView },
    { path: '/activities', name: 'activities', component: ActivitiesView },
    { path: '/faq', name: 'faq', component: FaqView },
    { path: '/messages', name: 'messages', component: MessagesView },
  ],
  scrollBehavior() { return { top: 0 } },
})

export default router
