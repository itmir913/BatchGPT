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

    <!-- 5단계 워크플로우 표시 -->
    <ProgressIndicator v-if="batchJob && !loading && !error" :batch_id="batch_id" :currentStep="currentStep"/>

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
          <form class="d-flex align-items-center gap-2" @submit.prevent="uploadFile">
            <!-- 파일 선택 필드 -->
            <input
                ref="fileInput"
                class="form-control flex-grow-1"
                type="file"
                @change="handleFileChange"
            />

            <!-- 업로드 버튼 -->
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
            <!-- DELETE 버튼 (왼쪽) -->
            <button class="btn btn-danger" @click="deleteBatchJob">Delete</button>

            <!-- 수정 버튼 (왼쪽) -->
            <button class="btn btn-secondary ms-2" @click="editBatchJob">Edit</button> <!-- ms-2 클래스 추가 -->
          </div>

          <!-- 다음 버튼 (오른쪽) -->
          <button :disabled="isNextButtonDisabled" class="btn btn-success" @click="goToNextStep">Next</button>
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
      currentStep: 1, // 현재 진행 중인 단계 (0부터 시작)

      batchJob: null, // 배치 작업 데이터
      loading: true, // 로딩 상태
      error: null, // 에러 메시지
      selectedFile: null, // 업로드할 파일
      uploading: false, // 업로드 상태
      isNextButtonDisabled: true,
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
        if (this.batchJob.file_name != null) {
          this.isNextButtonDisabled = false;
        }
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
        window.location.reload()
      }
    },

    editBatchJob() {
      // 수정 로직 구현 (예: 편집 페이지로 이동)
      // /batch-jobs/:batch_id/edit
      this.$router.push(`/batch-jobs/${this.batch_id}/edit`);
      console.log("Edit Batch Job");
    },

    async deleteBatchJob() {
      // 사용자에게 삭제 확인 알림 띄우기
      if (confirm("Are you sure you want to delete this batch job?")) {
        // DELETE 요청 보내기
        try {
          await axios.delete(
              `/api/batch-jobs/${this.batch_id}/`,
              {headers: {"Content-Type": "multipart/form-data"}, withCredentials: true}
          );
          alert("BatchJob Deleted successfully!");
          this.$router.push(`/home`);
        } catch (error) {
          const errorMessage = error.response.data?.error || "Unknown error occurred.";
          console.error("Error uploading file:", errorMessage);
          alert(`Error uploading file: ${errorMessage}`);
        }
      } else {
        console.log("Delete action canceled.");
      }
    },

    goToNextStep() {
      // 다음 단계로 이동하는 로직 구현
      if (this.batchJob.file_name == null) {
        console.log("File Null");
        alert("The uploaded file is missing. Please select a file to upload.");
        return
      }
      this.$router.push(`/batch-jobs/${this.batch_id}/configs`);
      console.log("Go to Next Step");
    },

    // 날짜 포맷팅 메서드
    formatDate(dateString) {
      const options = {year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "numeric"};
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
  max-width: 1000px;
}
</style>
