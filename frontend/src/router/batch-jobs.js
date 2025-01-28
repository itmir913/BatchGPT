// router/auth.js
import BatchJobCreateView from '@/components/batch-job/create/BatchJobCreateView.vue';
import BatchJobDetailView from "@/components/batch-job/detail/BatchJobDetailView.vue";
import BatchJobEditView from "@/components/batch-job/create/BatchJobEditView.vue";
import BatchJobConfigView from "@/components/batch-job/configs/BatchJobConfigsView.vue";
import BatchJobPreView from "@/components/batch-job/previews/BatchJobPreView.vue";
import BatchJobResultView from "@/components/batch-job/result/BatchJobResultView.vue";

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
    {
        path: '/batch-jobs/:batch_id/configs', // 동적 경로 정의
        name: 'Configure Prompt',
        component: BatchJobConfigView,
        props: true, // URL 파라미터를 컴포넌트의 props로 전달
    },
    {
        path: '/batch-jobs/:batch_id/preview', // 동적 경로 정의
        name: 'BatchJob Preview',
        component: BatchJobPreView,
        props: true, // URL 파라미터를 컴포넌트의 props로 전달
    },
    {
        path: '/batch-jobs/:batch_id/run', // 동적 경로 정의
        name: 'BatchJob Result',
        component: BatchJobResultView,
        props: true, // URL 파라미터를 컴포넌트의 props로 전달
    },
];
