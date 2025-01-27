<template>
  <div class="container my-4">
    <ToastView
        ref="toast"
        :message="messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator :batch_id="batch_id" :currentStep="3"/>
      </div>

      <div class="col-md-9">
        <!-- 로딩 상태 -->
        <div v-if="formStatus.isLoading" class="text-center mb-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>{{ formStatus.loadingMessage }}</p>
        </div>

        <div v-if="formStatus.isReady" class="mb-3">
          <!-- Input Prompt 컴포넌트 -->
          <InputPrompt
              :disabled="batchJobStatus.isEditDisabled"
              :prompt="previewData.prompt"
              @update:prompt="(newPrompt) => (previewData.prompt = newPrompt)"
          />

          <!-- 작업 단위 설정 컴포넌트 -->
          <div class="mb-3">
            <WorkUnitSettings
                :batchJob="batchJob"
                :disabled="batchJobStatus.isEditDisabled"
                :isReady="formStatus.isReady"
                :fileType="batchJob.file_type"
                :work_unit="previewData.work_unit"
            />
          </div>

          <div class="mb-3">
            <CsvPreview
                :disabled="batchJobStatus.isEditDisabled"
                :fileType="batchJob.file_type"
                :isReady="formStatus.isReady"
                :previewData="filteredData"
                :selectedColumns="previewData.CSV.selectedColumns"
                @toggle-column="toggleColumnSelection"
            />
          </div>

          <!-- 결과 미리보기 -->
          <div v-if="!formStatus.isResultLoading && resultFilteredData.length !== 0" class="mb-3">
            <!-- File Type이 CSV일 때 -->
            <div class="table-responsive">
              <table class="table table-striped table-hover align-middle custom-table">
                <thead class="table-dark">
                <tr>
                  <!-- 열 헤더 -->
                  <th scope="col" style="width: 50%;">Prompt</th>
                  <th scope="col" style="width: 50%;">Result</th>
                </tr>
                </thead>
                <tbody>
                <!-- resultFilteredData를 사용하여 데이터 출력 -->
                <tr v-for="(item, index) in resultFilteredData" :key="index">
                  <td>{{ item.prompt }}</td>
                  <td>{{ item.result }}</td>
                </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 버튼들 -->
          <div class="text-end my-3">
            <button
                class="btn btn-secondary me-3"
                @click="configSave">
              Save
            </button>
            <button :disabled="formStatus.isPreviewLoading || formStatus.isEditable"
                    class="btn btn-primary me-3"
                    @click="previewRun">
              Preview
            </button>
            <button class="btn btn-success" @click="goToNextStep">Next</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from "@/components/batch-job/components/ProgressIndicator.vue";
import CsvPreview from "@/components/batch-job/components/CSVPreview.vue";
import InputPrompt from "@/components/batch-job/components/InputPrompt.vue";
import WorkUnitSettings from "@/components/batch-job/components/WorkUnitSettings.vue";
import TaskUnitChecker from "@/components/batch-job/utils/TaskUnitChecker"
import {
  ERROR_MESSAGES,
  fetchBatchJobConfigsAPI,
  fetchPreviewAPI,
  fetchPreviewResultsAPI,
  modifyBatchJobConfigsAPI,
  shouldEditDisabled,
  SUCCESS_MESSAGES
} from '@/components/batch-job/utils/BatchJobUtils';
import {DEFAULT_GPT_MODEL} from "@/components/batch-job/utils/GPTUtils";
import ToastView from "@/components/batch-job/components/ToastView.vue";


