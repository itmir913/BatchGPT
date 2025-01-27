import {fetchBatchJobProcessStatus} from "@/components/batch-job/utils/BatchJobUtils";

class BatchJobChecker {

    constructor() {
        this.intervals = new Map(); // batch_id별 interval ID 저장
        this.controllers = new Map(); // batch_id별 AbortController 저장
        this.onCompleteCallback = null;
    }

    setOnCompleteCallback(callback) {
        this.onCompleteCallback = callback;
    }

    startCheckingBatchJob(batchJobId) {
        const controller = new AbortController();
        this.controllers.set(batchJobId, controller);

        const randomInterval = Math.floor(Math.random() * 2000) + 1000; // 1초에서 3초 사이
        const intervalId = setInterval(async () => {
            try {
                const response = await fetchBatchJobProcessStatus(batchJobId);
                const status = response.data.batch_job_status;
                const result = response.data.message ?? "";  // 상태 메세지 또는 결과

                if (this.onCompleteCallback) {
                    this.onCompleteCallback(batchJobId, status, result);
                }

                if (status !== 'Pending') {
                    console.log(`BatchJob ${batchJobId} started.`);
                    this.stopCheckingBatchJob(batchJobId);
                }

            } catch (error) {
                if (error.response && error.response.status === 404) {
                    // 404 오류일 경우 아무 동작도 하지 않거나, 특정 동작 수행

                }
            }
        }, randomInterval);

        this.intervals.set(batchJobId, intervalId);

        // 5분 후 자동 중지
        setTimeout(() => {
            this.stopAllChecking();
        }, 5 * 60 * 1000);
    }

    stopCheckingBatchJob(batchJobId) {
        if (this.intervals.has(batchJobId)) {
            clearInterval(this.intervals.get(batchJobId));
            this.intervals.delete(batchJobId);
        }
        if (this.controllers.has(batchJobId)) {
            this.controllers.get(batchJobId).abort();
            this.controllers.delete(batchJobId);
        }
    }

    stopAllChecking() {
        // this.intervals는 Map 객체이므로, forEach의 콜백 함수는 (value, key) 순으로 값을 전달
        // eslint-disable-next-line no-unused-vars
        this.intervals.forEach((intervalId, _) => {
            clearInterval(intervalId);
        });
        this.intervals.clear();

        this.controllers.forEach(controller => {
            controller.abort();
        });
        this.controllers.clear();

        console.log('All batch job checks stopped.');
    }
}

export default BatchJobChecker;
