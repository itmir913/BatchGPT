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


    <div v-if="isReady" class="mb-4">
      <h3 class="text-center mt-4 mb-2">CSV Preview</h3>
      <div>
        <div v-if="selectedColumns.length > 0" class="text-dark">
          <div>The following columns will be used in the GPT request,</div>
          <div>You can use them in the prompt like this: {{
              selectedColumns.map(col => '{' + `${col}` + '}').join(', ')
            }}
          </div>
        </div>
        <div v-else class="text-dark">
          <div>Select columns to be used for GPT requests.</div>
          <div>You can use them in the prompt.</div>
        </div>
      </div>
      <CsvPreview
          :isReady="isReady"
          :previewData="filteredData"
          :selectedColumns="selectedColumns"
          @toggle-column="toggleColumnSelection"
      />
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
              :id="'work_unit' + unit"
              v-model.number="work_unit"
              :value="unit"
              class="form-check-input"
              disabled
              type="radio"
          />
          <label :for="'work_unit' + unit" class="form-check-label">{{ unit }}</label>
        </div>

        <!-- 사용자 입력 필드 -->
        <div class="input-group w-25">
          <span class="input-group-text">Custom Units:</span>
          <input
              v-model.number="work_unit"
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
        Each time a request is made to GPT, it processes items in groups of {{ work_unit }} items.
      </div>
      <div class="text-dark">
        A total of {{ totalRequests }} requests will be processed.
      </div>

      <!-- 경고 메시지 -->
      <div v-if="remainder !== 0" class="text-danger">
        There are {{ remainder }} items left to process with the last request.
      </div>
      <div v-if="work_unit > batchJob.total_size" class="text-bg-danger">
        The {{ work_unit }} work unit cannot exceed the total size.
      </div>
    </div>

    <!-- 결과 미리보기 -->
    <CsvPreview
        :isReady="isPreviewRunning"
        :previewData="previewFilteredResult"
        :selectedColumns="previewResultSelectedColumns"
        @toggle-column="toggleColumnSelection"
    />

    <!-- 버튼들 -->
    <div class="text-end mb-4 mt-3">
      <button class="btn btn-secondary me-3" @click="configSave">Save Prompt</button>
      <button :disabled="isPreviewRunning" class="btn btn-primary me-3" @click="previewRun">Preview</button>
      <button class="btn btn-success" @click="goToNextStep">Next</button>
    </div>

  </div>
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';
import CsvPreview from '@/components/CSVPreview.vue'; // 추가된 부분

export default {
  props: ['batch_id'],
  components: {
    ProgressIndicator,
    CsvPreview, // 추가된 부분
  },
  data() {
    return {
      currentStep: 3,
      batchJob: null,
      loading: true,
      error: null,
      success: null,

      work_unit: 1,
      prompt: '',

      previewData: [],
      selectedColumns: [],

      previewResult: [],
      previewResultSelectedColumns: [],
      isPreviewRunning: false,
    };
  },
  computed: {
    remainder() {
      return this.batchJob.total_size % this.work_unit;
    },
    isReady() {
      return !this.loading;
    },
    totalRequests() {
      return this.batchJob ? Math.ceil(this.batchJob.total_size / this.work_unit) : 0;
    },
    filteredData() {
      if (!Array.isArray(this.previewData ?? []))
        return [];
      // eslint-disable-next-line no-unused-vars
      return this.previewData.map(({index, ...rest}) => rest);
    },
    previewFilteredResult() {
      return this.previewResult;
    },
  },
  methods: {
    async fetchBatchJob() {
      this.loading = true;
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/configs/`, {withCredentials: true});
        this.batchJob = response.data;
        const config = this.batchJob.config ?? {};
        this.work_unit = config.work_unit ?? 1;
        this.prompt = config.prompt ?? '';
      } catch (error) {
        this.handleError(`Failed to load Batch Job details. ${error.message}`);
      } finally {
        this.loading = false;
      }
    },

    async fetchPreviewData() {
      this.loading = true;
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/preview/`, {withCredentials: true});
        this.previewData = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
      } catch (error) {
        this.handleError(`Failed to load Preview data. ${error.message}`);
      } finally {
        this.loading = false;
      }
    },

    async previewRun() {
      if (this.selectedColumns.length === 0) {
        this.handleError("Please select the columns of the table.")
        return;
      }
      try {
        this.isPreviewRunning = true;

        const payload = {
          prompt: this.prompt,
          'selected_headers': this.selectedColumns,
        };

        const response = await axios.post(`/api/batch-jobs/${this.batch_id}/preview/`, payload);

        if (!response.data) {
          this.handleError("No data received from Server.")
          this.batchJob = null;
          return;
        }

        this.previewResult = response.data;
        this.handleSuccess("Preview loaded successfully!")
      } catch (error) {
        if (error.response && error.response.data) {
          const errorData = error.response.data;

          // Handle error if it's a JSON object
          if (errorData && errorData.error) {
            this.handleError(`Failed to load Preview data. Please try again later: ${errorData.error}`);
          } else {
            this.handleError(`Failed to load Preview data. Unknown error.`);
          }
        } else {
          this.handleError(`Failed to load Preview data. Please try again later: ${error.message}`);
        }
      } finally {
        this.isPreviewRunning = false;
      }
    },

    toggleColumnSelection(column) {
      if (this.selectedColumns.includes(column)) {
        this.selectedColumns = this.selectedColumns.filter(c => c !== column);
      } else {
        this.selectedColumns.push(column);
      }
    },

    async configSave() {
      this.clearMessages();
      this.loadingSave = true;

      if (this.work_unit > this.batchJob.total_size) {
        this.error = "The work unit cannot exceed the total size.";
        this.loadingSave = false;
        return;
      }

      if (!this.prompt.trim()) {
        this.error = "Prompt cannot be empty.";
        this.loadingSave = false;
        return;
      }

      const payload = {
        work_unit: this.batchJob.work_unit,
        prompt: this.prompt,
        gpt_model: this.batchJob.gpt_model,
      };

      try {
        const response = await axios.patch(`/api/batch-jobs/${this.batch_id}/configs/`, payload);

        if (!response.data) {
          this.error = "No data received from Server.";
          this.success = null;
          this.batchJob = null;
          return;
        }

        this.batchJob = response.data;
        const config = this.batchJob.config ?? {};
        this.prompt = config.prompt ?? '';

        this.success = "Configuration updated successfully.";
      } catch (err) {
        this.error = `Error updating configuration: ${err.message}`;
      } finally {
        this.loadingSave = false;
      }
    },

    goToNextStep() {
      this.$router.push(`/batch-jobs/${this.batch_id}/run`);
    },

    clearMessages() {
      this.success = null;
      this.error = null;
    },

    handleSuccess(message) {
      this.clearMessages();
      this.success = message;
      this.error = null;
    },

    handleError(message) {
      this.clearMessages();
      this.success = null;
      this.error = message;
    }
  },

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