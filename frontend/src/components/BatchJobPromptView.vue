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

    <!-- 파일 정보 표시 -->
    <div v-if="batchJob && !loading && !error" class="mb-4">
      <h5>Uploaded File</h5>
      <div class="table-responsive">
        <table class="table table-striped table-bordered">
          <thead class="table-light">
          <tr>
            <th style="width: 30%;">Item</th> <!-- 왼쪽 열 너비 조정 -->
            <th style="width: 70%;">Information</th> <!-- 오른쪽 열 너비 조정 -->
          </tr>
          </thead>
          <tbody>
          <tr>
            <td>File Name</td>
            <td>{{ batchJob.file_name }}</td>
          </tr>
          <tr>
            <td>Total Size</td>
            <td>{{ batchJob.total_size }}</td>
          </tr>
          <tr>
            <td>File Type</td>
            <td>{{ batchJob.file_type }}</td>
          </tr>
          </tbody>
        </table>

        <!-- 작업 단위 설정 -->
        <div v-if="batchJob && !loading && !error && batchJob.file_type === 'pdf'">
          <div class="mb-4">
            <h5 class="text-center">Select Task Unit</h5>
            <div class="d-flex justify-content-center align-items-center mb-2">
              <div class="form-check me-3">
                <input id="workUnit1" v-model.number="workUnit" class="form-check-input" type="radio" value="1"/>
                <label class="form-check-label" for="workUnit1">1</label>
              </div>
              <div class="form-check me-3">
                <input id="workUnit2" v-model.number="workUnit" class="form-check-input" type="radio" value="2"/>
                <label class="form-check-label" for="workUnit2">2</label>
              </div>
              <div class="form-check me-3">
                <input id="workUnit4" v-model.number="workUnit" class="form-check-input" type="radio" value="4"/>
                <label class="form-check-label" for="workUnit4">4</label>
              </div>
              <div class="form-check me-3">
                <input id="workUnit8" v-model.number="workUnit" class="form-check-input" type="radio" value="8"/>
                <label class="form-check-label" for="workUnit8">8</label>
              </div>

              <!-- 사용자 입력 필드 -->
              <div class="input-group w-25"> <!-- 너비를 25%로 설정 -->
                <span class="input-group-text">Custom Units:</span>
                <input v-model.number="workUnit" class="form-control" min="1" placeholder="Unit" type="number"/>
              </div>
            </div>
          </div>

          <!-- 경고 메시지 -->
          <div v-if="batchJob.total_size % workUnit !== 0" class="text-danger mt-2">
            작업 단위에 따라 나누었을 때 남는 부분이 있습니다!
          </div>
        </div>

      </div>
    </div>

    <!-- 프롬프트 입력란 -->
    <div v-if="!loading && !error" class="mb-4">
      <h5>Input Prompt</h5>
      <textarea v-model="promptInput" class="form-control" placeholder="Enter your prompt..." rows="3"></textarea>
      <!-- 버튼을 별도의 div로 감싸고 정렬 -->
      <div class="text-end mt-2">
        <button :disabled="loadingPreview" class="btn btn-primary" @click="previewResult">Preview</button>
      </div>
    </div>

    <!-- 미리보기 결과 -->
    <div v-if="previewData.length > 0" class="mt-4">
      <h5 class="mt-4">Preview Result</h5>
      <table class="table table-bordered">
        <thead>
        <tr>
          <th>Raw Data</th>
          <th>Response</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, index) in previewData.slice(0, 5)" :key="index">
          <td>{{ item.raw }}</td>
          <td class="animated-text">{{ item.response }}</td>
        </tr>
        </tbody>
      </table>
      <div class="text-end my-4">
        <button :disabled="isNextButtonDisabled" class="btn btn-success" @click="goToNextStep">Next</button>
      </div>
    </div>

  </div>
</template>


<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';

export default {
  name: 'BlurAnimation',
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
      workUnit: 1,
      promptInput: '',
      loadingPreview: false,
      previewData: [], // 미리보기 데이터
    };
  },
  methods: {
    // 배치 작업 데이터 가져오기
    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/preview/`, {
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

    previewResult() {
      this.loadingPreview = true;
      // 프롬프트 입력과 작업 단위를 기반으로 미리보기 데이터를 생성하는 로직
      // 예시 데이터
      this.previewData = [
        {raw: '예시 데이터 1', response: '응답 결과 1'},
        {raw: '예시 데이터 2', response: '응답 결과 2'},
        {raw: '예시 데이터 3', response: '응답 결과 3'},
        {raw: '예시 데이터 4', response: '응답 결과 4'},
        {raw: '예시 데이터 5', response: '응답 결과 5'},
        // 필요에 따라 더 많은 데이터를 추가
      ];
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

.mb-4 {
  margin-bottom: 1.5rem;
}

h5 {
  margin-bottom: .5rem;
}

.table th, .table td {
  vertical-align: middle;
}

.animated-text {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  animation: blurAnimation 1s infinite; /* 애니메이션 적용 */
}

@keyframes blurAnimation {
  0% {
    filter: blur(5px); /* 시작 시 흐림 효과 */
    opacity: 0.1;
  }
  50% {
    filter: blur(8px); /* 중간에 선명하게 */
    opacity: 0.3;
  }
  100% {
    filter: blur(5px); /* 다시 흐림 효과 */
    opacity: 0.1;
  }
}
</style>