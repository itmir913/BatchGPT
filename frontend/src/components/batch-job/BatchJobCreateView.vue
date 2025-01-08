<template>
  <div class="container mt-4">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="0"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <!-- Success/Failure Message -->
    <div v-if="messages.success && !messages.error" class="alert alert-success text-center mt-3" role="alert">
      {{ messages.success }}
    </div>
    <div v-if="messages.error" class="alert alert-danger text-center mt-3" role="alert">
      {{ messages.error }}
    </div>

    <!-- 배치 작업 폼 -->
    <h2 class="mb-3">Create a New Batch Job</h2>
    <div class="card">
      <div class="card-body">
        <!-- Form 시작 -->
        <form @submit.prevent="createBatchJob">
          <!-- 하위 컴포넌트 사용 -->
          <BatchJobInputFields
              :batchJob="batchJob"
              :isTitleInvalid="formStatus.isCreateButtonDisabled"
              @update:batchJob="batchJob = $event"
          />
          <!-- Submit 버튼 -->
          <button :disabled="formStatus.isFormDisabled" class="btn btn-primary" type="submit">
            Create Batch Job
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/batch-job/components/ProgressIndicator.vue';
import BatchJobInputFields from '@/components/batch-job/components/BatchJobInputFields.vue';

const API_BASE_URL = '/api/batch-jobs/create/';

const SUCCESS_MESSAGES = {
  createBatchJob: "Batch Job created successfully!",
};

const ERROR_MESSAGES = {
  createBatchJob: "Failed to create Batch Job. Please try again later.",
};

export default {
  components: {ProgressIndicator, BatchJobInputFields},
  data() {
    return {
      batch_id: 0,
      batchJob: {title: "", description: ""},
      loadingState: {loading: false, submitted: false},
      messages: {success: null, error: null},
    };
  },
  computed: {
    formStatus() {
      return {
        isFormDisabled: !this.batchJob.title || this.loadingState.loading,
        isCreateButtonDisabled: !this.batchJob.title && this.loadingState.submitted,
        isLoading: this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
      };
    },
  },
  methods: {
    clearMessages() {
      this.messages.success = null;
      this.messages.error = null;
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();

      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.loadingState.error = type === "error" ? fullMessage : null;
      this.loadingState.success = type === "success" ? fullMessage : null;
    },

    async createBatchJob() {
      // TODO 함수 분리 대상
      if (this.formStatus.isFormDisabled) return;

      try {
        this.clearMessages();
        this.loadingState.submitted = true;

        const payload = {
          'title': this.batchJob.title,
          'description': this.batchJob.description,
        };

        const response = await axios.post(API_BASE_URL, payload);
        this.batch_id = response.data.id;

        this.handleMessages("success", SUCCESS_MESSAGES.createBatchJob);
        this.$router.push(`/batch-jobs/${this.batch_id}/`);
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.createBatchJob);
      } finally {
        this.loadingState.submitted = false;
      }
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>