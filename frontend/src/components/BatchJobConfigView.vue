<template>
  <div class="container mt-5">
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-if="isReady" class="mb-4">
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
          <div v-for="unit in [1, 2, 4, 8]" :key="unit" class="form-check me-3">
            <input id="work_unit{{ unit }}"
                   v-model.number="work_unit" :value="unit"
                   class="form-check-input" type="radio"/>
            <label :for="'work_unit' + unit" class="form-check-label">{{ unit }}</label>
          </div>
          <div class="input-group w-25">
            <span class="input-group-text">Custom Units:</span>
            <input v-model.number="work_unit" class="form-control" min="1" placeholder="Unit" type="number"/>
          </div>
        </div>

        <div class="text-info">
          Each time a request is made to GPT, it processes items in groups of {{ work_unit }} items.
        </div>
        <div class="text-dark">
          A total of {{ totalRequests }} requests will be processed.
        </div>
        <div v-if="remainder !== 0" class="text-danger">
          There are {{ remainder }} items left to process with the last request.
        </div>
        <div v-if="work_unit > batchJob.total_size" class="text-bg-danger">
          The {{ work_unit }} work unit cannot exceed the total size.
        </div>
      </div>

      <!-- GPT Model Selection -->
      <div class="mb-4">
        <h3 class="text-center">Select GPT Model</h3>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
          <div v-for="(model, key) in models" :key="key" class="col-md-4">
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
      <div v-if="success && !error" class="alert alert-success text-center mt-4" role="alert">{{ success }}</div>
      <div v-if="error" class="alert alert-danger text-center mt-4" role="alert">{{ error }}</div>

      <!-- Action Buttons -->
      <div class="text-end mb-4 mt-3">
        <button :disabled="loadingSave || !prompt.trim()" class="btn btn-primary me-3" @click="configSave">Save</button>
        <button :disabled="loadingSave || canNext" class="btn btn-success" @click="goToNextStep">Next</button>
      </div>
    </div>
  </div>
</template>


<script>
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';

export default {
  props: ['batch_id'],
  components: {
    ProgressIndicator,
  },
  data() {
    return {
      currentStep: 2,
      batchJob: null,

      loading: true,
      error: null,
      success: null,

      loadingSave: false,

      work_unit: 1,
      prompt: '',
      gpt_model: 'gpt-4o-mini',  // 기본 모델
      models: { // 모델 딕셔너리
        'gpt-3.5-turbo': 'GPT-3.5 Turbo',
        'gpt-4': 'GPT-4',
        'gpt-4o': 'GPT-4o',
        'gpt-4o-mini': 'GPT-4o Mini'
      },
    };
  },
  computed: {
    remainder() {
      return this.batchJob?.total_size % this.work_unit;
    },
    isReady() {
      return !this.loading && this.batchJob;
    },
    totalRequests() {
      return this.batchJob ? Math.ceil(this.batchJob.total_size / this.work_unit) : 0;
    },
    canNext() {
      const config = this.batchJob.config ?? {};
      return Object.keys(config).length === 0;
    },
  },
  methods: {
    clearMessages() {
      this.success = null;
      this.error = null;
    },

    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/configs/`, {
          withCredentials: true,
        });

        if (!response.data) {
          this.error = "No data received from Server.";
          this.success = null;
          this.batchJob = null;
          return;
        }

        this.batchJob = response.data;
        const config = this.batchJob.config ?? {};
        this.work_unit = config.work_unit ?? 1;
        this.prompt = config.prompt ?? '';
        this.gpt_model = config.gpt_model ?? 'gpt-4o-mini';

      } catch (error) {
        console.error("Error fetching Batch Job:", error);
        this.error = "Failed to load Batch Job details. Please try again later.";
        this.success = null;
      } finally {
        this.loading = false;
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
        work_unit: this.work_unit,
        prompt: this.prompt,
        gpt_model: this.gpt_model,
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
        this.work_unit = config.work_unit ?? 1;
        this.prompt = config.prompt ?? '';
        this.gpt_model = config.gpt_model ?? 'gpt-4o-mini';

        this.success = "Configuration updated successfully.";
      } catch (err) {
        this.error = `Error updating configuration: ${err.message}`;
      } finally {
        this.loadingSave = false;
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
  font-size: 0.9rem; /* 폰트 크기 조정 */
}

.card:hover {
  transform: scale(1.05); /* 클릭 시 확대 효과 */
}

.card-body {
  padding: 1.25rem; /* 카드 내부 여백 조정 */
}

.card.selected {
  border: 2px solid #007bff; /* 선택된 카드 강조 */
}

.row {
  padding: 20px; /* 여백을 줄여줍니다 */
  overflow-x: hidden; /* 좌우 스크롤 방지 */
}
</style>


