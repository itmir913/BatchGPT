<template>
  <header class="py-5 bg-light border-bottom mb-4">
    <div class="container">
      <div class="text-center my-5">
        <h1 class="fw-bolder">Welcome to Batch GPT!</h1>
        <p class="lead mb-0">Your creative partner for effortless AI batch processing!</p>
      </div>
    </div>
  </header>

  <div class="container mt-5">
    <!-- 인증되지 않은 상태 -->
    <div v-if="!loading && !isAuthenticated" class="alert alert-warning text-center mb-4">
      <p class="fw-bold">Please log in to access your dashboard.</p>
    </div>

    <!-- 인증된 상태 -->
    <div v-if="!loading && isAuthenticated" class="row">
      <!-- 사용자 계정 정보 섹션 -->
      <div class="col-md-4 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-dark"><i class="bi bi-person-circle"></i> My Account</h2>
        </div>

        <div class="p-4 bg-light rounded-3 shadow-sm">
          <h4 class="text-primary mb-3">
            <i class="bi bi-person-circle"></i> Welcome, {{ user.email }}!
          </h4>
          <ul class="list-group">
            <li class="list-group-item bg-light">
              <strong>Balances:</strong> ${{ user.balance }}
            </li>
          </ul>
          <button class="btn btn-outline-primary mt-3 w-100" @click="logout">
            Logout
          </button>
        </div>
      </div>

      <!-- 배치 작업 섹션 -->
      <div class="col-md-8 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-dark"><i class="bi bi-gear"></i> My Batch Jobs</h2>
          <button class="btn btn-primary" @click="goToCreateBatchJob">
            Add New Batch Job
          </button>
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
          <div v-for="job in batchJobs" :key="job.id" class="col-md-6 mb-4">
            <a :href="`/batch-jobs/${job.id}`" class="text-decoration-none">
              <div class="card h-100 shadow-sm rounded-3 border">
                <div class="card-body">
                  <h5 class="card-title text-primary">
                    <i class="bi bi-file-earmark-text"></i> {{ job.title }}
                  </h5>
                  <p class="card-text">
                    {{ job.description || "No description provided." }}
                  </p>
                  <p class="card-text text-muted" style="font-size: 0.875rem;">
                    Created: {{ formatDate(job.created_at) }}<br/>
                    Updated: {{ formatDate(job.updated_at) }}
                  </p>
                </div>
              </div>
            </a>
          </div>
        </div>

        <!-- 배치 작업 없음 -->
        <p v-else class="text-center text-muted">
          No batch jobs found. Start by adding one!
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기본 스타일 */
.bg-light {
  background-color: #f8f9fa !important;
}

.card {
  border-radius: 0.75rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.card-body {
  padding: 1.25rem;
}

.btn-outline-primary {
  border-radius: 0.75rem;
}

.text-muted {
  font-size: 0.875rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

@media (max-width: 767px) {
  .card-body {
    padding: 1rem;
  }

  .btn {
    font-size: 0.875rem;
  }
}
</style>

<script>
import {fetchBatchJobListAPI} from "@/components/batch-job/utils/BatchJobUtils";
import {fetchAuthAPI, logoutAPI} from "@/components/auth/AuthUtils";

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

      const {isAuthenticated, email, balance} = await fetchAuthAPI();
      this.isAuthenticated = isAuthenticated;
      this.user.email = email;
      this.user.balance = balance;

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
        this.batchJobs = await fetchBatchJobListAPI();
      } catch (error) {
        console.error("Error fetching batch jobs:", error);
        this.error = "Failed to fetch batch jobs. Please try again later.";
      } finally {
        this.loading = false;
      }
    },
    async logout() {
      try {
        await logoutAPI();
        this.isAuthenticated = false;
        this.user.email = "";
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
      const options = {year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric"};
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },
};
</script>
