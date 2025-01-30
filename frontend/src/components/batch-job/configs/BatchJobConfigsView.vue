<template>
  <div class="container my-4">
    <ToastView
        ref="toast"
        :message="messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator :batch_id="batch_id" :currentStep="2"/>
      </div>

      <div class="col-md-9">
        <!-- 로딩 상태 -->
        <LoadingView v-if="formStatus.isLoading"/>

        <div v-if="formStatus.isReady" class="p-2 mb-3">
          <h2 class="mb-3">Uploaded File</h2>
          <table class="table table-striped table-bordered table-responsive mb-3">
            <thead class="table-light">
            <tr>
              <th style="width: 30%;">Item</th>
              <th style="width: 70%;">Information</th>
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

          <!-- GPT Model Selection -->
          <GPTModelSelector
              :available_models="available_models"
              :disabled="batchJobStatus.isEditable"
              :gpt_model="gpt_model"
              @update:gpt_model="gpt_model = $event"
          />

          <!-- Action Buttons -->
          <div class="text-end my-3">
            <button :disabled="formStatus.isSaveButtonDisabled || batchJobStatus.isEditable"
                    class="btn btn-primary me-3"
                    @click="configSave">
              Save
            </button>
            <button :disabled="formStatus.isNextButtonDisabled"
                    class="btn btn-success"
                    @click="goToNextStep">
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from '@/components/batch-job/common/ProgressIndicator.vue';
import {
  ERROR_MESSAGES,
  fetchBatchJobConfigsAPI,
  modifyBatchJobConfigsAPI,
  shouldEditDisabled,
  SUCCESS_MESSAGES
} from '@/components/batch-job/utils/BatchJobUtils';
import {DEFAULT_GPT_MODEL, MODELS} from "@/components/batch-job/utils/GPTUtils";
import GPTModelSelector from "@/components/batch-job/configs/GPTModelSelector.vue";
import ToastView from "@/components/batch-job/common/ToastView.vue";
import LoadingView from "@/components/batch-job/common/LoadingView.vue";

export default {
  props: ['batch_id'],
  components: {
    LoadingView,
    ToastView,
    GPTModelSelector,
    ProgressIndicator,
  },
  data() {
    return {
      batchJob: null,

      loadingState: {loading: true, loadingSave: false},
      messages: {success: null, error: null},

      work_unit: 1,
      gpt_model: DEFAULT_GPT_MODEL,
      available_models: MODELS,
    };
  },
  computed: {
    formStatus() {
      return {
        isLoading: this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
        isReady: !this.loadingState.loading && this.batchJob,
        isNextButtonDisabled: !!(this.batchJob && this.batchJob.config &&
            Object.keys(this.batchJob.config).length === 0 && !this.loadingState.loadingSave),
        isSaveButtonDisabled: this.loadingState.loadingSave,
      };
    },
    batchJobStatus() {
      return {
        isEditable: shouldEditDisabled(this.batchJob?.batch_job_status),
      };
    },
  },
  methods: {
    clearMessages() {
      this.messages.success = null;
      this.messages.error = null;
    },

    handleMessages(type, message) {
      this.clearMessages();
      if (type === "error") {
        this.messages.error = message;
      } else if (type === "success") {
        this.messages.success = message;
      }
    },

    async fetchBatchJob() {
      try {
        this.loadingState.loading = true;

        const {batchJob, configs} = await fetchBatchJobConfigsAPI(this.batch_id);
        this.batchJob = batchJob;
        this.work_unit = configs.work_unit ?? 1;
        this.gpt_model = configs.gpt_model ?? DEFAULT_GPT_MODEL;

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

    async configSave() {
      if (this.work_unit > this.batchJob.total_size) {
        return this.handleMessages("error", "The work unit cannot exceed the total size.");
      }

      try {
        this.loadingState.loadingSave = true;

        const payload = {
          work_unit: this.work_unit,
          gpt_model: this.gpt_model,
        };

        const {batchJob, configs} = await modifyBatchJobConfigsAPI(this.batch_id, payload);
        this.batchJob = batchJob;

        if (!this.batchJob) {
          this.handleMessages("error", ERROR_MESSAGES.fetchBatchJob);
          return;
        }

        this.work_unit = configs.work_unit ?? 1;
        this.gpt_model = configs.gpt_model ?? DEFAULT_GPT_MODEL;

        this.handleMessages("success", SUCCESS_MESSAGES.updatedConfigs);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.updatedConfigs} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.updatedConfigs} No response received.`);
        }
      } finally {
        this.loadingState.loadingSave = false;
      }
    },

    goToNextStep() {
      this.$router.push(`/batch-jobs/${this.batch_id}/preview`);
    },
  },
  async created() {
    await this.fetchBatchJob();
  },
};
</script>

<style scoped>
.table-responsive {
  overflow-x: auto;
}

.table th, .table td {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
