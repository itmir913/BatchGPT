<template>
  <div class="container my-4">
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
                  {{ formStatus.isBatchJobLoading ? "Loading..." : "Start Tasks" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 작업 결과 표시 -->
        <LoadingView v-if="formStatus.isTaskLoading"/>
        <div v-else-if="tasks.length > 0" class="table-responsive">
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
              <td>
                <div class="text-content badge bg-white text-dark border border-secondary">
                  {{ truncateText(task.request_data.prompt) }}
                </div>
                <div v-if="task.request_data.has_files">
                  <div class="row g-4 px-3 py-3">
                    <div v-for="(item, idx) in task.request_data.files_data" :key="idx"
                         class="col-md-4 col-sm-6 col-12">
                      <img :src="'data:image/jpeg;base64,' + item" alt="Image Preview" class="img-fluid">
                    </div>
                  </div>
                </div>
              </td>
              <td>
                <div class="text-content">{{ task.response_data }}</div>
              </td>
            </tr>
            </tbody>
          </table>

          <!-- 페이지 버튼 -->
          <div class="d-flex justify-content-center align-items-center mt-4">
            <nav aria-label="Page navigation">
              <ul class="pagination flex-wrap" style="gap: 5px;">
                <li :class="{disabled: currentPage === 1}" class="page-item">
                  <button class="page-link" @click="changePage(1)">&lt;&lt;</button>
                </li>
                <li :class="{disabled: currentPage === 1}" class="page-item">
                  <button class="page-link" @click="changePage(currentPage - 1)">&lt;</button>
                </li>
                <li v-if="currentPage > 3" class="page-item">
                  <span class="page-link">...</span>
                </li>
                <li v-for="page in pageRange" :key="page" :class="{active: currentPage === page}" class="page-item">
                  <button class="page-link" @click="changePage(page)">{{ page }}</button>
                </li>
                <li v-if="currentPage < totalPages - 2" class="page-item">
                  <span class="page-link">...</span>
                </li>
                <li :class="{disabled: currentPage === totalPages}" class="page-item">
                  <button class="page-link" @click="changePage(currentPage + 1)">&gt;</button>
                </li>
                <li :class="{disabled: currentPage === totalPages}" class="page-item">
                  <button class="page-link" @click="changePage(totalPages)">&gt;&gt;</button>
                </li>
              </ul>
            </nav>
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
      currentPage: 1,
      totalPages: 1,

      taskUnits: {
        taskUnitChecker: null,
        inProgressTasks: [],
      },

      loadingState: {fetchBatchJobLoading: false, fetchTaskLoading: false, isStartTask: false},
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
        isBatchJobLoading: this.loadingState.fetchBatchJobLoading,
        isTaskLoading: this.loadingState.fetchTaskLoading,
        isRunnable: shouldDisableRunButton(this.batchJob.batch_job_status) || !this.isStartTask,
      };
    },
    pageRange() {
      const range = [];
      const start = Math.max(this.currentPage - 3, 1);
      const end = Math.min(this.currentPage + 3, this.totalPages);

      for (let i = start; i <= end; i++) {
        range.push(i);
      }

      return range;
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
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJobDetail} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJobDetail} ${error}`);
        }
      } finally {
        this.loadingState.fetchBatchJobLoading = false;
      }
    },

    async fetchTasks() {
      if (this.loadingState.fetchTaskLoading) return;

      try {
        this.loadingState.fetchTaskLoading = true;
        const url = fetchTaskAPIUrl(this.batch_id, this.currentPage);
        const {tasks, nextPage, totalPages, hasMore} = await fetchTasksAPI(url);

        this.tasks = [...tasks];
        this.nextPage = nextPage;
        this.hasMore = hasMore;
        this.totalPages = totalPages;

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
          this.handleMessages("error", `${ERROR_MESSAGES.fetchTasks} ${error}`);
        }
      } finally {
        this.loadingState.fetchTaskLoading = false;
      }
    },

    async changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      await this.fetchTasks(); // 페이지 변경 시 데이터를 로드
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
          this.handleMessages("error", `${ERROR_MESSAGES.pendingTasks} ${error}`);
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

    truncateText(text) {
      const maxLength = 500;
      return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
    },

  },
  async mounted() {
    this.taskUnits.taskUnitChecker = new TaskUnitChecker();

    await this.fetchBatchJob();
    if (shouldDisplayResults(this.batchJob.batch_job_status)) {
      await this.fetchTasks();
    }
  },

  beforeUnmount() {
    this.taskUnits.taskUnitChecker.stopAllChecking();
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
