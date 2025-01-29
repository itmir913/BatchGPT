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
                :fileType="batchJob.file_type"
                :isReady="formStatus.isReady"
                :work_unit="previewData.work_unit"
                @update:work_unit="(newWorkUnit) => (previewData.work_unit = newWorkUnit)"
            />
          </div>

          <div class="mb-3 scroll-container">
            <CsvPreview
                :disabled="batchJobStatus.isEditDisabled"
                :fileType="batchJob.file_type"
                :isReady="formStatus.isReady"
                :previewData="filteredData"
                :selectedColumns="previewData.CSV.selectedColumns"
                @toggle-column="toggleColumnSelection"
            />
          </div>

          <div v-if="dynamicTableSupportedFileTypes.includes(batchJob.file_type)" class="mb-3 scroll-container">
            <TableView :data="filteredData"/>
          </div>

          <!-- 버튼들 -->
          <div class="text-end my-3">
            <button
                class="btn btn-secondary me-3"
                @click="configSave">
              Save
            </button>
            <button class="btn btn-success" @click="goToNextStep">Next</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.scroll-container {
  overflow-x: auto;
  white-space: pre-wrap;
}
</style>

<script>
import ProgressIndicator from "@/components/batch-job/common/ProgressIndicator.vue";
import CsvPreview from "@/components/batch-job/previews/CSVPreviewTable.vue";
import InputPrompt from "@/components/batch-job/previews/InputPrompt.vue";
import WorkUnitSettings from "@/components/batch-job/previews/WorkUnitSelector.vue";
import {
  ERROR_MESSAGES,
  fetchBatchJobConfigsAPI,
  fetchPreviewAPI,
  modifyBatchJobConfigsAPI,
  shouldEditDisabled,
  SUCCESS_MESSAGES
} from '@/components/batch-job/utils/BatchJobUtils';
import ToastView from "@/components/batch-job/common/ToastView.vue";
import {
  CSVSupportedFileTypes,
  DynamicTableSupportedFileTypes,
  WorkUnitSupportedFileTypes
} from '@/components/batch-job/utils/SupportedFileTypes';
import TableView from "@/components/batch-job/previews/FilePreviewTable.vue";

export default {
  props: ['batch_id'],
  components: {TableView, ToastView, WorkUnitSettings, CsvPreview, ProgressIndicator, InputPrompt},
  data() {
    return {
      batchJob: null,
      loadingState: {loading: true, configSave: false},
      messages: {success: null, error: null},
      previewData: {
        fetchData: [],
        prompt: '',
        work_unit: 1,
        CSV: {
          selectedColumns: [],
        },
      },
    };
  },
  computed: {
    formStatus() {
      return {
        isReady: !this.loadingState.loading,
        isLoading: this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
      };
    },
    filteredData() {
      if (!Array.isArray(this.previewData.fetchData ?? []))
        return [];
      // eslint-disable-next-line no-unused-vars
      return this.previewData.fetchData.map(({index, ...rest}) => rest);
    },
    batchJobStatus() {
      return {
        isEditDisabled: shouldEditDisabled(this.batchJob?.batch_job_status)
      };
    },
    dynamicTableSupportedFileTypes() {
      return DynamicTableSupportedFileTypes;
    },
  },
  methods: {
    clearMessages() {
      this.messages = {success: null, error: null};
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();
      this.messages[type] = details ? `${message} - ${details}` : message;
    },

    async fetchBatchJob() {
      try {
        this.clearMessages();
        this.loadingState.loading = true;

        const {batchJob, configs} = await fetchBatchJobConfigsAPI(this.batch_id);
        this.batchJob = batchJob;
        this.previewData.work_unit = configs.work_unit ?? 1;
        this.previewData.prompt = configs.prompt ?? '';
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
        this.previewData.fetchData = await fetchPreviewAPI(this.batch_id);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.loadPreview} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.loadPreview} No response received.`);
        }
      } finally {
        this.loadingState.loading = false;
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

      if (CSVSupportedFileTypes.includes(this.batchJob.file_type)
          && Array.isArray(this.previewData.CSV.selectedColumns)
          && this.previewData.CSV.selectedColumns.length === 0) {
        this.handleMessages("error", ERROR_MESSAGES.noColumn);
        this.loadingState.configSave = false;
        return;
      }

      if (WorkUnitSupportedFileTypes.includes(this.batchJob.file_type)
          && this.previewData.work_unit < 1) {
        this.handleMessages("error", ERROR_MESSAGES.noWorkUnit);
        this.loadingState.configSave = false;
        return;
      }

      if (!this.previewData.prompt.trim()) {
        this.handleMessages("error", ERROR_MESSAGES.emptyPrompt);
        this.loadingSave = false;
        return;
      }

      const payload = {
        'work_unit': this.previewData.work_unit,
        'prompt': this.previewData.prompt,
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

        await this.fetchPreviewData();
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

    goToNextStep() {
      this.$router.push(`/batch-jobs/${this.batch_id}/run`);
    },
  },
  async mounted() {
    await this.fetchBatchJob();
    await this.fetchPreviewData();
  },
};
</script>
