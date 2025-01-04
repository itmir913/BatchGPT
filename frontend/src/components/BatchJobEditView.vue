<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator v-if="batchJob && !loading && !error" :batch_id="id" :currentStep="currentStep"/>

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
      <div class="card-body">
        <BatchJobForm
            :batchJob="batchJob"
            @submit="modifyBatchJob"
        />
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
import BatchJobForm from '@/components/BatchJobForm.vue'; // BatchJobForm 컴포넌트 임포트

export default {
  props: ['batch_id'],
  components: {
    ProgressIndicator,
    BatchJobForm, // 등록
  },
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
    };
  },
  methods: {
    async modifyBatchJob(batchData) { // batchData를 인자로 받음
      try {
        const response = await axios.patch(`/api/batch-jobs/${this.batch_id}/`, batchData);

        this.id = response.data.id;
        this.successMessage = "Batch Job modified successfully!";
        this.errorMessage = "";

        setTimeout(() => {
          this.$router.push(`/batch-jobs/${this.batch_id}/`);
        }, 500);

        // 폼 초기화
        this.batchJob.title = "";
        this.batchJob.description = "";

      } catch (error) {
        console.error("Error modifying Batch Job:", error);
        this.successMessage = "";

        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.error || "Failed to modify Batch Job.";
        } else {
          this.errorMessage = "An unexpected error occurred.";
        }
      }
    },
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
}
</style>
