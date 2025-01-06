<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="0" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loadingState.loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>Processing your request...</p>
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
                :class="{ 'is-invalid': !batchJob.title && loadingState.submitted }"
            />
            <div v-if="!batchJob.title && loadingState.submitted" class="invalid-feedback">
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
          <button :disabled="isFormDisabled" class="btn btn-primary" type="submit">
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
  createSuccess: "Batch Job created successfully!",
};

const ERROR_MESSAGES = {
  failedToCreateError: "Failed to create Batch Job. Please try again later.",
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
    isFormDisabled() {
      return !this.batchJob.title || this.loadingState.loading;
    },
  },
  methods: {
    clearMessages() {
      this.messages.success = null;
      this.messages.error = null;
    },

    handleMessages(type, message) {
      this.clearMessages();
      if (type === "error") {
        this.messages.error = message;
      } else if (type === "success") {
        this.messages.success = message;
      }
    },

    async createBatchJob() {
      if (!this.batchJob?.title) return;

      try {
        this.loadingState.submitted = true;
        this.clearMessages();

        const response = await axios.post(API_BASE_URL, this.batchJob);
        this.batch_id = response.data.id;

        this.handleMessages("success", SUCCESS_MESSAGES.createSuccess);
        this.$router.push(`/batch-jobs/${this.batch_id}/`);
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.failedToCreateError);
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
