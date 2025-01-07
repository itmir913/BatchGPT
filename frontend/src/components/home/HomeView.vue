<template>
  <div class="container mt-5">
    <!-- 인증되지 않은 상태 -->
    <div v-if="!loading && !isAuthenticated" class="alert alert-warning text-center">
      <p>Please log in.</p>
    </div>

    <!-- 인증된 상태 -->
    <div v-if="!loading && isAuthenticated" class="card border-light shadow-lg"
         style="background: #f8f9fa; border-radius: 1rem;">
      <div class="card-body">
        <h4 class="card-title mb-3 text-primary">Welcome, {{ user.email }}!</h4>

        <!-- 추가 정보 출력 (예시) -->
        <ul class="list-group list-group-flush">
          <li class="list-group-item bg-light">
            <strong>Balances:</strong> ${{ user.balance }}
          </li>
          <!-- 필요한 추가 정보를 여기에 삽입 -->
        </ul>

        <button class="btn btn-outline-primary mt-3 w-100" @click="logout">
          Logout
        </button>
      </div>
    </div>

    <!-- 배치 작업 섹션 -->
    <div v-if="isAuthenticated" class="mt-5">
      <!-- 헤더 -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>My Batch Jobs</h2>
        <button class="btn btn-success" @click="goToCreateBatchJob">Add New Batch Job</button>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="loading" class="text-center my-5">
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
        <div v-for="job in batchJobs" :key="job.id" class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">
                <a
                    :href="`/batch-jobs/${job.id}`"
                    class="text-decoration-none text-primary"
                >
                  {{ job.title }}
                </a>
              </h5>
              <p class="card-text">
                {{ job.description || "No description provided." }}
              </p>
              <p class="card-text text-muted">
                Created: {{ formatDate(job.created_at) }}<br/>
                Updated: {{ formatDate(job.updated_at) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 배치 작업 없음 -->
      <p v-else class="text-center text-muted">
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
      user: {
        email: "",
        balance: 0,
      },
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
      this.user.email = authResponse.data.email;
      this.user.balance = authResponse.data.balance;

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
