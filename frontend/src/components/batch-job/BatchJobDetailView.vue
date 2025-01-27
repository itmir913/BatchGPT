<template>
  <div class="container my-4">
    <ToastView
        ref="toast"
        :message="state.messages"
    />

    <div class="row">
      <div class="col-md-3">
        <ProgressIndicator :batch_id="batch_id" :currentStep="1"/>
      </div>

      <div class="col-md-9">
        <!-- Loading State -->
        <div v-if="state.isLoading" class="text-center">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>{{ state.loadingMessage }}</p>
        </div>

        <!-- Batch Job Details -->
        <div v-if="!state.isLoading && batchJob" class="card mt-3">
          <div class="card-body">
            <h2 class="card-title">{{ batchJob.title }}</h2>
            <p class="card-text">{{ batchJob.description || "No description provided." }}</p>
            <p class="card-text text-muted">
              Created At: {{ formatDate(batchJob.created_at) }}<br/>
              Updated At: {{ formatDate(batchJob.updated_at) }}
            </p>

            <!-- File Upload Section -->
            <div class="mt-3">
              <h5>File Upload</h5>
              <form class="d-flex align-items-center gap-3" @submit.prevent="uploadFile">
                <input
                    ref="fileInput"
                    :disabled="!state.isEditable"
                    class="form-control flex-grow-1"
                    type="file"
                    @change="handleFileChange"
                />
                <button
                    :disabled="state.isUploading || !state.isEditable"
                    class="btn btn-primary"
                    style="white-space: nowrap;"
                    type="submit"
                >
                  {{ state.isUploading ? "Uploading..." : "Upload File" }}
                </button>
              </form>
            </div>

            <!-- Uploaded File Info -->
            <div v-if="batchJob.file_name" class="mt-3">
              <h5>Uploaded File</h5>
              <h6>{{ batchJob.file_name }}</h6>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex justify-content-between mt-3">
              <div>
                <button class="btn btn-danger" @click="deleteBatchJob">Delete</button>
                <button class="btn btn-secondary ms-2" @click="editBatchJob">Edit</button>
              </div>
              <button
                  :disabled="!state.isNextEnabled"
                  class="btn btn-success"
                  @click="goToNextStep"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-body {
  padding: 20px;
}

.card-title {
  font-size: 1.5rem;
  font-weight: bold;
}

.card-text {
  font-size: 1rem;
  white-space: pre-line;
}

.mt-3 {
  margin-top: 1rem;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.text-center {
  text-align: center;
}
</style>

<script>
import ProgressIndicator from "@/components/batch-job/components/ProgressIndicator.vue";
import {
  CONFIRM_MESSAGE,
  deleteBatchJobTitleAPI,
  ERROR_MESSAGES,
  fetchBatchJobTitleAPI,
  fetchFileTypesAPI,
  shouldEditDisabled,
  SUCCESS_MESSAGES,
  uploadFilesAPI,
} from "@/components/batch-job/utils/BatchJobUtils";
import ToastView from "@/components/batch-job/components/ToastView.vue";

export default {
  props: ["batch_id"],
  components: {ToastView, ProgressIndicator},
  data() {
    return {
      batchJob: null,
      allowedFileTypes: [],
      selectedFile: null,
      state: {
        isLoading: true,
        isUploading: false,
        isEditable: true,
        isNextEnabled: false,
        loadingMessage: CONFIRM_MESSAGE.loadingMessage,
        messages: {success: null, error: null},
      },
    };
  },
  watch: {
    batchJob(newVal) {
      this.state.isNextEnabled = !!(newVal && newVal.file_name);
      this.state.isEditable = !shouldEditDisabled(newVal?.batch_job_status);
    },
  },
  methods: {
    clearMessages() {
      this.state.messages = {success: null, error: null};
    },

    handleMessages(type, message) {
      this.clearMessages();
      this.state.messages[type] = message;
    },

    async fetchBatchJob() {
      try {
        this.state.isLoading = true;
        this.batchJob = await fetchBatchJobTitleAPI(this.batch_id);
      } catch {
        this.handleMessages("error", ERROR_MESSAGES.fetchBatchJob);
      } finally {
        this.state.isLoading = false;
      }
    },

    async fetchFileTypes() {
      try {
        this.allowedFileTypes = await fetchFileTypesAPI();
      } catch {
        this.handleMessages("error", ERROR_MESSAGES.fileTypes);
      }
    },

    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },

    validateFile() {
      if (!this.selectedFile) return `${ERROR_MESSAGES.missingFile}`;
      const fileExtension = this.selectedFile.name.split(".").pop().toLowerCase();
      if (!this.allowedFileTypes.includes(fileExtension)) {
        return `${ERROR_MESSAGES.unsupportedFileType} ${this.allowedFileTypes.join(", ")}`;
      }
      return null;
    },

    async uploadFile() {
      const errorMessage = this.validateFile();
      if (errorMessage) return this.handleMessages("error", errorMessage);

      try {
        this.state.isUploading = true;
        this.batchJob = await uploadFilesAPI(this.batch_id, this.selectedFile);
        this.handleMessages("success", SUCCESS_MESSAGES.uploadFile);
      } catch (error) {
        this.handleMessages("error", ERROR_MESSAGES.uploadFile);
      } finally {
        this.state.isUploading = false;
        this.resetFileInputHelper();
      }
    },

    resetFileInputHelper() {
      this.selectedFile = null;
      if (this.$refs.fileInput) this.$refs.fileInput.value = "";
    },

    editBatchJob() {
      this.$router.push(`/batch-jobs/${this.batch_id}/edit`);
    },

    async deleteBatchJob() {
      if (!confirm(`${CONFIRM_MESSAGE.deleteBatchJob}`)) return;

      try {
        await deleteBatchJobTitleAPI(this.batch_id);
        alert(SUCCESS_MESSAGES.deleteBatchJob);
        this.$router.push(`/home`);
      } catch {
        this.handleMessages("error", ERROR_MESSAGES.deleteBatchJob);
      }
    },

    goToNextStep() {
      if (!this.batchJob.file_name) {
        this.handleMessages("error", ERROR_MESSAGES.missingFile);
        return;
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
