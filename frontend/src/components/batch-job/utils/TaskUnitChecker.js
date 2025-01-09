import {checkTaskUnitStatus} from "@/components/batch-job/utils/BatchJobUtils";

class TaskUnitChecker {

    constructor() {
        this.intervals = new Map(); // task_unit_id별 interval ID 저장
        this.controllers = new Map(); // task_unit_id별 AbortController 저장
        this.onCompleteCallback = null;
    }

    setOnCompleteCallback(callback) {
        this.onCompleteCallback = callback;
    }

    startCheckingTaskUnits(batchJobId, taskUnitIds) {
        taskUnitIds.forEach(taskUnitId => {
            const controller = new AbortController();
            this.controllers.set(taskUnitId, controller);

            const randomInterval = Math.floor(Math.random() * 9000) + 1000; // 1초에서 10초 사이
            const intervalId = setInterval(async () => {
                try {
                    const response = await checkTaskUnitStatus(batchJobId, taskUnitId);
                    const status = response.data.status;
                    const result = response.data.response_data ?? "";

                    if (this.onCompleteCallback) {
                        this.onCompleteCallback(taskUnitId, status, result);
                    }

                    // COMPLETED 상태일 경우 interval 중지
                    if (status === 'Completed') {
                        console.log(`TaskUnit ${taskUnitId} completed.`);
                        this.stopCheckingTaskUnit(taskUnitId);
                    }

                } catch (error) {
                    // if (error.name === 'AbortError') {
                    //     console.warn(`Request for TaskUnit ${taskUnitId} was aborted.`);
                    // } else {
                    //     console.error(`Error checking TaskUnit ${taskUnitId}:`, error);
                    // }
                }
            }, randomInterval);

            this.intervals.set(taskUnitId, intervalId);
        });

        // 30초 후 모든 요청 자동 중지
        setTimeout(() => {
            this.stopAllChecking();
        }, 5 * 60 * 1000);
    }

    stopCheckingTaskUnit(taskUnitId) {
        if (this.intervals.has(taskUnitId)) {
            clearInterval(this.intervals.get(taskUnitId));
            this.intervals.delete(taskUnitId);
        }
        if (this.controllers.has(taskUnitId)) {
            this.controllers.get(taskUnitId).abort();
            this.controllers.delete(taskUnitId);
        }
    }

    stopAllChecking() {
        // eslint-disable-next-line no-unused-vars
        this.intervals.forEach((intervalId, taskUnitId) => {
            clearInterval(intervalId);
        });
        this.intervals.clear();

        this.controllers.forEach(controller => {
            controller.abort();
        });
        this.controllers.clear();

        console.log('All task unit checks stopped.');
    }
}

export default TaskUnitChecker;