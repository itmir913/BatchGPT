<template>
  <div class="container mt-5">

    <!-- 5단계 워크플로우 표시 -->
    <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 메시지 표시 -->
    <div v-if="success" class="alert alert-success text-center mt-4" role="alert">{{ success }}</div>
    <div v-if="error" class="alert alert-danger text-center mt-4" role="alert">{{ error }}</div>

    <!-- 배치 작업 상세 정보 -->
    <div v-if="isReady" class="card">
      <div class="card-body">
        <h2 class="card-title">{{ batchJob.title }}</h2>
        <p class="card-text">{{ batchJob.description || "No description provided." }}</p>
        <p class="card-text text-muted">
          Created At: {{ formatDate(batchJob.created_at) }}<br/>
          Updated At: {{ formatDate(batchJob.updated_at) }}
        </p>

        <!-- 파일 업로드 섹션 -->
        <div class="mt-4">
          <h5>File Upload</h5>
          <form class="d-flex align-items-center gap-2" @submit.prevent="uploadFile">
            <input
                ref="fileInput"
                class="form-control flex-grow-1"
                type="file"
                @change="handleFileChange"
            />
            <button
                :disabled="uploading"
                class="btn btn-primary"
                style="white-space: nowrap;"
                type="submit"
            >
              {{ uploading ? "Uploading..." : "Upload File" }}
            </button>
          </form>
        </div>

        <!-- 업로드된 파일 정보 -->
        <div v-if="batchJob.file_name" class="mt-4">
          <h5>Uploaded File</h5>
          <h6>{{ batchJob.file_name }}</h6>
        </div>

        <!-- 하단 버튼 추가 -->
        <div class="d-flex justify-content-between mt-4">
          <div>
            <button class="btn btn-danger" @click="deleteBatchJob">Delete</button>
            <button class="btn btn-secondary ms-2" @click="editBatchJob">Edit</button>
          </div>
          <button
              :disabled="isNextButtonDisabled"
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
import axios from "@/configs/axios";
import ProgressIndicator from '@/components/BatchJobProgressIndicator.vue';

export default {
  props: ['batch_id'],
  components: {
    ProgressIndicator,
  },
  data() {
    return {
      currentStep: 1,
      batchJob: null,
      loading: true,
      error: null,
      success: null,
      selectedFile: null,
      uploading: false,
      allowedFileTypes: [],
    };
  },
  computed: {
    isReady() {
      return !this.loading;
    },
    isNextButtonDisabled() {
      return !this.batchJob || !this.batchJob.file_name;
    },
  },
  methods: {

    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/`, {withCredentials: true});
        this.batchJob = response.data;
        this.clearMessage()
      } catch (error) {
        this.handleError("Failed to load Batch Job details. Please try again later.");
      } finally {
        this.loading = false;
      }
    },

    async fetchFileTypes() {
      try {
        const response = await axios.get('/api/batch-jobs/supported-file-types/');
        this.allowedFileTypes = Object.values(response.data); // ['csv', 'pdf', ...]
      } catch (error) {
        this.handleError("Failed to retrieve the types of files supported by the server. Please try again later.");
      }
    },

    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },

    async uploadFile() {
      if (!this.selectedFile) {
        return this.handleError("Please select a file to upload.");
      }

      const fileExtension = this.selectedFile.name.split('.').pop().toLowerCase();
      if (!this.allowedFileTypes.includes(fileExtension)) {
        this.handleError(`Unsupported file type.
        Please upload one of the following: ${this.allowedFileTypes.join(', ')}`)

        this.selectedFile = null;
        this.resetFileInput();
        return;
      }

      try {
        const formData = new FormData();
        formData.append("file", this.selectedFile);
        this.uploading = true;
        const response = await axios.patch(
            `/api/batch-jobs/${this.batch_id}/upload/`,
            formData,
            {headers: {"Content-Type": "multipart/form-data"}, withCredentials: true}
        );
        this.batchJob = response.data;
        this.handleSuccess("File uploaded successfully!")
      } catch (error) {
        this.handleError(`Error uploading file: ${error.response.data?.error || "Unknown error occurred."}`);
      } finally {
        this.uploading = false;
        this.selectedFile = null;
        this.resetFileInput();
      }
    },

    clearMessage() {
      this.error = null;
      this.success = null;
    },

    handleError(message) {
      this.error = message;
      this.success = null;
    },

    handleSuccess(message) {
      this.error = null;
      this.success = message;
    },

    resetFileInput() {
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
          await axios.delete(`/api/batch-jobs/${this.batch_id}/`, {withCredentials: true});
          alert("Batch Job deleted successfully!")
          this.$router.push(`/home`);
        } catch (error) {
          this.handleError(`Error deleting batch job: ${error.response.data?.error || "Unknown error occurred."}`);
        }
      }
    },

    goToNextStep() {
      if (!this.batchJob.file_name) {
        return this.handleError("The uploaded file is missing. Please select a file to upload.");
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
