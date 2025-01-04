<template>
  <div class="container mt-5">

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center mb-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="error" class="alert alert-danger text-center mb-4" role="alert">
      {{ error }}
    </div>

    <!-- 5단계 워크플로우 표시 -->
    <ProgressIndicator v-if="batchJob && isReady" :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 파일 정보 표시 -->
    <div v-if="batchJob && isReady" class="mb-4">
      <h5>Uploaded File</h5>
      <div class="table-responsive mb-4">
        <table class="table table-striped table-bordered">
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

        <!-- 프롬프트 입력란 -->
        <div v-if="isReady" class="mb-4">
          <h5>Input Prompt</h5>
          <textarea
              v-model="prompt"
              class="form-control"
              placeholder="Enter your prompt..."
              rows="5"
          ></textarea>
        </div>

        <!-- 작업 단위 설정 -->
        <div v-if="batchJob && isReady">
          <div class="mb-4">
            <h5 class="text-center mt-4 mb-2">Select Number of Items per Task</h5>
            <div class="d-flex justify-content-center align-items-center mb-2">
              <div class="form-check me-3">
                <input id="workUnit1" v-model.number="workUnit" class="form-check-input" type="radio" value="1"/>
                <label class="form-check-label" for="workUnit1">1</label>
              </div>
              <div class="form-check me-3">
                <input id="workUnit2" v-model.number="workUnit" class="form-check-input" type="radio" value="2"/>
                <label class="form-check-label" for="workUnit2">2</label>
              </div>
              <div class="form-check me-3">
                <input id="workUnit4" v-model.number="workUnit" class="form-check-input" type="radio" value="4"/>
                <label class="form-check-label" for="workUnit4">4</label>
              </div>
              <div class="form-check me-3">
                <input id="workUnit8" v-model.number="workUnit" class="form-check-input" type="radio" value="8"/>
                <label class="form-check-label" for="workUnit8">8</label>
              </div>

              <!-- 사용자 입력 필드 -->
              <div class="input-group w-25">
                <span class="input-group-text">Custom Units:</span>
                <input v-model.number="workUnit" class="form-control" min="1" placeholder="Unit" type="number"/>
              </div>
            </div>

            <!-- 안내 메시지 -->
            <div class="text-info">
              Each time a request is made to GPT, it processes items in groups of {{ workUnit }} items.
            </div>

            <div class="text-dark">
              A total of {{ calculateCeil(batchJob.total_size, workUnit) }} requests will be processed.
            </div>

            <!-- 경고 메시지 -->
            <div v-if="remainder !== 0" class="text-danger">
              There are {{ remainder }} items left to process with the last request.
            </div>
            <div v-if="workUnit > batchJob.total_size" class="text-bg-danger">
              The {{ workUnit }} work unit cannot exceed the total size.
            </div>
          </div>
        </div>

        <!-- 버튼을 별도의 div로 감싸고 정렬 -->
        <div class="text-end mb-4 mt-3">
          <button :disabled="loadingSave" class="btn btn-primary me-3" @click="configSave">Save</button>
          <button :disabled="isDisabledNext" class="btn btn-success" @click="goToNextStep">Next</button>
        </div>

      </div>
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
      currentStep: 2, // 현재 진행 중인 단계 (0부터 시작)
      batchJob: null, // 배치 작업 데이터
      loading: true, // 로딩 상태
      error: null, // 에러 메시지
      workUnit: 1,
      prompt: '',
      loadingSave: false,
      isDisabledNext: true,
    };
  },
  computed: {
    remainder() {
      return this.batchJob.total_size % this.workUnit;
    },
    isReady() {
      return !this.loading && !this.error;
    },
  },
  methods: {
    // 배치 작업 데이터 가져오기
    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/configs/`, {
          withCredentials: true,
        });
        this.batchJob = response.data;

        const config = this.batchJob.config ?? {}

        this.workUnit = config.workUnit ?? 1
        this.prompt = config.prompt ?? ''

        if (this.prompt !== '') {
          this.isDisabledNext = false;
        }

      } catch (error) {
        console.error("Error fetching Batch Job:", error);
        this.error = "Failed to load Batch Job details. Please try again later.";
      } finally {
        this.loading = false;
      }
    },

    async configSave() {
      this.loadingSave = true; // 로딩 상태 설정
      this.error = null; // 이전 오류 초기화

      if (this.workUnit > this.batchJob.total_size) {
        alert('The work unit cannot exceed the total size.');
        this.loadingSave = false;
        return;
      }

      if (!this.prompt.trim()) {
        alert('Prompt cannot be empty. Please enter a valid prompt.');
        this.loadingSave = false;
        return;
      }

      const payload = {
        workUnit: this.workUnit,
        prompt: this.prompt,
      };

      try {
        await axios.patch(`/api/batch-jobs/${this.batch_id}/configs/`, payload);
        // 성공적인 응답 처리
        alert('Configuration updated successfully.');
        this.isDisabledNext = false;
      } catch (err) {
        // 오류 처리
        this.error = err.response ? err.response.data : 'An error occurred';
        alert('Error updating configuration: ' + this.error);
      } finally {
        this.loadingSave = false; // 로딩 상태 해제
      }
    },

    goToNextStep() {
      // 다음 단계로 이동하는 로직 구현
      this.$router.push(`/batch-jobs/${this.batch_id}/preview`);
    },

    calculateCeil(totalSize, workUnit) {
      return Math.ceil(totalSize / workUnit);
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

.table th, .table td {
  vertical-align: middle;
}
</style>