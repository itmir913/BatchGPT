<template>
  <div class="container my-4">
    <ToastView
        ref="toast"
        :message="messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator
            :batch_id="batch_id"
            :currentStep="3"
            :batch_status="batchJobStatus.Status"
        />
      </div>

      <div class="col-md-9">
        <LoadingView
            v-if="formStatus.isLoading"
        />

        <div v-else class="mb-3">
          <div class="mb-3">
            <InputPrompt
                :disabled="batchJobStatus.isEditDisabled"
                :prompt="previewData.prompt"
                @update:prompt="(newPrompt) => (previewData.prompt = newPrompt)"
            />
          </div>

          <div v-if="WorkUnitSupportedFileTypes.includes(batchJob.file_type)"
               class="mb-3">
            <WorkUnitSettings
                :batchJob="batchJob"
                :disabled="batchJobStatus.isEditDisabled"
                :work_unit="previewData.work_unit"
                @update:work_unit="(newWorkUnit) => (previewData.work_unit = newWorkUnit)"
            />
          </div>

          <div v-if="PDFModeSupportedFileTypes.includes(batchJob.file_type)"
               class="mb-3">
            <PDFModeSelector
                :disabled="batchJobStatus.isEditDisabled"
                :fileType="batchJob.file_type"
                :selectedMode="previewData.PDF.selectedMode"
                :supportedMode="previewData.PDF.supportedMode"
                @update:selectedMode="(newWorkUnit) => (previewData.PDF.selectedMode = newWorkUnit)"
            />
          </div>

          <div v-if="CSVSupportedFileTypes.includes(batchJob.file_type)
                        && filteredData && filteredData.length > 0"
               class="mb-3 scroll-container">
            <CsvPreview
                :disabled="batchJobStatus.isEditDisabled"
                :previewData="filteredData"
                :selectedColumns="previewData.CSV.selectedColumns"
                @toggle-column="toggleColumnSelection"
            />
          </div>

          <div class="text-end my-3">
            <button
                class="btn btn-secondary me-3"
                @click="configSave">
              Save
            </button>
            <button class="btn btn-success" @click="goToNextStep">Next</button>
          </div>

          <div v-if="dynamicTableSupportedFileTypes.includes(batchJob.file_type)
                        && filteredData && filteredData.length > 0" class="mb-3 scroll-container">
            <FilePreviewTableView
                :data="filteredData"
            />
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
  fetchPDFSupportedModeAPI,
  fetchPreviewAPI,
  getStepLink,
  modifyBatchJobConfigsAPI,
  shouldEditDisabled,
  SUCCESS_MESSAGES
} from '@/components/batch-job/utils/BatchJobUtils';
import ToastView from "@/components/batch-job/common/ToastView.vue";
import {
  CSVSupportedFileTypes,
  DynamicTableSupportedFileTypes,
  PDFModeSupportedFileTypes,
  WorkUnitSupportedFileTypes
} from '@/components/batch-job/utils/SupportedFileTypes';
import FilePreviewTableView from "@/components/batch-job/previews/FilePreviewTable.vue";
import PDFModeSelector from "@/components/batch-job/previews/PDFModeSelector.vue";
import LoadingView from "@/components/batch-job/common/LoadingSpinner.vue";
import {getErrorMessage} from "@/components/batch-job/utils/CommonFunctions";

export default {
  props: ['batch_id'],
  components: {
    LoadingView,
    PDFModeSelector, FilePreviewTableView, ToastView, WorkUnitSettings, CsvPreview, ProgressIndicator, InputPrompt
  },
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
        PDF: {
          supportedMode: {},
          selectedMode: '',
        }
      },
    };
  },
  computed: {
    formStatus() {
      return {
        isLoading: this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
      };
    },
    filteredData() {
      let data = this.previewData.fetchData?.data;
      data = typeof data === 'string' ? JSON.parse(data) : data;
      if (!Array.isArray(data ?? []))
        return [];
      return data;
    },
    batchJobStatus() {
      return {
        isEditDisabled: shouldEditDisabled(this.batchJob?.batch_job_status),
        Status: this.batchJob ? this.batchJob?.batch_job_status : null,
      };
    },
    dynamicTableSupportedFileTypes() {
      return DynamicTableSupportedFileTypes;
    },
    CSVSupportedFileTypes() {
      return CSVSupportedFileTypes;
    },
    PDFModeSupportedFileTypes() {
      return PDFModeSupportedFileTypes;
    },
    WorkUnitSupportedFileTypes() {
      return WorkUnitSupportedFileTypes;
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

        if (CSVSupportedFileTypes.includes(this.batchJob.file_type)) {
          this.previewData.CSV.selectedColumns = configs.selected_headers ?? [];
        }

        if (PDFModeSupportedFileTypes.includes(this.batchJob.file_type)) {
          this.previewData.PDF.selectedMode = configs.pdf_mode ?? 'text';
          this.previewData.PDF.supportedMode = await fetchPDFSupportedModeAPI();
        }

      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.fetchBatchJobDetail}`);
        this.handleMessages("error", errorMessage);
      } finally {
        this.loadingState.loading = false;
      }
    },

    async fetchPreviewData() {
      try {
        this.previewData.fetchData = [];
        this.previewData.fetchData = await fetchPreviewAPI(this.batch_id);

      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.loadPreview}`);
        this.handleMessages("error", errorMessage);
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
        'pdf_mode': this.previewData.PDF.selectedMode,
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
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.updatedConfigs}`);
        this.handleMessages("error", errorMessage);
      } finally {
        this.loadingSave = false;
      }

    },

    goToNextStep() {
      this.$router.push(getStepLink(4, this.batch_id));
    },
  },
  async mounted() {
    await this.fetchBatchJob();
    await this.fetchPreviewData();
  },
};
</script>
