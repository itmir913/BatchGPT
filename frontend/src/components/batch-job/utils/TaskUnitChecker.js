import {checkTaskUnitStatus} from "@/components/batch-job/utils/BatchJobUtils";
import {completedTaskUnit} from "@/components/batch-job/utils/TaskUnitUtils";

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
        this.isStopped = false;  // Flag to indicate if checking should be stopped
    }

    setOnCompleteCallback(callback) {
        this.onCompleteCallback = callback;
    }

    startCheckingTaskUnits(batchJobId, taskUnitIds) {
        taskUnitIds.forEach(taskUnitId => {
            this.taskQueue.push({batchJobId, taskUnitId, attempts: 0});
        });

        this.isStopped = false; // Reset stop flag
        this.processTasks();

        this.timeoutId = setTimeout(() => {
            this.stopAllChecking();
        }, MAX_CHECK_TIME);
    }

    async processTasks() {
        const taskPromises = [];

        while ((this.taskQueue.length > 0 || taskPromises.length > 0) && !this.isStopped) {
            if (this.inProgress.size < MAX_CONCURRENT_TASKS) {
                const taskUnit = this.taskQueue.shift();
                if (!taskUnit) continue;

                this.inProgress.add(taskUnit.taskUnitId);
                const taskPromise = this.checkTaskUnitStatus(taskUnit.batchJobId, taskUnit.taskUnitId, taskUnit.attempts);
                taskPromises.push({taskUnitId: taskUnit.taskUnitId, promise: taskPromise});
            }

            if (taskPromises.length >= MAX_CONCURRENT_TASKS) {
                const results = await Promise.allSettled(taskPromises.map(p => p.promise));

                results.forEach((result, index) => {
                    const taskUnitId = taskPromises[index].taskUnitId;
                    if (result.status === 'rejected') {
                        console.error(`Task ${taskUnitId} failed:`, result.reason);
                    }
                });

                taskPromises.length = 0;
            }
        }

        if (taskPromises.length > 0) {
            await Promise.all(taskPromises.map(p => p.promise));
        }
    }

    async checkTaskUnitStatus(batchJobId, taskUnitId, attempts) {
        const tryChecking = async () => {
            try {
                if (this.isStopped) return;  // Check if stopped before processing
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

                if (completedTaskUnit(status)) {
                    console.log(`TaskUnit ${taskUnitId} has been ${status}.`);
                    this.stopCheckingTaskUnit(taskUnitId);
                }

            } catch (error) {
                if (this.isStopped) return;  // Check if stopped before processing errors
                if (error.response && error.response.status === 404) {
                    attempts++;
                    await this.delay(DELAY_AFTER_FAILURE);

                    if (attempts < MAX_RETRIES) {
                        this.taskQueue.unshift({batchJobId, taskUnitId, attempts});
                        console.log(`TaskUnit ${taskUnitId} not found. Retrying... Attempt ${attempts}/${MAX_RETRIES}`);
                    } else {
                        this.taskQueue.push({batchJobId, taskUnitId, attempts});
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
            if (!controller.signal.aborted) {
                controller.abort();
                console.log(`TaskUnit ${taskUnitId} stopped.`);
            }
            this.controllers.delete(taskUnitId);
        }
    }

    stopAllChecking() {
        // Prevent further tasks from being processed
        this.isStopped = true;

        // Clear queue and in-progress tasks
        this.taskQueue = [];

        this.inProgress.forEach(taskUnitId => {
            this.stopCheckingTaskUnit(taskUnitId);
        });
        this.inProgress.clear();

        this.controllers.forEach((controller, taskUnitId) => {
            controller.abort();
            console.log(`TaskUnit ${taskUnitId} aborted.`);
        });
        this.controllers.clear();

        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }

        console.log('All task unit checks stopped, including queued tasks.');
    }
}

export default TaskUnitChecker;
