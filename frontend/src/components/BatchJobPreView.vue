<template>
  <div class="container mt-5">

    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loading || isPreviewRunning" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 메시지 영역 -->
    <div v-if="success && !error" class="alert alert-success text-center mt-4" role="alert">{{ success }}</div>
    <div v-if="error" class="alert alert-danger text-center mt-4" role="alert">{{ error }}</div>

    <!-- CSV 데이터 미리보기 -->
    <div v-if="isReady" class="mb-4">
      <h3 class="text-center mt-4 mb-2">CSV Preview</h3>
      <div>
        <div v-if="selectedColumn" class="text-dark">
          The "{{ selectedColumn }}" column will be used to send requests to GPT.
        </div>
        <div v-else class="text-dark">
          Click on a column to select it for GPT requests.
        </div>
      </div>
      <table v-if="filteredData.length > 0" class="table table-hover table-bordered table-striped mt-3">
        <thead class="table-primary">
        <tr>
          <!-- 각 열 이름 -->
          <th
              v-for="(value, key) in filteredData[0]"
              :key="'header-' + key"
              :class="{ 'selected-column': selectedColumn === key }"
              style="cursor: pointer;"
              @click="selectColumn(key)"
          >
            {{ key }}
          </th>
        </tr>
        </thead>
        <tbody>
        <!-- 데이터 행 렌더링 -->
        <tr v-for="row in filteredData" :key="'row-' + row.id"> <!-- row.index에서 row.id로 수정 -->
          <td
              v-for="(value, key) in row"
              :key="'cell-' + key"
              :class="{ 'selected-column': selectedColumn === key }"
              style="cursor: pointer;"
              @click="selectColumn(key)"
          >
            {{ value }}
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- 프롬프트 입력란 -->
    <div v-if="isReady" class="mb-4">
      <h3>Input Prompt</h3>
      <textarea
          v-model="prompt"
          class="form-control"
          placeholder="Enter your prompt..."
          rows="5"
      ></textarea>
    </div>

    <!-- 작업 단위 설정 -->
    <div v-if="batchJob && isReady">
      <h3 class="text-center mt-4 mb-2">Select Number of Items per Task</h3>
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

      previewData: [], // 서버에서 가져온 CSV 데이터
      selectedColumn: null, // 선택된 열 이름

      isPreviewRunning: false,
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
    filteredData() {
      if (!Array.isArray(this.previewData ?? {}))
        return {};

      // eslint-disable-next-line no-unused-vars
      return this.previewData.map(({index, ...rest}) => rest);
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

    async fetchPreviewData() {
      this.loading = true;
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/preview/`, {withCredentials: true});

        if (typeof response.data === 'string') {
          this.previewData = JSON.parse(response.data);
        } else {
          this.previewData = response.data;
        }

      } catch (error) {
        this.handleError("Failed to load Preview data. Please try again later.");
      } finally {
        this.loading = false;
      }
    },

    previewRun() {
      this.isPreviewRunning = true;

      try {

        this.success = "Preview loaded successfully!";
      } catch (error) {
        this.handleError("Failed to load Preview data. Please try again later.");
      } finally {
        this.isPreviewRunning = false;
      }
    },

    selectColumn(key) {
      this.selectedColumn = key; // 클릭된 열을 선택
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
    await this.fetchPreviewData();
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>

<style scoped>
/* 선택된 열 강조 */
.selected-column {
  background-color: #d1ecf1 !important; /* 밝은 파란색 배경 */
  font-weight: bold; /* 텍스트 굵게 */
}

/* 테이블 스타일 */
.table th,
.table td {
  text-align: center;
}

.table th {
  cursor: pointer;
}

.table th:hover,
.table td:hover {
  background-color: #f8d7da; /* 마우스 오버 시 밝은 빨간색 */
}
</style>