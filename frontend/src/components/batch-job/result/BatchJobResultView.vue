<template>
  <div class="container my-4 infinite-scroll-container">
    <ToastView
        ref="toast"
        :message="messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator :batch_id="batch_id" :currentStep="4"/>
      </div>

      <div class="col-md-9">
        <!-- 정보 카드 -->
        <h2 class="mb-3">Summary</h2>
        <div class="card mb-4 rounded-4">
          <div class="card-body p-4">
            <!-- 반응형 테이블 레이아웃 -->
            <div class="row">
              <!-- General Information 테이블 -->
              <BatchJobInformationTableView :batchJob="batchJob"/>

              <!-- Configuration 테이블 -->
              <DynamicTableView :configs="batchJob.configs"/>
            </div>
          </div>
        </div>

        <div class="card mb-4 rounded-4">
          <div class="card-body p-4">
            <!-- RUNNING 버튼 -->
            <div class="text-center">
              <button :disabled="formStatus.isLoading || formStatus.isStartTask ||!formStatus.isRunnable"
                      class="btn btn-primary"
                      @click="handleRun">
                {{ formStatus.isLoading ? "Loading..." : "Start Tasks" }}
              </button>
            </div>
          </div>
        </div>

        <!-- CSV 표 형식 테이블 -->
        <div v-if="tasks.length > 0" class="table-responsive scroll-container">
          <h2 class="mb-3">Results</h2>
          <table class="table table-striped table-hover align-middle custom-table">
            <thead class="table-dark">
            <tr>
              <th scope="col" style="width: 10%;">Status</th>
              <th scope="col" style="width: 45%;">Request</th>
              <th scope="col" style="width: 45%;">Response</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="task in tasks" :key="task.task_unit_id">
              <td>
              <span :class="{
                'badge bg-warning text-dark': task.task_unit_status === 'Pending',
                'badge bg-info': task.task_unit_status === 'In Progress',
                'badge bg-danger': task.task_unit_status === 'Failed',
                'badge bg-success': task.task_unit_status === 'Completed',
              }">
                {{ task.task_unit_status }}
              </span>
              </td>
              <td>{{ parseResponseData(task.request_data) }}</td>
              <td>{{ parseResponseData(task.response_data) }}</td>
            </tr>
            </tbody>
          </table>

          <div>
            <!-- 로딩 상태 표시 -->
            <div v-if="formStatus.isLoading" class="text-center my-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <!-- 더 이상 데이터가 없을 때 -->
            <div v-if="!formStatus.hasMore && !formStatus.isLoading" class="text-center my-4">
              <p class="text-muted">No more data</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from "@/components/batch-job/common/ProgressIndicator.vue";
import {
  ERROR_MESSAGES,
  fetchBatchJobConfigsAPI,
  fetchTaskAPIUrl,
  fetchTasksAPI,
  runBatchJobProcess,
  shouldDisableRunButton,
  shouldDisplayResults,
  SUCCESS_MESSAGES
} from "@/components/batch-job/utils/BatchJobUtils";
import {DEFAULT_GPT_MODEL} from "@/components/batch-job/utils/GPTUtils";
import BatchJobChecker from "@/components/batch-job/utils/BatchJobChecker";
import TaskUnitChecker from "@/components/batch-job/utils/TaskUnitChecker";
import ToastView from "@/components/batch-job/common/ToastView.vue";
import BatchJobInformationTableView from "@/components/batch-job/result/InfoTable.vue";
import DynamicTableView from "@/components/batch-job/result/ConfigTable.vue";
import LoadingView from "@/components/batch-job/common/LoadingView.vue";

