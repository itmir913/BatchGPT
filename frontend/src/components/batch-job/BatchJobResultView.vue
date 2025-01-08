<template>
  <div class="container mt-4 infinite-scroll-container">
    <!-- 진행 상태 표시 -->
    <div class="mb-4">
      <ProgressIndicator :batch_id="batch_id" :currentStep="4"/>
    </div>

    <!-- RUNNING 버튼 -->
    <div class="text-center mb-4">
      <button
          :disabled="formStatus.isLoading && formStatus.shouldDisableRunButton"
          class="btn btn-primary"
          @click="handleRun"
      >
        {{ formStatus.isLoading ? "Loading..." : "Start Tasks" }}
      </button>
    </div>

    <!-- CSV 표 형식 테이블 -->
    <div class="table-responsive">
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
            <span
                :class="{
                'badge bg-success': task.task_unit_status === 'Completed',
                'badge bg-warning text-dark': task.task_unit_status === 'PENDING',
                'badge bg-danger': task.task_unit_status === 'FAILED'
              }"
            >
              {{ task.task_unit_status }}
            </span>
          </td>
          <td>{{ parseResponseData(task.request_data) }}</td>
          <td>{{ parseResponseData(task.response_data) }}</td>
        </tr>
        </tbody>
      </table>
    </div>

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
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from "@/components/batch-job/components/ProgressIndicator.vue";
import {
  ERROR_MESSAGES,
  fetchBatchJobConfigsAPI,
  shouldDisableRunButton,
  shouldDisplayResults
} from "@/components/batch-job/utils/batchJobUtils";

const API_BASE_URL = "/api/batch-jobs/";
const API_TASK_UNITS_URL = "/task-units/";

export default {
  props: ["batch_id"],
  components: {ProgressIndicator},
  data() {
    return {
      tasks: [],
      nextPage: null,
      loadingState: {loading: false, loadingSave: false},
      hasMore: true,

      batchJob: null,
      batch_job_status: "CREATED",
    };
  },
  computed: {
    formStatus() {
      return {
        isLoading: this.loadingState.loading,
        hasMore: this.hasMore,
        isReady: !this.loadingState.loading && this.hasMore,
        shouldDisableRunButton: shouldDisableRunButton(this.batch_job_status),
      };
    },
  },
  methods: {
    clearMessages() {
      this.messages = {success: null, error: null};
      this.loadingState.error = null;
      this.loadingState.success = null;
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();

      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.loadingState.error = type === "error" ? fullMessage : null;
      this.loadingState.success = type === "success" ? fullMessage : null;
    },

    async fetchBatchJob() {
      try {
        this.clearMessages();

        const {batchJob, configs} = await fetchBatchJobConfigsAPI(this.batch_id);
        this.batchJob = batchJob;
        this.work_unit = configs.work_unit ?? 1;
        this.prompt = configs.prompt ?? '';
        this.batch_job_status = batchJob.batch_job_status ?? 'CREATED';
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.fetchBatchJob);
      } finally {
        this.loadingState.loading = false;
      }
    },

    async fetchTasks(url = `${API_BASE_URL}${this.batch_id}${API_TASK_UNITS_URL}`) {
      // TODO 함수 분리 대상
      this.loadingState.loading = true;
      try {
        const response = await axios.get(url);
        const data = response.data;

        this.tasks.push(...data.results);
        this.nextPage = data.next;
        this.hasMore = !!data.next;
      } catch (error) {
        console.error("Error fetching tasks:", error);
      } finally {
        this.loadingState.loading = false;
      }
    },
    parseResponseData(responseData) {
      return responseData;
    },
    handleRun() {
      this.tasks = []; // 기존 데이터를 초기화
      this.nextPage = null;
      this.hasMore = true;
      this.fetchTasks();
    },
  },
  async mounted() {
    await this.fetchBatchJob();
    if (shouldDisplayResults(this.batch_job_status))
      await this.fetchTasks();
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}

.infinite-scroll-container {
  padding: 20px;
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
