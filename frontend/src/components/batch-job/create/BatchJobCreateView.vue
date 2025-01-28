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
        <div v-if="formStatus.isLoading" class="text-center">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>{{ formStatus.loadingMessage }}</p>
        </div>

        <!-- 배치 작업 폼 -->
        <h2 class="mb-3">Create a New Batch Job</h2>
        <div class="card">
          <div class="card-body">
            <!-- Form 시작 -->
            <form @submit.prevent="createBatchJob">
              <!-- 하위 컴포넌트 사용 -->
              <BatchJobInputFields
                  :batchJob="batchJob"
                  :isTitleInvalid="formStatus.isCreateButtonDisabled"
                  @update:batchJob="batchJob = $event"
              />
              <!-- Submit 버튼 -->
              <button :disabled="formStatus.isFormDisabled || loadingState.submitted" class="btn btn-primary"
                      type="submit">
                Create Batch Job
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from '@/components/batch-job/common/ProgressIndicator.vue';
import BatchJobInputFields from '@/components/batch-job/create/InputBatchJobTitleFields.vue';
import {createBatchJobAPI} from "@/components/batch-job/utils/BatchJobUtils";
import ToastView from "@/components/batch-job/common/ToastView.vue";

const SUCCESS_MESSAGES = {
  createBatchJob: "Batch Job created successfully!",
};

const ERROR_MESSAGES = {
  createBatchJob: "Failed to create Batch Job. Please try again later.",
};

export default {
  components: {ToastView, ProgressIndicator, BatchJobInputFields},
  data() {
    return {
      batch_id: 0,
      batchJob: {title: "", description: ""},
      loadingState: {loading: false, submitted: false},
      messages: {success: null, error: null},
    };
  },
  computed: {
    formStatus() {
      return {
        isFormDisabled: !this.batchJob.title || this.loadingState.loading,
        isCreateButtonDisabled: !this.batchJob.title && this.loadingState.submitted,
        isLoading: this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
      };
    },
  },
  methods: {
    clearMessages() {
      this.messages.success = null;
      this.messages.error = null;
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();

      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.loadingState.error = type === "error" ? fullMessage : null;
      this.loadingState.success = type === "success" ? fullMessage : null;
    },

    async createBatchJob() {
      if (this.loadingState.submitted) return;
      this.loadingState.submitted = true;

      if (this.formStatus.isFormDisabled) return;

      try {
        this.clearMessages();

        const payload = {
          'title': this.batchJob.title,
          'description': this.batchJob.description,
        };

        const {batch_id} = await createBatchJobAPI(payload);
        this.batch_id = batch_id;

        this.handleMessages("success", SUCCESS_MESSAGES.createBatchJob);

        setTimeout(() => {
          this.$router.push(`/batch-jobs/${this.batch_id}/`);
        }, 1000);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.createBatchJob} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.createBatchJob} No response received.`);
        }
        this.loadingState.submitted = false;
      }
    },
  },
};
</script>

<style scoped>
</style>