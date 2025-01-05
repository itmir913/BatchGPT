<template>
  <div class="container mt-5">

    <!-- 진행 상태 표시 -->
    <ProgressIndicator v-if="batchJob && isReady" :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loading || isPreviewRunning" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 메시지 영역 -->
    <div v-if="success && !error" class="alert alert-success text-center mt-4" role="alert">{{ success }}</div>
    <div v-if="error" class="alert alert-danger text-center mt-4" role="alert">{{ error }}</div>

    <!-- 프롬프트 입력란 -->
    <div v-if="isReady" class="mb-4">
      <h5>Input Prompt</h5>
      <textarea
          v-model="prompt"
          class="form-control"
          placeholder="Enter your prompt..."
          rows="5"
      ></textarea>
    </div>

    <!-- 작업 단위 설정 -->
    <div v-if="batchJob && isReady">
      <h5 class="text-center mt-4 mb-2">Select Number of Items per Task</h5>
      <div class="d-flex justify-content-center align-items-center mb-2">
        <!-- 라디오 버튼들 -->
        <div v-for="unit in [1, 2, 4, 8]" :key="unit" class="form-check me-3">
          <input
              :id="'workUnit' + unit"
              v-model.number="workUnit"
              :value="unit"
              class="form-check-input"
              disabled
              type="radio"
          />
          <label :for="'workUnit' + unit" class="form-check-label">{{ unit }}</label>
        </div>

        <!-- 사용자 입력 필드 -->
        <div class="input-group w-25">
          <span class="input-group-text">Custom Units:</span>
          <input
              v-model.number="workUnit"
              class="form-control"
              disabled
              min="1"
              placeholder="Unit"
              type="number"
          />
        </div>
      </div>

      <!-- 안내 메시지 -->
      <div class="text-info">
        Each time a request is made to GPT, it processes items in groups of {{ workUnit }} items.
      </div>
      <div class="text-dark">
        A total of {{ totalRequests }} requests will be processed.
      </div>

      <!-- 경고 메시지 -->
      <div v-if="remainder !== 0" class="text-danger">
        There are {{ remainder }} items left to process with the last request.
      </div>
      <div v-if="workUnit > batchJob.total_size" class="text-bg-danger">
        The {{ workUnit }} work unit cannot exceed the total size.
      </div>
    </div>

    <!-- 버튼들 -->
    <div class="text-end mb-4 mt-3">
      <button :disabled="isPreviewRunning" class="btn btn-primary me-3" @click="previewRun">Preview</button>
      <button class="btn btn-success" @click="goToNextStep">Next</button>
    </div>

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
      currentStep: 3, // 현재 진행 중인 단계 (0부터 시작)
      batchJob: null, // 배치 작업 데이터
      loading: true, // 로딩 상태
      error: null, // 에러 메시지
      success: null,
      workUnit: 1,
      prompt: '',
      isPreviewRunning: false,
      previewData: [], // 미리보기 데이터
    };
  },
  computed: {
    remainder() {
      return this.batchJob.total_size % this.workUnit;
    },
    isReady() {
      return !this.loading;
    },
    totalRequests() {
      return this.batchJob ? Math.ceil(this.batchJob.total_size / this.workUnit) : 0;
    },
  },
  methods: {
    // 배치 작업 데이터 가져오기
    async fetchBatchJob() {
      this.loading = true;
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/configs/`, {withCredentials: true});
        this.batchJob = response.data;
        const config = this.batchJob.config ?? {};
        this.workUnit = config.workUnit ?? 1;
        this.prompt = config.prompt ?? '';
      } catch (error) {
        this.handleError("Failed to load Batch Job details. Please try again later.");
      } finally {
        this.loading = false;
      }
    },

    // 미리보기 실행
    async previewRun() {
      if (this.isPreviewRunning) return;

      this.isPreviewRunning = true;
      try {
        const payload = {
          prompt: this.prompt,
        };

        const response = await axios.post(`/api/batch-jobs/${this.batch_id}/preview/`, payload, {withCredentials: true});
        this.previewData = response.data;

      } catch (error) {
        this.handleError("Failed to run Batch Job preview. Please try again later.");
      } finally {
        this.isPreviewRunning = false;
      }
    },

    // 다음 단계로 이동
    goToNextStep() {
      this.$router.push(`/batch-jobs/${this.batch_id}/run`);
    },

    // 에러 처리 공통 메서드
    handleError(message) {
      this.success = null;
      this.error = message;
    }
  },

  // 컴포넌트 생성 시 배치 작업 데이터 가져오기
  async created() {
    await this.fetchBatchJob();
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}

.table th, .table td {
  vertical-align: middle;
}
</style>
