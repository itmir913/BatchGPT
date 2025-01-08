<template>
  <div class="container mt-4">
    <!-- 5단계 워크플로우 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="1"/>

    <!-- 로딩 상태 -->
    <div v-if="formStatus.isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>{{ formStatus.loadingMessage }}</p>
    </div>

    <!-- 메시지 표시 -->
    <div v-if="messages.success" class="alert alert-success text-center mt-3" role="alert">{{ messages.success }}</div>
    <div v-if="messages.error" class="alert alert-danger text-center mt-3" role="alert">{{ messages.error }}</div>

    <!-- 배치 작업 상세 정보 -->
    <div v-if="formStatus.isReady" class="card mt-3">
      <div class="card-body">
        <h2 class="card-title">{{ batchJob.title }}</h2>
        <p class="card-text">{{ batchJob.description || "No description provided." }}</p>
        <p class="card-text text-muted">
          Created At: {{ formatDate(batchJob.created_at) }}<br/>
          Updated At: {{ formatDate(batchJob.updated_at) }}
        </p>

        <!-- 파일 업로드 섹션 -->
        <div class="mt-3">
          <h5>File Upload</h5>
          <form class="d-flex align-items-center gap-3" @submit.prevent="uploadFile">
            <input
                ref="fileInput"
                :disabled="batchJobStatus.isEditDisabled"
                class="form-control flex-grow-1"
                type="file"
                @change="handleFileChange"
            />
            <button
                :disabled="formStatus.isUploading || batchJobStatus.isEditDisabled"
                class="btn btn-primary"
                style="white-space: nowrap;"
                type="submit"
            >
              {{ formStatus.isUploading ? "Uploading..." : "Upload File" }}
            </button>
          </form>
        </div>

        <!-- 업로드된 파일 정보 -->
        <div v-if="batchJob.file_name" class="mt-3">
          <h5>Uploaded File</h5>
          <h6>{{ batchJob.file_name }}</h6>
        </div>

        <!-- 하단 버튼 추가 -->
        <div class="d-flex justify-content-between mt-3">
          <div>
            <button class="btn btn-danger" @click="deleteBatchJob">Delete</button>
            <button class="btn btn-secondary ms-2" @click="editBatchJob">Edit</button>
          </div>
          <button
              :disabled="formStatus.isNextButtonDisabled"
              class="btn btn-success"
              @click="goToNextStep"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressIndicator from "@/components/batch-job/components/ProgressIndicator.vue";
import {
  deleteBatchJobTitleAPI,
  ERROR_MESSAGES,
  fetchBatchJobTitleAPI,
  fetchFileTypesAPI,
  isEditDisabled,
  SUCCESS_MESSAGES,
  uploadFilesAPI
} from '@/components/batch-job/utils/batchJobUtils';

export default {
  props: ["batch_id"],
  components: {ProgressIndicator},
  data() {
    return {
      batchJob: null,
      allowedFileTypes: [],
      selectedFile: null,

      loadingState: {loading: true, uploading: false},
      messages: {success: null, error: null},
    };
  },
  computed: {
    // 버튼 상태와 로딩 상태를 하나로 관리
    formStatus() {
      return {
        isNextButtonDisabled: !this.batchJob || !this.batchJob.file_name,
        isUploading: this.loadingState.uploading,
        isLoading: this.loadingState.loading,
        isReady: !this.loadingState.loading,
        loadingMessage: this.loadingState.loading ? "Please wait while we load the data..." : "",
      };
    },
    batchJobStatus() {
      return {
        isEditDisabled: isEditDisabled(this.batchJob.batch_job_status)
      };
    },
  },
  methods: {
    // 메시지 처리 함수
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

    async fetchBatchJob() {
      try {
        this.loadingState.loading = true;

        this.batchJob = await fetchBatchJobTitleAPI(this.batch_id);
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.fetchBatchJob);
      } finally {
        this.loadingState.loading = false;
      }
    },

    async fetchFileTypes() {
      try {
        this.allowedFileTypes = await fetchFileTypesAPI();
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.fileTypes);
      }
    },

    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },

    validateFile() {
      if (!this.selectedFile) {
        return "Please select a file to upload.";
      }
      const fileExtension = this.selectedFile.name.split(".").pop().toLowerCase();
      if (!this.allowedFileTypes.includes(fileExtension)) {
        return `Unsupported file type. Please upload one of the following: ${this.allowedFileTypes.join(", ")}`;
      }
      return null;
    },

    async uploadFile() {
      const errorMessage = this.validateFile();
      if (errorMessage) {
        return this.handleMessages("error", errorMessage);
      }

      try {
        this.loadingState.uploading = true;
        this.batchJob = await uploadFilesAPI(this.batchJob, this.selectedFile);
        this.handleMessages("success", SUCCESS_MESSAGES.uploadFile);
      } catch (error) {
        this.handleMessages("error", `${ERROR_MESSAGES.uploadFile} ${error.response.data?.error || "Unknown error occurred."}`);
      } finally {
        this.loadingState.uploading = false;
        this.resetFileInput();
      }
    },

    resetFileInput() {
      this.selectedFile = null;
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = "";
      }
    },

    editBatchJob() {
      this.$router.push(`/batch-jobs/${this.batch_id}/edit`);
    },

    async deleteBatchJob() {
      if (confirm("Are you sure you want to delete this batch job?")) {
        try {
          await deleteBatchJobTitleAPI();
          alert(SUCCESS_MESSAGES.deleteBatchJob);
          this.$router.push(`/home`);
        } catch (error) {
          this.handleMessages("error", `${ERROR_MESSAGES.deleteBatchJob} ${error.response.data?.error || "Unknown error occurred."}`);
        }
      }
    },

    goToNextStep() {
      if (!this.batchJob.file_name) {
        return this.handleMessages("error", ERROR_MESSAGES.missingFile);
      }
      this.$router.push(`/batch-jobs/${this.batch_id}/configs`);
    },

    formatDate(dateString) {
      const options = {year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "numeric"};
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },

  mounted() {
    this.fetchBatchJob();
    this.fetchFileTypes();
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>
