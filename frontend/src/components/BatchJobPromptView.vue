<template>
  <div class="container mt-5">

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

    <!-- 5단계 워크플로우 표시 -->
    <ProgressIndicator v-if="batchJob && !loading && !error" :batch_id="batch_id" :currentStep="currentStep"/>

  </div>
</template>


<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';

export default {
  props: ['batch_id'],  // URL 파라미터를 props로 받음
  components: {
    ProgressIndicator, // 등록
  },
  data() {
    return {
      currentStep: 2, // 현재 진행 중인 단계 (0부터 시작)

      batchJob: null, // 배치 작업 데이터
      loading: true, // 로딩 상태
      error: null, // 에러 메시지
    };
  },
  methods: {
    // 배치 작업 데이터 가져오기
    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/`, {
          withCredentials: true,
        });
        this.batchJob = response.data;
        if (this.batchJob.file_name != null) {
          this.isNextButtonDisabled = false;
        }
      } catch (error) {
        console.error("Error fetching Batch Job:", error);
        this.error = "Failed to load Batch Job details. Please try again later.";
      } finally {
        this.loading = false;
      }
    },

  },
  async created() {
    await this.fetchBatchJob();
  },
};
</script>

<style scoped>
.container {
  max-width: 800px;
}
</style>
