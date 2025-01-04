<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator v-if="batchJob && !loading && !error" :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="error" class="alert alert-danger text-center" role="alert">
      {{ error }}
    </div>

    <!-- 배치 작업 폼 -->
    <h2 class="mb-4">Modify Batch Job</h2>
    <div class="card">
      <div v-if="batchJob && !loading && !error" class="card-body">
        <!-- Form 시작 -->
        <form @submit.prevent="modifyBatchJob">
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
          <button :disabled="isButtonDisabled" class="btn btn-primary" type="submit">Edit Batch Job</button>
        </form>
      </div>
    </div>

    <!-- 성공 메시지 -->
    <div v-if="successMessage" class="alert alert-success mt-4" role="alert">
      {{ successMessage }}
    </div>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="alert alert-danger mt-4" role="alert">
      {{ errorMessage }}
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
  props: ['batch_id'],
  data() {
    return {
      currentStep: 0, // 현재 진행 중인 단계 (0부터 시작)
      batchJob: {
        title: "", // Title 초기값
        description: "", // Description 초기값
      },
      successMessage: "", // 성공 메시지 상태
      errorMessage: "", // 에러 메시지 상태
      loading: false, // 로딩 상태
      error: null, // 에러 메시지
      isButtonDisabled: true,
    };
  },

  methods: {
    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/`, {withCredentials: true});
        this.batchJob = response.data; // API 응답으로 batchJob 데이터 설정
        this.isButtonDisabled = false
      } catch (error) {
        console.error("Error fetching Batch Job:", error);
        this.isButtonDisabled = true
        this.error = "Failed to load Batch Job details. Please try again later.";
      }
    },

    async modifyBatchJob() {
      try {
        this.isButtonDisabled = true
        const response = await axios.patch(`/api/batch-jobs/${this.batch_id}/`, this.batchJob);

        this.id = response.data.id;
        this.successMessage = "Batch Job modified successfully!";
        this.errorMessage = "";

        setTimeout(() => {
          this.$router.push(`/batch-jobs/${this.id}/`);
        }, 1000);

      } catch (error) {
        console.error("Error modifying Batch Job:", error);
        this.isButtonDisabled = false
        this.successMessage = "";

        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.error || "Failed to modify Batch Job.";
        } else {
          this.errorMessage = "An unexpected error occurred.";
        }
      }
    },
  },

  async created() {
    await this.fetchBatchJob(); // 컴포넌트 생성 시 배치 작업 데이터 가져오기
  }
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>
