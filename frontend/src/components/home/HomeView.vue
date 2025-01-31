<template>
  <ToastView
      ref="toast"
      :message="messages"
  />

  <header class="py-5 bg-light border-bottom mb-4">
    <div class="container">
      <div class="text-center my-5">
        <h1 class="fw-bolder">Welcome to Batch GPT!</h1>
        <p class="lead mb-0">Your creative partner for effortless AI batch processing!</p>
      </div>
    </div>
  </header>

  <div class="container my-4">
    <!-- 인증된 상태 -->
    <div class="row">
      <!-- 사용자 계정 정보 섹션 -->
      <div class="col-md-4 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-dark"><i class="bi bi-person-circle"></i> My Account</h2>
        </div>

        <LoadingView v-if="formStatus.isUserDataLoading"/>
        <div v-else class="p-4 bg-light rounded-3 shadow-sm">
          <h4 class="text-primary mb-3">
            <i class="bi bi-person-circle"></i> Welcome, {{ user.username }}!
          </h4>
          <ul class="list-group">
            <li class="list-group-item bg-light">
              <strong>Email:</strong> {{ user.email }}
            </li>
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

        <!-- 배치 작업 리스트 -->
        <LoadingView v-if="formStatus.isBatchJobLoading"/>
        <div v-else-if="batchJobs.length > 0" class="row">
          <div v-for="job in batchJobs" :key="job.id" class="col-md-6 mb-4">
            <router-link :to="getJobLink(job)" class="text-decoration-none">
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
                  <span :class="{
                  'badge bg-success': job.batch_job_status === BATCH_JOB_STATUS.COMPLETED,
                  'badge bg-warning text-dark': job.batch_job_status === BATCH_JOB_STATUS.IN_PROGRESS,
                  'badge bg-danger': job.batch_job_status === BATCH_JOB_STATUS.FAILED,
                  'badge bg-secondary': ![BATCH_JOB_STATUS.COMPLETED, BATCH_JOB_STATUS.IN_PROGRESS, BATCH_JOB_STATUS.FAILED].includes(job.batch_job_status)
                   }">
                  {{ job.batch_job_status }}
                </span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
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
import {
  BATCH_JOB_STATUS,
  ERROR_MESSAGES,
  fetchBatchJobListAPI,
  getJobLink,
  getStepLink
} from "@/components/batch-job/utils/BatchJobUtils";
import {fetchAuthAPI, logoutAPI} from "@/components/auth/AuthUtils";
import LoadingView from "@/components/batch-job/common/LoadingSpinner.vue";
import ToastView from "@/components/batch-job/common/ToastView.vue";
import {getErrorMessage} from "@/components/batch-job/utils/CommonFunctions";

export default {
  components: {ToastView, LoadingView},
  data() {
    return {
      isAuthenticated: false, // 사용자 인증 상태
      user: {
        username: "",
        email: "",
        balance: 0,
      },
      batchJobs: [], // 사용자 배치 작업 데이터
      loadingState: {userDataLoading: false, fetchBatchJobLoading: false},
      messages: {success: null, error: null},
    };
  },

  computed: {
    BATCH_JOB_STATUS() {
      return BATCH_JOB_STATUS
    },
    formStatus() {
      return {
        isUserDataLoading: this.loadingState.userDataLoading,
        isBatchJobLoading: this.loadingState.fetchBatchJobLoading,
      };
    },
  },

  methods: {
    getJobLink,
    clearMessages() {
      this.messages.error = null;
      this.messages.success = null;
    },

    handleMessages(type, message, details = "") {
      this.clearMessages();

      const fullMessage = details ? `${message} - ${details}` : message;
      this.messages[type] = fullMessage;
      this.messages.error = type === "error" ? fullMessage : null;
      this.messages.success = type === "success" ? fullMessage : null;
    },

    async fetchUserAccount() {
      if (this.loadingState.userDataLoading) return;

      try {
        this.loadingState.userDataLoading = true;

        const {isAuthenticated, username, email, balance} = await fetchAuthAPI();
        this.isAuthenticated = isAuthenticated;
        this.user.username = username;
        this.user.email = email;
        this.user.balance = balance;

        if (this.isAuthenticated)
          await this.fetchBatchJobs();

      } catch (error) {
        console.error("Error checking authentication:", error);
        this.isAuthenticated = false;
        this.$router.push({name: 'Login'});
      } finally {
        this.loadingState.userDataLoading = false;
      }
    },

    async fetchBatchJobs() {
      if (this.loadingState.fetchBatchJobLoading) return;

      try {
        this.loadingState.fetchBatchJobLoading = true;
        this.batchJobs = await fetchBatchJobListAPI();
      } catch (error) {
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.fetchBatchJobList}`);
        this.handleMessages("error", errorMessage);
      } finally {
        this.loadingState.fetchBatchJobLoading = false;
      }
    },

    async logout() {
      try {
        await logoutAPI();
        this.isAuthenticated = false;

        this.user = {
          username: "",
          email: "",
          balance: 0,
        };

        alert("You have been logged out.");
        this.$router.push({name: 'Login'});
      } catch (error) {
        console.error("Error during logout:", error);
        alert("Logout failed. Please try again.");
      }
    },

    goToCreateBatchJob() {
      this.$router.push(getStepLink(0, null));
    },

    formatDate(dateString) {
      const options = {year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric"};
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },

  async mounted() {
    await this.fetchUserAccount();
  },
};
</script>
