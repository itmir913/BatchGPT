<template>
  <div class="container mt-4">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center mb-3">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <div v-if="formStatus.isReady" class="mb-3">
      <!-- File Type이 CSV일 때 -->
      <div class="mb-3 g-3 p-2">
        <h3 class="text-center mt-3 mb-2">CSV Preview</h3>
        <div>
          <div v-if="previewData.CSV.selectedColumns.length > 0" class="text-dark">
            <div>The following columns will be used in the GPT request,</div>
            <div>You can use them in the prompt like this: {{
                previewData.CSV.selectedColumns.map(col => '{' + `${col}` + '}').join(', ')
              }}
            </div>
          </div>
          <div v-else class="text-dark">
            <div>Select columns to be used for GPT requests.</div>
            <div>You can use them in the prompt.</div>
          </div>
        </div>
        <CsvPreview
            :isReady="formStatus.isReady"
            :previewData="filteredData"
            :selectedColumns="previewData.CSV.selectedColumns"
            @toggle-column="toggleColumnSelection"
        />
      </div>

      <!-- 프롬프트 입력란 -->
      <div class="mb-3 g-3 p-2">
        <h3>Input Prompt</h3>
        <textarea
            v-model="previewData.prompt"
            class="form-control"
            placeholder="Enter your prompt..."
            rows="5"
        ></textarea>
      </div>

      <!-- 작업 단위 설정 컴포넌트 -->
      <div class="mb-3 g-3 p-2">
        <WorkUnitSettings
            :batchJob="batchJob"
            :isReady="formStatus.isReady"
            :work_unit="previewData.work_unit"
        />
      </div>

      <!-- 결과 미리보기 -->
      <div class="mb-3 g-3 p-2">
        <!-- File Type이 CSV일 때 -->
        <CsvPreview
            :isReady="formStatus.isResultLoading"
            :previewData="resultFilteredData"
            :selectedColumns="previewData.CSV.resultSelectedColumns"
            @toggle-column="toggleColumnSelection"
        />
      </div>

      <!-- 메시지 표시 -->
      <div>
        <div v-if="messages.success" class="alert alert-success text-center mt-3" role="alert">{{
            messages.success
          }}
        </div>
        <div v-if="messages.error" class="alert alert-danger text-center mt-3" role="alert">{{ messages.error }}</div>
      </div>

      <!-- 버튼들 -->
      <div class="text-end mb-3 mt-3">
        <button class="btn btn-secondary me-3" @click="configSave">Save</button>
        <button :disabled="formStatus.isPreviewLoading" class="btn btn-primary me-3" @click="previewRun">Preview
        </button>
        <button class="btn btn-success" @click="goToNextStep">Next</button>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from "@/components/BatchJobProgressIndicator.vue";
import CsvPreview from "@/components/CSVPreview.vue";
import axios from "@/configs/axios";
import WorkUnitSettings from "@/components/WorkUnitSettings.vue";

const API_BASE_URL = "/api/batch-jobs/";
const API_PREVIEW_POSTFIX = "/preview/";
const API_CONFIGS_POSTFIX = "/configs/";
const SUCCESS_MESSAGES = {
  updatedConfigs: "Configuration updated successfully.",
  loadResult: "Preview result loaded successfully!",
};
const ERROR_MESSAGES = {
  loadBatchJob: "Failed to load Batch Job details. Please try again later.",
  loadPreview: "Failed to load Preview data. Please try again later.",
  noColumn: "Please select at least one column.",
  emptyPrompt: "Prompt cannot be empty.",
  noDataReceived: "No data received from Server.",
  updatedConfigs: "Error updating configuration. Please try again later.",
  loadResult: "Failed to load Preview data. Please try again later.",
};

