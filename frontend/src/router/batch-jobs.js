// router/auth.js
import BatchJobCreateView from '@/components/BatchJobCreateView.vue';
import BatchJobDetailView from "@/components/BatchJobDetailView.vue";
import BatchJobEditView from "@/components/BatchJobEditView.vue";

export default [
    {
        path: '/batch-jobs',
        redirect: '/home', // 기본 경로를 /home으로 리디렉션
    },
    {
        path: '/batch-jobs/create',
        name: 'Create BatchJob',
        component: BatchJobCreateView,
    },
    {
        path: '/batch-jobs/:batch_id', // 동적 경로 정의
        name: 'BatchJobDetail',
        component: BatchJobDetailView,
        props: true, // URL 파라미터를 컴포넌트의 props로 전달
    },
    {
        path: '/batch-jobs/:batch_id/edit', // 동적 경로 정의
        name: 'Edit BatchJob',
        component: BatchJobEditView,
        props: true, // URL 파라미터를 컴포넌트의 props로 전달
    },
];
