<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="null" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 메시지 -->
    <div v-if="success" class="alert alert-success text-center mt-4" role="alert">{{ success }}</div>
    <div v-if="error" class="alert alert-danger text-center mt-4" role="alert">{{ error }}</div>

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
            />
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
          <button :disabled="isButtonDisabled || !batchJob.title" class="btn btn-primary" type="submit">
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

export default {
  components: {
    ProgressIndicator,
  },
  data() {
    return {
      currentStep: 0, // 현재 진행 중인 단계 (0부터 시작)
      batchJob: {
        title: "", // Title 초기값
        description: "", // Description 초기값
      },
      id: 0,
      success: null, // 성공 메시지 상태
      error: null, // 에러 메시지 상태
      loading: false, // 로딩 상태
      isButtonDisabled: false,
    };
  },
  computed: {
    isReady() {
      return !this.loading;
    },
  },
  methods: {
    async createBatchJob() {
      this.isButtonDisabled = true;
      this.loading = true;
      this.clearMessages();  // 메시지 초기화

      try {
        const response = await axios.post('/api/batch-jobs/create/', this.batchJob);
        this.id = response.data.id;
        this.success = "Batch Job created successfully!";
        this.error = null;

        // 리디렉션을 직접 처리
        this.$router.push(`/batch-jobs/${this.id}/`);
      } catch (error) {
        this.error = this.getErrorMessage(error);
        this.success = null;
      } finally {
        this.isButtonDisabled = false;
        this.loading = false;
      }
    },

    // 오류 메시지를 처리하는 함수
    getErrorMessage(error) {
      if (error.response && error.response.data) {
        return error.response.data.error || "Failed to create Batch Job.";
      }
      return "An unexpected error occurred.";
    },

    // 메시지 초기화 함수
    clearMessages() {
      this.success = null;
      this.error = null;
    },
  }
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>
