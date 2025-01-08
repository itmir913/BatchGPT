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

        const randomInterval = Math.floor(Math.random() * 4000) + 3000; // 3초에서 7초 사이
        const intervalId = setInterval(async () => {
            try {
                const response = await fetchBatchJobProcessStatus(batchJobId);
                const status = response.data.status;
                const result = response.data.message ?? "";  // 상태 메세지 또는 결과

                if (this.onCompleteCallback) {
                    this.onCompleteCallback(batchJobId, status, result);
                }

                if (status !== 'Pending') {
                    console.log(`BatchJob ${batchJobId} started.`);
                    this.stopCheckingBatchJob(batchJobId);
                }

            } catch (error) {
                if (error.name === 'AbortError') {
                    console.warn(`Request for BatchJob ${batchJobId} was aborted.`);
                } else {
                    console.error(`Error checking BatchJob ${batchJobId}:`, error);
                }
            }
        }, randomInterval);

        this.intervals.set(batchJobId, intervalId);

        // 30초 후 자동 중지
        setTimeout(() => {
            this.stopAllChecking();
        }, 30000);
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
        // eslint-disable-next-line no-unused-vars
        this.intervals.forEach((intervalId, batchJobId) => {
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