export default {
  props: ['batch_id'],
  components: {ToastView, WorkUnitSettings, CsvPreview, ProgressIndicator, InputPrompt},
  data() {
    return {
      batchJob: null,
      loadingState: {loading: true, previewLoading: false, configSave: false, resultLoading: false},
      messages: {success: null, error: null},
      previewData: {
        fetchData: [],
        prompt: '',
        work_unit: 1,
        CSV: {
          selectedColumns: [],
        },
        resultData: [],
      },
      taskUnits: {
        taskUnitChecker: null,
        taskUnitIds: [],
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
        isEditable: shouldEditDisabled(this.batchJob?.batch_job_status),
      };
    },
    filteredData() {
      if (!Array.isArray(this.previewData.fetchData ?? []))
        return [];
      // eslint-disable-next-line no-unused-vars
      return this.previewData.fetchData.map(({index, ...rest}) => rest);
    },
    resultFilteredData() {
      if (!Array.isArray(this.previewData.resultData ?? []))
        return [];
      // eslint-disable-next-line no-unused-vars
      return this.previewData.resultData.map(({prompt, result, ...rest}) => ({prompt, result}));
    },
    batchJobStatus() {
      return {
        isEditDisabled: shouldEditDisabled(this.batchJob?.batch_job_status)
      };
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

        const {batchJob, configs} = await fetchBatchJobConfigsAPI(this.batch_id);
        this.batchJob = batchJob;
        this.previewData.work_unit = configs.work_unit ?? 1;
        this.previewData.prompt = configs.prompt ?? '';
        this.gpt_model = configs.gpt_model ?? DEFAULT_GPT_MODEL;
        this.previewData.CSV.selectedColumns = configs.selected_headers ?? [];

      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJob} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJob} No response received.`);
        }
      } finally {
        this.loadingState.loading = false;
      }
    },

    async fetchPreviewData() {
      try {
        this.clearMessages();
        this.loadingState.previewLoading = true;
        this.previewData.fetchData = await fetchPreviewAPI(this.batch_id);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.loadPreview} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.loadPreview} No response received.`);
        }
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
      if (Array.isArray(this.previewData.CSV.selectedColumns) && this.previewData.CSV.selectedColumns.length === 0) {
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
        const {batchJob, configs} = await modifyBatchJobConfigsAPI(this.batch_id, payload);
        this.batchJob = batchJob;

        if (!this.batchJob) {
          this.handleMessages("error", ERROR_MESSAGES.noDataReceived);
          this.batchJob = null;
          return;
        }

        this.previewData.work_unit = configs.work_unit ?? 1;
        this.previewData.prompt = configs.prompt ?? '';
        this.previewData.CSV.selectedColumns = configs.selected_headers ?? [];

        this.handleMessages("success", SUCCESS_MESSAGES.updatedConfigs);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.updatedConfigs} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.updatedConfigs} No response received.`);
        }
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
        this.taskUnits.taskUnitChecker.stopAllChecking()

        const payload = {
          'prompt': this.previewData.prompt,
          'selected_headers': this.previewData.CSV.selectedColumns,
        };

        this.previewData.resultData = await fetchPreviewResultsAPI(this.batch_id, payload);

        if (!this.previewData.resultData) {
          this.handleMessages("error", ERROR_MESSAGES.noDataReceived);
          this.batchJob = null;
          return;
        }

        this.taskUnitIds = this.previewData.resultData.map(item => item.task_unit_id);

        this.taskUnits.taskUnitChecker.startCheckingTaskUnits(this.batch_id, this.taskUnitIds);
        this.taskUnits.taskUnitChecker.setOnCompleteCallback((taskId, status, result) => {
          const previewItem = this.previewData.resultData.find(item => item.task_unit_id === taskId);
          if (previewItem) {
            previewItem.result = result;
          } else {
            console.error(`Task ID ${taskId} not found in previewData.resultData`);
          }
        });

        this.handleMessages("success", SUCCESS_MESSAGES.loadPreviewResult);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.loadResult} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.loadResult} No response received.`);
        }
      } finally {
        this.loadingState.resultLoading = false;
      }

    },

    goToNextStep() {
      const selectedHeader = this.batchJob?.configs?.selected_headers ?? []
      if (selectedHeader.length <= 0) {
        this.handleMessages("error", ERROR_MESSAGES.noColumn)
        return
      }

      const prompt = this.batchJob?.configs?.prompt ?? ''
      if (!prompt.trim()) {
        this.handleMessages("error", ERROR_MESSAGES.emptyPrompt);
        return;
      }

      this.$router.push(`/batch-jobs/${this.batch_id}/run`);
    },
  },
  async mounted() {
    this.taskUnits.taskUnitChecker = new TaskUnitChecker();
    await this.fetchBatchJob();
    await this.fetchPreviewData();
  },
  beforeUnmount() {
    this.taskUnits.taskUnitChecker.stopAllChecking();
  },
};
</script>

<style scoped>
/* 열 구분선 추가 */
.custom-table td,
.custom-table th {
  border-right: 1px solid #dee2e6; /* Bootstrap 기본 테이블 경계선 색상 */
}

.custom-table th:last-child,
.custom-table td:last-child {
  border-right: none; /* 마지막 열은 구분선 제거 */
}
</style>
