import {createRouter, createWebHistory} from 'vue-router';

import HomeView from '@/components/HomeView.vue';
import LoginView from '@/components/LoginView.vue';
import RegisterView from '@/components/RegisterView.vue';

import axios from '@/configs/axios'; // Axios 설정 가져오기

const routes = [
    {
        path: '/',
        redirect: '/home', // 기본 경로를 /home으로 리디렉션
    },
    {
        path: '/home',
        name: 'Home',
        component: HomeView,
        meta: {requiresAuth: true}, // 인증이 필요한 경로
    },
    {
        path: '/login',
        name: 'Login',
        component: LoginView,
    },
    {
        path: '/register',
        name: 'Register',
        component: RegisterView,
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),  // 히스토리 모드 사용
    routes,
});

// 글로벌 네비게이션 가드
router.beforeEach(async (to, from, next) => {
    // 인증이 필요한 경로인지 확인
    if (to.matched.some((record) => record.meta.requiresAuth)) {
        try {
            // Django API 호출로 로그인 여부 확인
            const response = await axios.get('/api/auth/check/', {withCredentials: true});
            if (response.data.is_authenticated) {
                next(); // 인증된 경우 정상적으로 이동
            } else {
                next('/login'); // 인증되지 않은 경우 로그인 페이지로 이동
            }
        } catch (error) {
            console.error('Error checking authentication:', error);
            next('/login'); // 에러 발생 시에도 로그인 페이지로 이동
        }
    } else {
        next(); // 인증이 필요하지 않은 경로는 그대로 진행
    }
});

export default router;
