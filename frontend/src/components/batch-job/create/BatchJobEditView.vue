<template>
  <div class="container my-4">
    <ToastView
        ref="toast"
        :message="messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator :batch_id="batch_id" :currentStep="0"/>
      </div>

      <div class="col-md-9">
        <!-- 로딩 상태 -->
        <LoadingView v-if="loading"/>

        <!-- 배치 작업 폼 -->
        <h2 class="mb-3">Modify Batch Job</h2>
        <div v-if="batchJob && isReady" class="card">
          <div class="card-body">
            <form @submit.prevent="modifyBatchJob">
              <!-- 하위 컴포넌트 사용 -->
              <BatchJobInputFields
                  :batchJob="batchJob"
                  :isTitleInvalid="formStatus.isCreateButtonDisabled"
                  @update:batchJob="batchJob = $event"
              />
              <!-- 버튼 -->
              <div class="d-flex justify-content-end mt-3">
                <button class="btn btn-secondary me-2" @click="cancelButton">Cancel</button>
                <button :disabled="isButtonDisabled" class="btn btn-primary" type="submit">Edit Batch Job</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from '@/components/batch-job/common/ProgressIndicator.vue';
import BatchJobInputFields from "@/components/batch-job/create/InputBatchJobTitleFields.vue";
import {
  ERROR_MESSAGES,
  fetchBatchJobTitleAPI,
  getStepLink,
  modifyBatchJobTitleAPI,
  SUCCESS_MESSAGES
} from "@/components/batch-job/utils/BatchJobUtils";
import ToastView from "@/components/batch-job/common/ToastView.vue";
import LoadingView from "@/components/batch-job/common/LoadingSpinner.vue";
import {getErrorMessage} from "@/components/batch-job/utils/CommonFunctions";

export default {
  components: {
    LoadingView,
    ToastView,
    BatchJobInputFields,
    ProgressIndicator,
  },
  props: ['batch_id'],
  data() {
    return {
      batchJob: null, // 배치 작업 초기값

      messages: {success: null, error: null},

      loading: false, // 로딩 상태
      isButtonDisabled: true, // 버튼 비활성화 여부
    };
  },
  computed: {
    isReady() {
      return !this.loading;
    },

    formStatus() {
      return {
        isCreateButtonDisabled: !this.batchJob.title,
      };
    },
  },
  methods: {
    // 배치 작업 데이터를 가져오는 메서드
    async fetchBatchJob() {
      try {
        this.batchJob = await fetchBatchJobTitleAPI(this.batch_id);
        this.isButtonDisabled = false;
      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.fetchBatchJobDetail}`);
        this.handleMessages("error", errorMessage);
      }
    },

    // 배치 작업 수정 처리
    async modifyBatchJob() {
      try {
        this.isButtonDisabled = true;

        const payload = {
          'title': this.batchJob.title,
          'description': this.batchJob.description,
        };

        await modifyBatchJobTitleAPI(this.batch_id, payload);

        this.handleMessages("success", SUCCESS_MESSAGES.modifyBatchJob);

        // 수정 후 자동으로 배치 작업 상세 페이지로 리다이렉트
        setTimeout(() => {
          this.$router.push(getStepLink(1, this.batch_id));
        }, 1000);

      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.modifyBatchJob}`);
        this.handleMessages("error", errorMessage);
        this.isButtonDisabled = false;
      }
    },

    clearMessages() {
      this.messages = {success: null, error: null};
    },

    handleMessages(type, message) {
      this.clearMessages();
      this.messages[type] = message;
    },

    // 취소 버튼 처리
    cancelButton() {
      this.$router.push(getStepLink(1, this.batch_id));
    },
  },

  // 컴포넌트 마운트 후 배치 작업 데이터 가져오기
  mounted() {
    this.fetchBatchJob();
  },
};
</script>
