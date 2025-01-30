import {checkTaskUnitStatus} from "@/components/batch-job/utils/BatchJobUtils";

const MAX_CONCURRENT_TASKS = 5;  // 동시에 서버로 요청할 Task 상태 조회 개수
const MAX_RETRIES = 10;  // 10번의 시도 후 큐의 맨 뒤로 들어감
const MAX_CHECK_TIME = 5 * 60 * 1000; // 5분 뒤 모든 상태 조회 요청 중지
const RANDOM_DELAY_RANGE = {min: 150, max: 1000}; // 동시 요청 작업 간의 랜덤 딜레이
const DELAY_AFTER_FAILURE = 1000;  // 상태 조회 실패(404) 후 다음 시도까지 딜레이

class TaskUnitChecker {
    constructor() {
        this.controllers = new Map();
        this.onCompleteCallback = null;
        this.taskQueue = [];
        this.inProgress = new Set();
        this.timeoutId = null;
    }

    setOnCompleteCallback(callback) {
        this.onCompleteCallback = callback;
    }

    startCheckingTaskUnits(batchJobId, taskUnitIds) {
        taskUnitIds.forEach(taskUnitId => {
            this.taskQueue.push({batchJobId, taskUnitId, attempts: 1});
        });

        this.processTasks();

        this.timeoutId = setTimeout(() => {
            this.stopAllChecking();
        }, MAX_CHECK_TIME);
    }

    async processTasks() {
        while (this.taskQueue.length > 0) {
            if (this.inProgress.size < MAX_CONCURRENT_TASKS) {
                const taskUnit = this.taskQueue.shift();
                this.inProgress.add(taskUnit.taskUnitId);
                await this.checkTaskUnitStatus(taskUnit.batchJobId, taskUnit.taskUnitId, taskUnit.attempts);
            }
        }
    }

    async checkTaskUnitStatus(batchJobId, taskUnitId, attempts) {
        const tryChecking = async () => {
            try {
                const randomDelay = Math.floor(Math.random() * (RANDOM_DELAY_RANGE.max - RANDOM_DELAY_RANGE.min + 1)) + RANDOM_DELAY_RANGE.min;
                await this.delay(randomDelay);

                const controller = new AbortController();
                this.controllers.set(taskUnitId, controller);

                const response = await checkTaskUnitStatus(batchJobId, taskUnitId, {signal: controller.signal});
                const status = response.data.status;
                const result = response.data.response_data ?? "";

                if (this.onCompleteCallback) {
                    this.onCompleteCallback(taskUnitId, status, result);
                }

                if (status === 'Completed') {
                    console.log(`TaskUnit ${taskUnitId} has been completed.`);
                    this.stopCheckingTaskUnit(taskUnitId);
                }

            } catch (error) {
                if (error.response && error.response.status === 404) {
                    attempts++;
                    await this.delay(DELAY_AFTER_FAILURE);

                    if (attempts < MAX_RETRIES) {
                        this.taskQueue.unshift({batchJobId, taskUnitId, attempts}); // 큐의 맨 앞에 추가
                        console.log(`TaskUnit ${taskUnitId} not found. Retrying... Attempt ${attempts}/${MAX_RETRIES}`);
                    } else {
                        this.taskQueue.push({batchJobId, taskUnitId, attempts}); // 큐의 맨 뒤에 추가
                        console.log(`TaskUnit ${taskUnitId} failed after ${MAX_RETRIES} retries.`);
                    }
                } else {
                    console.error(`Error checking TaskUnit ${taskUnitId}:`, error);
                }
            } finally {
                this.controllers.delete(taskUnitId);
                this.inProgress.delete(taskUnitId);
            }
        }

        await tryChecking();
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    stopCheckingTaskUnit(taskUnitId) {
        if (this.controllers.has(taskUnitId)) {
            const controller = this.controllers.get(taskUnitId);
            controller.abort();
            this.controllers.delete(taskUnitId);
            console.log(`TaskUnit ${taskUnitId} stopped.`);
        }
    }

    stopAllChecking() {
        // 큐에 있는 대기 중인 작업들 모두 취소
        this.taskQueue = [];

        // 진행 중인 작업들 취소
        this.controllers.forEach((controller, taskUnitId) => {
            controller.abort();
            console.log(`TaskUnit ${taskUnitId} aborted.`);
        });

        // 진행 중인 작업 목록과 대기 목록 초기화
        this.controllers.clear();
        this.inProgress.clear();

        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            console.log('Timeout cleared.');
        }

        console.log('All task unit checks stopped, including queued tasks.');
    }
}

export default TaskUnitChecker;
