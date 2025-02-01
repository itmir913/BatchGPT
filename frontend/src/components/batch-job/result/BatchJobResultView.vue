<template>
  <div class="container my-4">
    <ToastView
        ref="toast"
        :message="messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator :batch_id="batch_id" :batch_status="batchJobStatus.Status" :currentStep="4"/>
      </div>
      <div class="col-md-9">
        <!-- 정보 카드 -->
        <h2 class="mb-3">Summary</h2>
        <LoadingView v-if="formStatus.isBatchJobLoading"/>
        <div v-else>
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
                <button :disabled="formStatus.isRunnable"
                        class="btn btn-primary"
                        @click="handleRun">
                  {{ formStatus.isTaskLoading ? "Loading..." : "Start Tasks" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 작업 결과 표시 -->
        <LoadingView v-if="formStatus.isTaskLoading"/>
        <ResultTable v-else-if="tasks.length > 0"
                     :currentPage="currentPage"
                     :tasks="tasks"
                     :totalPages="totalPages"
                     @change-page="changePage"/>

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
import LoadingView from "@/components/batch-job/common/LoadingSpinner.vue";
import {getErrorMessage} from "@/components/batch-job/utils/CommonFunctions";
import ResultTable from "@/components/batch-job/result/ResultTable.vue";

export default {
  props: ["batch_id"],
  components: {ResultTable, LoadingView, DynamicTableView, BatchJobInformationTableView, ToastView, ProgressIndicator},
  data() {
    return {
      tasks: [],
      nextPage: null,
      hasMore: true,

      currentPage: 1,
      totalPages: 1,

      taskUnitChecker: null,

      messages: {success: null, error: null},
      loadingState: {fetchBatchJobLoading: false, fetchTaskLoading: false, isStartTask: false},

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
        isBatchJobLoading: this.loadingState.fetchBatchJobLoading,
        isTaskLoading: this.loadingState.fetchTaskLoading,
        isRunnable: !shouldDisableRunButton(this.batchJob.batch_job_status) || this.loadingState.isStartTask,
      };
    },

    batchJobStatus() {
      return {
        Status: this.batchJob ? this.batchJob?.batch_job_status : null,
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
        this.loadingState.fetchBatchJobLoading = true;
        this.clearMessages();

        const {batchJob} = await fetchBatchJobConfigsAPI(this.batch_id);
        this.batchJob = batchJob;
        this.batchJob.batch_job_status = batchJob.batch_job_status ?? 'Created';
      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.fetchBatchJobDetail}`);
        this.handleMessages("error", errorMessage);
      } finally {
        this.loadingState.fetchBatchJobLoading = false;
      }
    },

    async fetchTasks() {
      if (this.loadingState.fetchTaskLoading) {
        return;
      }

      try {
        this.loadingState.fetchTaskLoading = true;

        const url = fetchTaskAPIUrl(this.batch_id, this.currentPage);
        const {tasks, nextPage, totalPages, hasMore} = await fetchTasksAPI(url);

        this.tasks = [...tasks];
        this.nextPage = nextPage;
        this.hasMore = hasMore;
        this.totalPages = totalPages;

        const inProgressTasks = tasks.filter(task =>
            ['Pending', 'In Progress'].includes(task.task_unit_status)
        ).map(task => task.task_unit_id);

        if (inProgressTasks?.length > 0) {
          if (this.taskUnitChecker) {
            this.taskUnitChecker.stopAllChecking();
          }

          this.taskUnitChecker = new TaskUnitChecker();
          this.taskUnitChecker.setOnCompleteCallback(this.handleTaskComplete);
          this.taskUnitChecker.startCheckingTaskUnits(this.batch_id, inProgressTasks);
        }

      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.fetchTasks}`);
        this.handleMessages("error", errorMessage);
      } finally {
        this.loadingState.fetchTaskLoading = false;
      }
    },

    async changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      if (this.currentPage === page) return;
      this.currentPage = page;
      if (this.taskUnitChecker) {
        this.taskUnitChecker.stopAllChecking();
        this.taskUnitChecker = null;
      }
      await this.fetchTasks(); // 페이지 변경 시 데이터를 로드
    },

    async handleRun() {
      if (this.loadingState.isStartTask) return;
      this.loadingState.isStartTask = true;

      if (this.taskUnitChecker) {
        this.taskUnitChecker.stopAllChecking();
        this.taskUnitChecker = null;
      }

      this.tasks = []; // 기존 데이터를 초기화
      this.nextPage = null;
      this.hasMore = true;

      try {
        this.batchJob = await runBatchJobProcess(this.batch_id);
        this.handleMessages("success", SUCCESS_MESSAGES.pendingTasks)

        this.batchJobChecker.setOnCompleteCallback(this.handleBatchJobStatus);
        this.batchJobChecker.startCheckingBatchJob(this.batch_id);

      } catch (error) {
        this.loadingState.isStartTask = false;
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.pendingTasks}`);
        this.handleMessages("error", errorMessage);
      }
    },

    async handleBatchJobStatus(batchJobId, status, result) {
      this.batchJob.batch_job_status = status;

      if (status !== 'Pending') {
        console.log('Batch job started successfully.', result);
        this.handleMessages("success", SUCCESS_MESSAGES.runTasks)
        await this.fetchTasks();
      } else if (status === 'Failed') {
        console.log('Batch job failed.');
      }
    },

    handleTaskComplete(taskId, status, result) {
      const previewItem = this.tasks.find(item => item.task_unit_id === taskId);
      if (previewItem) {
        previewItem.response_data = result;
        previewItem.task_unit_status = status;
      } else {
        console.error(`Task ID ${taskId} not found in taskUnits.taskUnitChecker`);
      }
    }

  },

  async mounted() {
    await this.fetchBatchJob();
    if (shouldDisplayResults(this.batchJob.batch_job_status)) {
      await this.fetchTasks();
    }
  },

  beforeUnmount() {
    if (this.taskUnitChecker) {
      this.taskUnitChecker.stopAllChecking();
      this.taskUnitChecker = null;
    }
  }
};
</script>

<style scoped>
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
</style>

<style scoped>
.table td {
  padding: 0.5rem;
  vertical-align: top;
}

.text-content {
  text-align: justify;
  word-wrap: break-word;
  white-space: normal;
}

img {
  max-width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}
</style>
