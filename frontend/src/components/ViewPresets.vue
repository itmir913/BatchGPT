<template>
  <div class="container mt-5">
    <!-- 진행 상태 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <!-- 메시지 표시 -->
    <div v-if="messages.success" class="alert alert-success text-center mt-4" role="alert">{{ messages.success }}</div>
    <div v-if="messages.error" class="alert alert-danger text-center mt-4" role="alert">{{ messages.error }}</div>

  </div>
</template>


<script>
import ProgressIndicator from "@/components/batch-job/components/ProgressIndicator.vue";

const API_BASE_URL = "/api/batch-jobs/";
const SUCCESS_MESSAGES = {};
const ERROR_MESSAGES = {};

export default {
  props: ['batch_id'],
  components: {ProgressIndicator},
  data() {
    return {
      currentStep: 3,
      batchJob: null,
      loadingState: {loading: true},
      messages: {success: null, error: null},
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

    goToNextStep() {
      this.$router.push(`/batch-jobs/${this.batch_id}/run`);
    },
  },
  mounted() {
    this.fetchBatchJob();
  },
};
</script>


<style scoped>
.container {
  max-width: 1000px;
}
</style>