<template>
  <div class="container mt-5">
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
          <button class="btn btn-primary" type="submit">Create Batch Job</button>
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
import axios from "@/configs/axios"; // Axios 설정 파일 가져오기

export default {
  data() {
    return {
      batchJob: {
        title: "", // Title 초기값
        description: "", // Description 초기값
      },
      id: 0,
      successMessage: "", // 성공 메시지 상태
      errorMessage: "", // 에러 메시지 상태
    };
  },
  methods: {
    async createBatchJob() {
      try {
        // API 요청 보내기
        const response = await axios.post('/api/batch-jobs/create/', this.batchJob);

        // 성공 시 메시지 표시 및 폼 초기화
        this.id = response.data.id
        this.successMessage = "Batch Job created successfully!";
        this.errorMessage = "";
        this.batchJob.title = "";
        this.batchJob.description = "";

        setTimeout(() => {
          this.$router.push(`/batch-jobs/${this.id}/`);
        }, 1000);

      } catch (error) {
        // 에러 처리
        console.error("Error creating Batch Job:", error);
        this.successMessage = "";
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.error || "Failed to create Batch Job.";
        } else {
          this.errorMessage = "An unexpected error occurred.";
        }
      }
    },
  },
};
</script>

<style scoped>
/* 부트스트랩 스타일은 이미 포함되어 있다고 가정 */
.container {
  max-width: 600px;
}
</style>
