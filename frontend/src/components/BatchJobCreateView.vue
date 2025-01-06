<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="0" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <!-- Success/Failure Message -->
    <div v-if="messages.success && !messages.error" class="alert alert-success text-center mt-4" role="alert">
      {{ messages.success }}
    </div>
    <div v-if="messages.error" class="alert alert-danger text-center mt-4" role="alert">
      {{ messages.error }}
    </div>

    <!-- 배치 작업 폼 -->
    <h2 class="mb-4">Create a New Batch Job</h2>
    <div class="card">
      <div class="card-body">
        <!-- Form 시작 -->
        <form @submit.prevent="createBatchJob">
          <!-- Title 입력 -->
          <div class="mb-3">
            <label class="form-label" for="title">Title</label>
            <input
                id="title"
                v-model="batchJob.title"
                class="form-control"
                placeholder="Enter the title of the batch job"
                required
                type="text"
                :class="{ 'is-invalid': formStatus.isCreateButtonDisabled }"
            />
            <div v-if="formStatus.isCreateButtonDisabled" class="invalid-feedback">
              Title is required.
            </div>
          </div>

          <!-- Description 입력 -->
          <div class="mb-3">
            <label class="form-label" for="description">Description</label>
            <textarea
                id="description"
                v-model="batchJob.description"
                class="form-control"
                placeholder="Enter a description (optional)"
                rows="4"
            ></textarea>
          </div>

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
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';

const API_BASE_URL = '/api/batch-jobs/create/';

const SUCCESS_MESSAGES = {
  createBatchJob: "Batch Job created successfully!",
};

const ERROR_MESSAGES = {
  createBatchJob: "Failed to create Batch Job. Please try again later.",
};

export default {
  components: {ProgressIndicator},
  data() {
    return {
      currentStep: 0,
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
      if (this.formStatus.isFormDisabled) return;

      try {
        this.clearMessages();
        this.loadingState.submitted = true;

        const response = await axios.post(API_BASE_URL, this.batchJob);
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
