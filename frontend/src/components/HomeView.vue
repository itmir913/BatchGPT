<template>
  <div class="container mt-5">
    <!-- 인증된 사용자 -->
    <div v-if="!loading && isAuthenticated" class="alert alert-success text-center">
      <p>Welcome, {{ email }}!</p>
      <button class="btn btn-primary mt-3" @click="logout">Logout</button>
    </div>

    <!-- 인증되지 않은 사용자 -->
    <div v-if="!loading && !isAuthenticated" class="alert alert-warning text-center">
      <p>Please log in.</p>
    </div>

    <!-- 배치 작업 리스트 -->
    <div v-if="isAuthenticated" class="mt-5">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>My Batch Jobs</h2>
        <!-- 배치 작업 추가 버튼 -->
        <button class="btn btn-success" @click="goToCreateBatchJob">Add New Batch Job</button>
      </div>

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

      <!-- 배치 작업 리스트 -->
      <div v-if="batchJobs.length > 0" class="row">
        <div
            v-for="job in batchJobs"
            :key="job.id"
            class="col-md-4 mb-4"
        >
          <div class="card h-100">
            <div class="card-body">
              <!-- 제목 및 링크 -->
              <h5 class="card-title">
                <a :href="`/batch-jobs/${job.id}`" class="text-decoration-none text-primary">
                  {{ job.title }}
                </a>
              </h5>

              <!-- 설명 표시 -->
              <p class="card-text">
                {{ job.description || "No description provided." }}
              </p>

              <!-- 날짜 표시 -->
              <p class="card-text text-muted">
                Created At: {{ formatDate(job.created_at) }}<br/>
                Updated At: {{ formatDate(job.updated_at) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 배치 작업이 없을 때 -->
      <p v-else-if="!loading && !error" class="text-center text-muted">
        No batch jobs found.
      </p>
    </div>
  </div>
</template>


<script>
import axios from "@/configs/axios";

export default {
  data() {
    return {
      isAuthenticated: false, // 사용자 인증 상태
      email: "", // 사용자 이메일
      batchJobs: [], // 사용자 배치 작업 데이터
      loading: false, // 로딩 상태
      error: null, // 에러 메시지
    };
  },
  async created() {
    try {
      // 인증 상태 확인
      this.loading = true;
      const authResponse = await axios.get("/api/auth/check/", {
        withCredentials: true,
      });
      this.isAuthenticated = authResponse.data.is_authenticated;
      this.email = authResponse.data.email;

      // 배치 작업 데이터 가져오기
      if (this.isAuthenticated) {
        await this.fetchBatchJobs();
      }
    } catch (error) {
      console.error("Error checking authentication:", error);
      this.isAuthenticated = false;
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async fetchBatchJobs() {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.get("/api/batch-jobs/", {
          withCredentials: true,
        });
        this.batchJobs = response.data; // API에서 가져온 데이터 저장
      } catch (error) {
        console.error("Error fetching batch jobs:", error);
        this.error = "Failed to fetch batch jobs. Please try again later.";
      } finally {
        this.loading = false;
      }
    },
    async logout() {
      try {
        await axios.post("/api/auth/logout/", {}, {withCredentials: true});
        this.isAuthenticated = false;
        this.email = "";
        alert("You have been logged out.");
        await this.$router.push("/login");
      } catch (error) {
        console.error("Error during logout:", error);
        alert("Logout failed. Please try again.");
      }
    },
    goToCreateBatchJob() {
      // /batch-job/create 경로로 이동
      this.$router.push("/batch-jobs/create");
    },
    formatDate(dateString) {
      const options = {year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "numeric"};
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}
</style>
