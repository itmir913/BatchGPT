<template>
  <div class="container mt-4">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 메시지 표시 -->
    <div v-if="success" class="alert alert-success text-center mt-3" role="alert">{{ success }}</div>
    <div v-if="error" class="alert alert-danger text-center mt-3" role="alert">{{ error }}</div>

    <!-- 배치 작업 폼 -->
    <h2 class="mb-3">Modify Batch Job</h2>
    <div v-if="batchJob && isReady" class="card">
      <div class="card-body">
        <form @submit.prevent="modifyBatchJob">
          <!-- 하위 컴포넌트 사용 -->
          <BatchJobInputFields
              :batchJob="batchJob"
              :isTitleInvalid="formStatus.isCreateButtonDisabled"
              @update:batchJob="batchJob = $event"
          />
          <!-- 버튼 -->
          <div class="d-flex justify-content-end mt-3">
            <button class="btn btn-secondary me-2" @click="cancelButton">Cancel</button>
            <button :disabled="isButtonDisabled" class="btn btn-primary" type="submit">Edit Batch Job</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/batch-job/components/ProgressIndicator.vue';
import BatchJobInputFields from "@/components/batch-job/components/BatchJobInputFields.vue";

export default {
  components: {
    BatchJobInputFields,
    ProgressIndicator,
  },
  props: ['batch_id'],
  data() {
    return {
      currentStep: 0, // 현재 진행 중인 단계
      batchJob: {title: "", description: ""}, // 배치 작업 초기값
      success: null, // 성공 메시지 상태
      error: null, // 에러 메시지 상태
      loading: false, // 로딩 상태
      isButtonDisabled: true, // 버튼 비활성화 여부
    };
  },
  computed: {
    isReady() {
      return !this.loading;
    },

    formStatus() {
      return {
        isCreateButtonDisabled: !this.batchJob.title,
      };
    },
  },
  methods: {
    // 배치 작업 데이터를 가져오는 메서드
    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/`, {withCredentials: true});
        this.batchJob = response.data;
        this.isButtonDisabled = false; // 버튼 활성화
      } catch (error) {
        this.handleError("Failed to load Batch Job details. Please try again later.");
      }
    },

    // 배치 작업 수정 처리
    async modifyBatchJob() {
      try {
        this.isButtonDisabled = true;

        const payload = {
          'title': this.batchJob.title,
          'description': this.batchJob.description,
        };

        await axios.patch(`/api/batch-jobs/${this.batch_id}/`, payload);
        this.success = "Batch Job modified successfully!";
        this.error = null;

        // 수정 후 자동으로 배치 작업 상세 페이지로 리다이렉트
        setTimeout(() => {
          this.$router.push(`/batch-jobs/${this.batch_id}/`);
        }, 1000);
      } catch (error) {
        this.isButtonDisabled = false; // 버튼 활성화
        this.handleError(`Error modifying Batch Job: ${error.response?.data?.error || "An unexpected error occurred."}`);
      }
    },

    // 에러 처리 메서드
    handleError(message) {
      this.error = message;
      this.success = null; // 성공 메시지 초기화
    },

    // 취소 버튼 처리
    cancelButton() {
      this.$router.push(`/batch-jobs/${this.batch_id}`);
    },
  },

  // 컴포넌트 마운트 후 배치 작업 데이터 가져오기
  mounted() {
    this.fetchBatchJob();
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>
