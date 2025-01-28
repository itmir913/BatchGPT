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
                <div
                    ref="dropZone"
                    :class="{'drag-over': isDragOver}"
                    class="file-upload-dropzone form-control flex-grow-1"
                    @click="triggerFileInputClick"
                    @dragover.prevent="handleDragOver"
                    @dragleave.prevent="handleDragLeave"
                    @drop.prevent="handleDrop"
                >
                  <input
                      ref="fileInput"
                      :disabled="state.isEditable"
                      class="d-none"
                      type="file"
                      @change="handleFileChange"
                      multiple
                  />
                  <span v-if="!selectedFiles">Drag and drop files or click to select</span>
                  <span v-else style="white-space: pre-line;">
                    {{ selectedFiles.map(file => file.name).join(',\n') }}
                  </span>
                </div>

                <button
                    :disabled="state.isUploading || state.isEditable"
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

<style>
.file-upload-dropzone {
  position: relative;
  min-height: 150px;
  height: 150px;
  border: 2px dashed #ccc;
  display: flex !important;
  justify-content: center;
  align-items: center;
  text-align: center;
  transition: background-color 0.3s ease;
}

.file-upload-dropzone span {
  display: block;
  font-size: 16px;
  color: #666;
}

.file-upload-dropzone.drag-over {
  background-color: #e0e0e0;
}
</style>

<script>
import JSZip from 'jszip';
import ProgressIndicator from "@/components/batch-job/common/ProgressIndicator.vue";
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
import ToastView from "@/components/batch-job/common/ToastView.vue";

export default {
  props: ["batch_id"],
  components: {ToastView, ProgressIndicator},
  data() {
    return {
      batchJob: null,
      allowedFileTypes: [],
      selectedFiles: null,
      isDragOver: false,
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
      this.state.isEditable = shouldEditDisabled(newVal?.batch_job_status);
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
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJob} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.fetchBatchJob} No response received.`);
        }
      } finally {
        this.state.isLoading = false;
      }
    },

    async fetchFileTypes() {
      try {
        this.allowedFileTypes = await fetchFileTypesAPI();
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.fileTypes} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.fileTypes} No response received.`);
        }
      }
    },

    handleDragOver() {
      this.isDragOver = true;
    },
    handleDragLeave() {
      this.isDragOver = false;
    },
    handleDrop(event) {
      this.isDragOver = false;
      const files = event.dataTransfer.files;
      this.handleFileChange({target: {files}});
    },
    handleFileChange(event) {
      this.selectedFiles = event.target.files.length ? Array.from(event.target.files) : null;
    },
    triggerFileInputClick() {
      this.$refs.fileInput.click(); // 숨겨진 파일 입력 클릭
    },

    async compressFiles(files, zipFileName = 'compressed_files.zip') {
      const zip = new JSZip();

      files.forEach((file) => {
        zip.file(file.name, file);
      });

      // 압축 파일을 지정한 이름으로 생성
      const compressedBlob = await zip.generateAsync({type: 'blob'});

      // ZIP 파일에 이름을 지정하여 반환
      return new File([compressedBlob], zipFileName, {type: 'application/zip'});
    },

    validateFile() {
      if (!this.selectedFiles || this.selectedFiles.length === 0) {
        return `${ERROR_MESSAGES.missingFile}`;
      }

      for (const file of this.selectedFiles) {
        const fileExtension = file.name.split(".").pop().toLowerCase();

        if (!this.allowedFileTypes.includes(fileExtension)) {
          return `${ERROR_MESSAGES.unsupportedFileType} ${this.allowedFileTypes.join(", ")}`;
        }
      }

      return null;
    },

    async uploadFile() {
      const errorMessage = this.validateFile();
      if (errorMessage) return this.handleMessages("error", errorMessage);

      try {
        this.state.isUploading = true;

        let filesToUpload = this.selectedFiles;
        if (this.selectedFiles.length > 1) {
          const zipFile = await this.compressFiles(this.selectedFiles, 'batch_files.zip');
          if (zipFile.size === 0) {
            return this.handleMessages("error", ERROR_MESSAGES.compressFiles);
          }
          filesToUpload = zipFile
        } else {
          filesToUpload = this.selectedFiles[0]
        }

        this.batchJob = await uploadFilesAPI(this.batch_id, filesToUpload);
        this.handleMessages("success", SUCCESS_MESSAGES.uploadFile);
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.uploadFile} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.uploadFile} No response received.`);
        }
      } finally {
        this.state.isUploading = false;
        this.resetFileInputHelper();
      }
    },

    resetFileInputHelper() {
      this.selectedFiles = null;
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
      } catch (error) {
        if (error.response) {
          this.handleMessages("error", `${ERROR_MESSAGES.deleteBatchJob} ${error.response.data.error}`);
        } else {
          this.handleMessages("error", `${ERROR_MESSAGES.deleteBatchJob} No response received.`);
        }
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