export default {
  props: ["batch_id"],
  components: {LoadingView, DynamicTableView, BatchJobInformationTableView, ToastView, ProgressIndicator},
  data() {
    return {
      tasks: [],
      nextPage: null,
      hasMore: true,

      taskUnits: {
        taskUnitChecker: null,
        inProgressTasks: [],
      },

      loadingState: {loading: false, loadingSave: false, isStartTask: false},
      messages: {success: null, error: null},

      batchJob: {
        title: "title",
        description: "description.",
        file_name: "example_file.csv",
        total_size: "0",
        batch_job_status: "Created", // Possible values: 'Completed', 'In Progress', 'Failed'
        configs: {
          prompt: "Generate summary",
          gpt_model: DEFAULT_GPT_MODEL,
        }
      },
      batchJobChecker: new BatchJobChecker(),
    };
  },
  computed: {
    formStatus() {
      return {
        isLoading: this.loadingState.loading,
        hasMore: this.hasMore,
        isReady: !this.loadingState.loading && this.hasMore,
        isRunnable: shouldDisableRunButton(this.batchJob.batch_job_status),
      };
    },
  },
  methods: {
    clearMessages() {
      this.messages.error = null;
      this.messages.success = null;
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();

      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.messages.error = type === "error" ? fullMessage : null;
      this.messages.success = type === "success" ? fullMessage : null;
    },

    async fetchBatchJob() {
      try {
        this.loadingState.loading = true;
        this.clearMessages();

        const {batchJob, configs} = await fetchBatchJobConfigsAPI(this.batch_id);
        this.batchJob = batchJob;
        this.work_unit = configs.work_unit ?? 1;
        this.prompt = configs.prompt ?? '';
        this.batchJob.batch_job_status = batchJob.batch_job_status ?? 'Created';
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJob} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJob} No response received.`);
        }
      } finally {
        this.loadingState.loading = false;
      }
    },

    async fetchTasks() {
      if (!this.hasMore) return;

      this.loadingState.loading = true;

      try {
        const {tasks, nextPage, hasMore} = await fetchTasksAPI(this.nextPage ?? fetchTaskAPIUrl(this.batch_id));

        this.tasks.push(...tasks);
        this.nextPage = nextPage;
        this.hasMore = hasMore;

        this.taskUnits.inProgressTasks = tasks.filter(task =>
            ['Pending', 'In Progress'].includes(task.task_unit_status)
        ).map(task => task.task_unit_id);

        if (this.taskUnits.inProgressTasks?.length > 0) {
          this.taskUnits.taskUnitChecker.startCheckingTaskUnits(this.batch_id, this.taskUnits.inProgressTasks);
          this.taskUnits.taskUnitChecker.setOnCompleteCallback((taskId, status, result) => {
            const previewItem = this.tasks.find(item => item.task_unit_id === taskId);
            if (previewItem) {
              previewItem.response_data = result;
              previewItem.task_unit_status = status;
            } else {
              console.error(`Task ID ${taskId} not found in taskUnits.taskUnitChecker`);
            }
          });
        }

      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchTasks} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchTasks} No response received.`);
        }
      } finally {
        this.loadingState.loading = false;
      }
    },
    parseResponseData(responseData) {
      return responseData;
    },
    async handleRun() {
      if (this.loadingState.isStartTask) return;
      this.loadingState.isStartTask = true;

      this.tasks = []; // 기존 데이터를 초기화
      this.nextPage = null;
      this.hasMore = true;

      this.taskUnits.taskUnitChecker.stopAllChecking()

      try {
        this.batchJob = await runBatchJobProcess(this.batch_id);
        this.handleMessages("success", SUCCESS_MESSAGES.pendingTasks)

        this.batchJobChecker.setOnCompleteCallback(this.handleBatchJobStatus);
        this.batchJobChecker.startCheckingBatchJob(this.batch_id);

      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.pendingTasks} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.pendingTasks} No response received.`);
        }
      }
    },
    async handleBatchJobStatus(batchJobId, status, result) {
      this.batchJob.batch_job_status = status;

      if (status !== 'Pending') {
        console.log('Batch job started successfully.', result);
        this.handleMessages("success", SUCCESS_MESSAGES.runTasks)
        this.loadingState.isStartTask = false;
        await this.fetchTasks();
      } else if (status === 'Failed') {
        console.log('Batch job failed.');
      }
    },
    async onScroll() {
      const bottom = this.$el.getBoundingClientRect().bottom;
      const windowHeight = window.innerHeight;

      // 스크롤이 끝에 가까워지면 데이터를 가져옵니다.
      if (bottom <= windowHeight
          && this.tasks?.length > 0 && this.hasMore
          && !this.loadingState.loading) {
        await this.fetchTasks();
      }
    },
  },
  async mounted() {
    this.taskUnits.taskUnitChecker = new TaskUnitChecker();
    window.addEventListener('scroll', this.onScroll);

    await this.fetchBatchJob();
    if (shouldDisplayResults(this.batchJob.batch_job_status)) {
      await this.fetchTasks();
    }
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.onScroll);
  }
};
</script>

<style>
.scroll-container {
  overflow-x: auto;
  white-space: pre-wrap;
}
</style>

<style scoped>
.infinite-scroll-container {
  overflow-y: auto;
}

.table-responsive {
  margin-top: 20px;
}

.custom-table td,
.custom-table th {
  border-right: 1px solid #dee2e6;
}

.custom-table th:last-child,
.custom-table td:last-child {
  border-right: none;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.text-muted {
  font-size: 1.2rem;
}
</style>
