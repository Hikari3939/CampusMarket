import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/user';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  { 
    path: '/product/:id',
    component: () => import('../views/ProductDetail.vue')
  },
  { 
    path: '/publish', 
    component: () => import('../views/Publish.vue'),
    meta: { requiresAuth: true } // 需要登录
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true } // 需要登录
  },
  {
    path: '/chat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true } // 需要登录
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  // 判断目标路由是否需要鉴权，且当前用户没有 token
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login'); // 未登录，强制去登录页
  } else {
    next();
  }
});

export default router;