export default {
  props: ['batch_id'],
  components: {WorkUnitSettings, CsvPreview, ProgressIndicator},
  data() {
    return {
      currentStep: 3,
      batchJob: null,
      loadingState: {loading: true, previewLoading: false, configSave: false, resultLoading: false},
      messages: {success: null, error: null},
      previewData: {
        fetchData: [],
        prompt: '',
        work_unit: 1,
        CSV: {
          selectedColumns: [],
          resultSelectedColumns: [], // 사용하지 않음
        },
        resultData: [],
      },
    };
  },
  computed: {
    formStatus() {
      return {
        isReady: !this.loadingState.loading,
        isLoading: this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
        isPreviewLoading: this.loadingState.previewLoading,
        isResultLoading: this.loadingState.resultLoading,
      };
    },
    filteredData() {
      if (!Array.isArray(this.previewData.fetchData ?? []))
        return [];
      // eslint-disable-next-line no-unused-vars
      return this.previewData.fetchData.map(({index, ...rest}) => rest);
    },
    resultFilteredData() {
      return this.previewData.resultData;
    },
  },
  methods: {
    clearMessages() {
      this.messages = {success: null, error: null};
      this.loadingState.error = null;
      this.loadingState.success = null;
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();

      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.loadingState.error = type === "error" ? fullMessage : null;
      this.loadingState.success = type === "success" ? fullMessage : null;
    },

    async fetchBatchJob() {
      try {
        this.clearMessages();
        const response = await axios.get(`${API_BASE_URL}${this.batch_id}${API_CONFIGS_POSTFIX}`, {withCredentials: true});
        this.batchJob = response.data;

        this.previewData.work_unit = this.batchJob.config.work_unit ?? 1;
        this.previewData.prompt = this.batchJob.config.prompt ?? '';
        this.previewData.CSV.selectedColumns = this.batchJob.config.selected_headers ?? [];
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.loadBatchJob);
      } finally {
        this.loadingState.loading = false;
      }
    },

    async fetchPreviewData() {
      try {
        this.clearMessages();
        this.loadingState.previewLoading = true;
        const response = await axios.get(`${API_BASE_URL}${this.batch_id}${API_PREVIEW_POSTFIX}`, {withCredentials: true});
        this.previewData.fetchData = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.loadPreview);
      } finally {
        this.loadingState.previewLoading = false;
      }
    },

    toggleColumnSelection(column) {
      if (this.previewData.CSV.selectedColumns.includes(column)) {
        this.previewData.CSV.selectedColumns = this.previewData.CSV.selectedColumns.filter(c => c !== column);
      } else {
        this.previewData.CSV.selectedColumns.push(column);
      }
    },

    async configSave() {
      this.clearMessages();
      this.loadingState.configSave = true;

      // TODO CSV에서만 작동해야 한다.
      if (Array.isArray(this.selectedColumns) && this.selectedColumns.length === 0) {
        this.handleMessages("error", ERROR_MESSAGES.noColumn);
        this.loadingState.configSave = false;
        return;
      }

      if (!this.previewData.prompt.trim()) {
        this.handleMessages("error", ERROR_MESSAGES.emptyPrompt);
        this.loadingSave = false;
        return;
      }

      const payload = {
        'work_unit': this.batchJob.work_unit,
        'prompt': this.previewData.prompt,
        'gpt_model': this.batchJob.gpt_model,
        'selected_headers': this.previewData.CSV.selectedColumns,
      };

      try {
        const response = await axios.patch(`${API_BASE_URL}${this.batch_id}${API_CONFIGS_POSTFIX}`, payload);
        this.batchJob = response.data;

        if (!this.batchJob) {
          this.handleMessages("error", ERROR_MESSAGES.noDataReceived);
          this.batchJob = null;
          return;
        }

        this.batchJob.config = this.batchJob.config ?? {};
        this.previewData.work_unit = this.batchJob.config.work_unit ?? 1;
        this.previewData.prompt = this.batchJob.config.prompt ?? '';
        this.previewData.CSV.selectedColumns = this.batchJob.config.selected_headers ?? [];

        this.handleMessages("success", SUCCESS_MESSAGES.updatedConfigs);
      } catch (err) {
        this.handleMessages("error", ERROR_MESSAGES.updatedConfigs);
      } finally {
        this.loadingSave = false;
      }

    },

    async previewRun() {
      this.clearMessages();

      if (this.previewData.CSV.selectedColumns.length === 0) {
        this.handleMessages("error", ERROR_MESSAGES.noColumn);
        return;
      }

      try {
        this.loadingState.resultLoading = true;

        const payload = {
          'prompt': this.previewData.prompt,
          'selected_headers': this.previewData.CSV.selectedColumns,
        };

        const response = await axios.post(`${API_BASE_URL}${this.batch_id}${API_PREVIEW_POSTFIX}`, payload);
        this.previewData.resultData = response.data;

        if (!response.data) {
          this.handleMessages("error", ERROR_MESSAGES.noDataReceived);
          this.batchJob = null;
          return;
        }

        this.handleMessages("success", SUCCESS_MESSAGES.loadResult);
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.loadResult);
      } finally {
        this.loadingState.resultLoading = false;
      }

    },

    goToNextStep() {
      this.$router.push(`/batch-jobs/${this.batch_id}/run`);
    },
  },
  mounted() {
    this.fetchBatchJob();
    this.fetchPreviewData();
  },
};
</script>


<style scoped>
.container {
  max-width: 1000px;
}
</style>