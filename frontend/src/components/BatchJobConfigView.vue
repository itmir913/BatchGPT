<template>
  <div class="container mt-5">
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <div v-if="formStatus.isReady" class="mb-4">
      <h3>Uploaded File</h3>
      <table class="table table-striped table-bordered table-responsive mb-4">
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
      <div class="mb-4">
        <h3 class="text-center mt-4 mb-2">Select Number of Items per Task</h3>
        <div class="d-flex justify-content-center align-items-center mb-2">
          <div v-for="unit in [1, 2, 4, 8]" :key="'unit-' + unit" class="form-check me-3">
            <input id="work_unit{{ unit }}" v-model.number="work_unit" :disabled="workUnit.isWorkUnitDisabled"
                   :value="unit"
                   class="form-check-input" type="radio"/>
            <label :for="'work_unit' + unit" class="form-check-label">{{ unit }}</label>
          </div>
          <div class="input-group w-25">
            <span class="input-group-text">Custom Units:</span>
            <input v-model.number="work_unit" :disabled="workUnit.isWorkUnitDisabled" class="form-control" min="1"
                   placeholder="Unit" type="number"/>
          </div>
        </div>

        <div class="text-info">
          Each time a request is made to GPT, it processes items in groups of {{ work_unit }} items.
        </div>
        <div class="text-dark">
          A total of {{ workUnit.totalRequests }} requests will be processed.
        </div>
        <div v-if="workUnit.isWorkUnitDisabled" class="text-success">
          This option is disabled as the current file type does not support it.
        </div>
        <div v-if="workUnit.remainder !== 0" class="text-danger">
          There are {{ workUnit.remainder }} items left to process with the last request.
        </div>
        <div v-if="work_unit > batchJob.total_size" class="text-bg-danger">
          The {{ work_unit }} work unit cannot exceed the total size.
        </div>
      </div>

      <!-- GPT Model Selection -->
      <div class="mb-4">
        <h3 class="text-center">Select GPT Model</h3>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
          <div v-for="(model, key) in models" :key="'model-' + key" class="col-md-4">
            <div :class="{'border-primary': gpt_model === key}" class="card shadow-sm clickable-card"
                 @click="gpt_model = key">
              <div class="card-body d-flex flex-column justify-content-center text-center">
                <input id="model" v-model="gpt_model" :value="key" class="form-check-input" style="display: none;"
                       type="radio"/>
                <label :for="key" class="form-check-label">{{ model }}</label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Prompt Input Section -->
      <div class="mb-4 g-4 p-3">
        <h3>Input Prompt</h3>
        <textarea v-model="prompt" class="form-control" placeholder="Enter your prompt..." rows="5"></textarea>
      </div>

      <!-- Success/Failure Message -->
      <div v-if="messages.success" class="alert alert-success text-center mt-4" role="alert">
        {{ messages.success }}
      </div>
      <div v-if="messages.error" class="alert alert-danger text-center mt-4" role="alert">{{ messages.error }}</div>

      <!-- Action Buttons -->
      <div class="text-end mb-4 mt-3">
        <button :disabled="formStatus.isSaveButtonDisabled" class="btn btn-primary me-3" @click="configSave">
          Save
        </button>
        <button :disabled="formStatus.isNextButtonDisabled" class="btn btn-success"
                @click="goToNextStep">Next
        </button>
      </div>
    </div>

  </div>
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';

// 상수화 가능한 값 정의
const API_BASE_URL = "/api/batch-jobs/";
const API_CONFIG_URL = "configs/";

const DEFAULT_GPT_MODEL = 'gpt-4o-mini';

const SUCCESS_MESSAGES = {
  saveConfigSuccess: "Configuration updated successfully.",
};

const ERROR_MESSAGES = {
  fetchBatchJobError: "Failed to load Batch Job details. Please try again later.",
  saveConfigError: "Error updating configuration: ",
};

export default {
  props: ['batch_id'],
  components: {
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
    workUnit() {
      return {
        totalRequests: this.batchJob ? Math.ceil(this.batchJob.total_size / this.work_unit) : 0,
        remainder: this.batchJob.total_size % this.work_unit,
        isWorkUnitDisabled: this.batchJob.file_type !== 'pdf',
      }
    },

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
        const response = await axios.get(`${API_BASE_URL}${this.batch_id}/${API_CONFIG_URL}`, {withCredentials: true});
        this.batchJob = response.data;
        if (!response.data) {
          this.handleMessages("error", ERROR_MESSAGES.fetchBatchJobError);
          return;
        }

        const config = this.batchJob.config ?? {};
        this.work_unit = config.work_unit ?? 1;
        this.prompt = config.prompt ?? '';
        this.gpt_model = config.gpt_model ?? DEFAULT_GPT_MODEL;
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.fetchBatchJobError);
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
          this.handleMessages("error", ERROR_MESSAGES.fetchBatchJobError);
          return;
        }

        const config = this.batchJob.config ?? {};
        this.work_unit = config.work_unit ?? 1;
        this.prompt = config.prompt ?? '';
        this.gpt_model = config.gpt_model ?? DEFAULT_GPT_MODEL;

        this.handleMessages("success", SUCCESS_MESSAGES.saveConfigSuccess);
      } catch (err) {
        this.handleMessages("error", `${ERROR_MESSAGES.saveConfigError} ${err.message}`);
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
