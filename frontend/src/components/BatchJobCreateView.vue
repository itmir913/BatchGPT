<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loadingState.loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>Processing your request...</p>
    </div>

    <!-- 메시지 -->
    <div v-show="messages.success" class="alert alert-success text-center mt-4" role="alert">
      {{ messages.success }}
    </div>
    <div v-show="messages.error" class="alert alert-danger text-center mt-4" role="alert">
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
                :class="{ 'is-invalid': !batchJob.title && submitted }"
            />
            <div v-if="!batchJob.title && submitted" class="invalid-feedback">
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

const API_URL = '/api/batch-jobs/create/';
const SUCCESS_MSG = "Batch Job created successfully!";
const ERROR_MSG = "Failed to create Batch Job.";

export default {
  components: {ProgressIndicator},
  data() {
    return {
      currentStep: 0,  // 진행 단계 (필요시 동적으로 변경)
      id: 0,
      batchJob: {title: "", description: ""},
      loadingState: {loading: false, success: null, error: null},
      messages: {success: null, error: null},
      submitted: false,  // 폼 제출 상태
    };
  },
  computed: {
    isFormDisabled() {
      return !this.batchJob.title || this.loadingState.loading;
    },
  },
  methods: {
    async createBatchJob() {
      this.submitted = true;  // 폼 제출 상태로 설정

      if (!this.batchJob.title) return;  // 제목이 없으면 리턴

      this.loadingState.loading = true;
      this.clearMessages();  // 메시지 초기화

      try {
        const response = await axios.post(API_URL, this.batchJob);
        this.id = response.data.id;
        this.handleMessages("success", SUCCESS_MSG);
        this.$router.push(`/batch-jobs/${this.id}/`);
      } catch (error) {
        this.handleMessages("error", ERROR_MSG);
      } finally {
        this.loadingState.loading = false;
        this.submitted = false;  // 폼 제출 후 초기화
      }
    },

    clearMessages() {
      this.messages = {success: null, error: null};
      this.loadingState.error = null;
      this.loadingState.success = null;
    },

    handleMessages(type, message, details = "") {
      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.loadingState.error = type === "error" ? fullMessage : null;
      this.loadingState.success = type === "success" ? fullMessage : null;
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>
