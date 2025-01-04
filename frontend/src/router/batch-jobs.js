// router/auth.js
import BatchJobCreateView from '@/components/BatchJobCreateView.vue';

export default [
    {
        path: '/batch-job/create',
        name: 'Create BatchJob',
        component: BatchJobCreateView,
    },
];
