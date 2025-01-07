import axios from "@/configs/axios";

const API_BASE_URL_BATCH_JOBS = "/api/batch-jobs/";
const API_BASE_URL_TASK_UNITS = "/task-units/";

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

            // 1초마다 상태 확인
            const intervalId = setInterval(async () => {
                try {
                    const response = await this.checkTaskUnitStatus(batchJobId, taskUnitId, controller.signal);
                    const status = response.data.status;
                    const result = response.data.response_data ?? "";

                    if (this.onCompleteCallback) {
                        this.onCompleteCallback(taskUnitId, status, result);
                    }

                    // COMPLETED 상태일 경우 interval 중지
                    if (status === 'COMPLETED') {
                        console.log(`TaskUnit ${taskUnitId} completed.`);
                        this.stopCheckingTaskUnit(taskUnitId);
                    }
                } catch (error) {
                    if (error.name === 'AbortError') {
                        console.warn(`Request for TaskUnit ${taskUnitId} was aborted.`);
                    } else {
                        console.error(`Error checking TaskUnit ${taskUnitId}:`, error);
                    }
                }
            }, 1000);

            this.intervals.set(taskUnitId, intervalId);
        });

        // 30초 후 모든 요청 자동 중지
        setTimeout(() => {
            this.stopAllChecking();
        }, 30000);
    }

    async checkTaskUnitStatus(batchJobId, taskUnitId, signal) {
        return await axios.get(`${API_BASE_URL_BATCH_JOBS}${batchJobId}${API_BASE_URL_TASK_UNITS}${taskUnitId}/`, {signal});
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