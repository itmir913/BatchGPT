<template>
  <div class="container mt-4">
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <div v-if="formStatus.isReady" class="p-2 mb-3">
      <h3>Uploaded File</h3>
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

      <!-- Work Unit Selection Section -->
      <div class="p-2 mb-3">
        <WorkUnitSettings
            :batchJob="batchJob"
            :isReady="formStatus.isReady"
            :work_unit="work_unit"
            :disabled="batchJobStatus.isEditDisabled"
        />
      </div>

      <!-- GPT Model Selection -->
      <div class="p-2 mb-3">
        <h3 class="text-center">Select GPT Model</h3>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
          <div v-for="(model, key) in models" :key="'model-' + key" class="col-md-4">
            <div :class="{'border-primary': gpt_model === key}" class="card shadow-sm clickable-card"
                 @click="gpt_model = key">
              <div class="card-body d-flex flex-column justify-content-center text-center">
                <input id="model" v-model="gpt_model" :value="key" class="form-check-input" style="display: none;"
                       :disabled="batchJobStatus.isEditDisabled"
                       type="radio"/>
                <label :for="key" class="form-check-label">{{ model }}</label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Prompt 컴포넌트 -->
      <InputPrompt
          :disabled="batchJobStatus.isEditDisabled"
          :prompt="prompt"
          @update:prompt="(newPrompt) => (prompt = newPrompt)"
      />

      <!-- Success/Failure Message -->
      <div v-if="messages.success" class="alert alert-success text-center mt-3" role="alert">
        {{ messages.success }}
      </div>
      <div v-if="messages.error" class="alert alert-danger text-center mt-3" role="alert">{{ messages.error }}</div>

      <!-- Action Buttons -->
      <div class="text-end mt-3">
        <button :disabled="formStatus.isSaveButtonDisabled || batchJobStatus.isEditDisabled"
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
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/batch-job/components/ProgressIndicator.vue';
import WorkUnitSettings from "@/components/batch-job/components/WorkUnitSettings.vue";
import {
  DEFAULT_GPT_MODEL,
  ERROR_MESSAGES,
  fetchBatchJobConfigsAPI,
  isEditDisabled,
  SUCCESS_MESSAGES
} from '@/components/batch-job/utils/batchJobUtils';
import InputPrompt from "@/components/batch-job/components/InputPrompt.vue";

// 상수화 가능한 값 정의
const API_BASE_URL = "/api/batch-jobs/";
const API_CONFIG_URL = "configs/";

export default {
  props: ['batch_id'],
  components: {
    InputPrompt,
    WorkUnitSettings,
    ProgressIndicator,
  },
  data() {
    return {
      currentStep: 2,
      batchJob: null,

      loadingState: {loading: true, loadingSave: false},
      messages: {success: null, error: null},

      work_unit: 1,
      prompt: '',
      gpt_model: DEFAULT_GPT_MODEL,
      models: {
        'gpt-3.5-turbo': 'GPT-3.5 Turbo',
        'gpt-4': 'GPT-4',
        'gpt-4o': 'GPT-4o',
        'gpt-4o-mini': 'GPT-4o Mini',
      },
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
        isSaveButtonDisabled: this.loadingState.loadingSave || !this.prompt.trim(),
      };
    },
    batchJobStatus() {
      return {
        isEditDisabled: isEditDisabled(this.batchJob.batch_job_status)
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
        this.prompt = configs.prompt ?? '';
        this.gpt_model = configs.gpt_model ?? DEFAULT_GPT_MODEL;

      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.fetchBatchJob);
      } finally {
        this.loadingState.loading = false;
      }
    },

    async configSave() {
      if (this.work_unit > this.batchJob.total_size) {
        return this.handleMessages("error", "The work unit cannot exceed the total size.");
      }

      if (!this.prompt.trim()) {
        return this.handleMessages("error", "Prompt cannot be empty.");
      }

      try {
        this.loadingState.loadingSave = true;

        const payload = {
          work_unit: this.work_unit,
          prompt: this.prompt,
          gpt_model: this.gpt_model,
        };

        const response = await axios.patch(`${API_BASE_URL}${this.batch_id}/${API_CONFIG_URL}`, payload);
        this.batchJob = response.data;

        if (!response.data) {
          this.handleMessages("error", ERROR_MESSAGES.fetchBatchJob);
          return;
        }

        const config = this.batchJob.config ?? {};
        this.work_unit = config.work_unit ?? 1;
        this.prompt = config.prompt ?? '';
        this.gpt_model = config.gpt_model ?? DEFAULT_GPT_MODEL;

        this.handleMessages("success", SUCCESS_MESSAGES.updatedConfigs);
      } catch (err) {
        this.handleMessages("error", `${ERROR_MESSAGES.updatedConfigs} ${err.message}`);
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
.container {
  max-width: 1000px;
}

.table-responsive {
  overflow-x: auto;
}

.table th, .table td {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

<!-- GPT 모델 선택 카드 -->
<style scoped>
.card {
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
  font-size: 0.9rem;
}

.card:hover {
  transform: scale(1.05);
}

.card-body {
  padding: 1.25rem;
}

.card.selected {
  border: 2px solid #007bff;
}

.row {
  padding: 20px;
  overflow-x: hidden;
}
</style>
