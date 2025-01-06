// router/home.js
import HomeView from '@/components/home/HomeView.vue';

export default [
    {
        path: '/home',
        name: 'Home',
        component: HomeView,
        meta: {requiresAuth: true}, // 인증 필요 여부 설정
    },
];
