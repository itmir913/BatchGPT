// router/auth.js
import LoginView from '@/components/auth/LoginView.vue';
import RegisterView from '@/components/auth/RegisterView.vue';

export default [
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
