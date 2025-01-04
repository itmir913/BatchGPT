<template>
  <div class="container mt-5">
    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="error" class="alert alert-danger text-center" role="alert">
      {{ error }}
    </div>

    <!-- 배치 작업 상세 정보 -->
    <div v-if="batchJob && !loading && !error" class="card">
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
          <form @submit.prevent="uploadFile">
            <div class="mb-3">
              <input
                  ref="fileInput"
                  class="form-control"
                  type="file"
                  @change="handleFileChange"
              />
            </div>
            <button :disabled="uploading" class="btn btn-primary" type="submit">
              {{ uploading ? "Uploading..." : "Upload File" }}
            </button>
          </form>
        </div>

        <!-- 업로드된 파일 정보 -->
        <div v-if="batchJob.file" class="mt-4">
          <h5>Uploaded File</h5>
          <a :href="batchJob.file" target="_blank">{{ batchJob.file }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/configs/axios";

export default {
  props: ['batch_id'],  // URL 파라미터를 props로 받음
  data() {
    return {
      batchJob: null, // 배치 작업 데이터
      loading: true, // 로딩 상태
      error: null, // 에러 메시지
      selectedFile: null, // 업로드할 파일
      uploading: false, // 업로드 상태
    };
  },
  methods: {
    // 배치 작업 데이터 가져오기
    async fetchBatchJob() {
      try {
        const response = await axios.get(`/api/batch-jobs/${this.batch_id}/`, {
          withCredentials: true,
        });
        this.batchJob = response.data;
      } catch (error) {
        console.error("Error fetching Batch Job:", error);
        this.error = "Failed to load Batch Job details. Please try again later.";
      } finally {
        this.loading = false;
      }
    },

    // 파일 선택 핸들러
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },

    // 파일 업로드 핸들러
    async uploadFile() {
      if (!this.selectedFile) {
        alert("Please select a file to upload.");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        this.uploading = true;
        const response = await axios.patch(
            `/api/batch-jobs/${this.batch_id}/upload/`,
            formData,
            {headers: {"Content-Type": "multipart/form-data"}, withCredentials: true}
        );
        this.batchJob = response.data; // 업데이트된 데이터 반영
        alert("File uploaded successfully!");
      } catch (error) {
        const errorMessage = error.response.data?.error || "Unknown error occurred.";
        console.error("Error uploading file:", errorMessage);
        alert(`Error uploading file: ${errorMessage}`);
      } finally {
        this.uploading = false;
        this.selectedFile = null;
        if (this.$refs.fileInput) {
          this.$refs.fileInput.value = ""; // 파일 입력 초기화
        }
      }
    },

    // 날짜 포맷팅 메서드
    formatDate(dateString) {
      const options = {year: "numeric", month: "long", day: "numeric"};
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },
  async created() {
    await this.fetchBatchJob();
  },
};
</script>

<style scoped>
.container {
  max-width: 800px;
}
</style>
