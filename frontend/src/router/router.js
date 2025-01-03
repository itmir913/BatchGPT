// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HelloWorld from '../components/HelloWorld.vue';  // 홈 컴포넌트
import Register from '../components/Register.vue';  // Register 컴포넌트

const routes = [
    {
        path: '/',
        name: 'HelloWorld',
        component: HelloWorld,
    },
    {
        path: '/register',  // 이 경로에서 Register 컴포넌트 표시
        name: 'Register',
        component: Register,
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),  // 히스토리 모드 사용
    routes,
});

export default router;
