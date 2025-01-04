// router/auth.js
import LoginView from '@/components/LoginView.vue';
import RegisterView from '@/components/RegisterView.vue';

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
