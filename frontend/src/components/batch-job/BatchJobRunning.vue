<template>
  <div class="container mt-4 infinite-scroll-container">
    <!-- 진행 상태 표시 -->
    <div class="mb-4">
      <ProgressIndicator :batch_id="batch_id" :currentStep="currentStep"/>
    </div>

    <!-- CSV 표 형식 테이블 -->
    <div class="table-responsive">
      <table class="table table-striped table-hover align-middle custom-table">
        <thead class="table-dark">
        <tr>
          <!-- 열 비율 설정 -->
          <th scope="col" style="width: 10%;">Status</th>
          <th scope="col" style="width: 45%;">Request</th>
          <th scope="col" style="width: 45%;">Response</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="task in tasks" :key="task.task_unit_id">
          <td>
            <!-- Status 표시 -->
            <span
                :class="{
                  'badge bg-success': task.status === 'COMPLETED',
                  'badge bg-warning text-dark': task.status === 'PENDING',
                  'badge bg-danger': task.status === 'FAILED'
                }"
            >
                {{ task.task_response_status }}
              </span>
          </td>
          <td>{{ parseResponseData(task.request_data) }}</td>
          <td>{{ parseResponseData(task.response_data) }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- 로딩 상태 표시 -->
    <div v-if="formStatus.isLoading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 더 이상 데이터가 없을 때 -->
    <div v-if="!formStatus.hasMore && !formStatus.isLoading" class="text-center my-4">
      <p class="text-muted">No more data</p>
    </div>
  </div>
</template>

<script>
import axios from "@/configs/axios";
import ProgressIndicator from "@/components/batch-job/components/ProgressIndicator.vue";

const API_BASE_URL = "/api/batch-jobs/";
const API_TASK_UNITS_URL = "/task-units/";

export default {
  props: ["batch_id"],
  components: {ProgressIndicator},
  data() {
    return {
      currentStep: 4,
      tasks: [], // TaskUnit 데이터를 저장
      nextPage: null, // 다음 페이지 URL
      loadingState: {loading: true, loadingSave: false},
      hasMore: true, // 추가 데이터 여부
    };
  },
  computed: {
    formStatus() {
      return {
        isLoading: this.loadingState.loading, // 로딩 중인지 여부
        hasMore: this.hasMore, // 더 가져올 데이터가 있는지 여부
        isReady: !this.loadingState.loading && this.hasMore, // 데이터 로드 준비 상태
      };
    },
  },
  methods: {
    async fetchTasks(url = `${API_BASE_URL}${this.batch_id}${API_TASK_UNITS_URL}`) {
      this.loadingState.loading = true;
      try {
        const response = await axios.get(url);
        const data = response.data;

        // 새로운 데이터를 기존 데이터에 추가
        this.tasks.push(...data.results);

        // 다음 페이지 URL 설정
        this.nextPage = data.next;

        // 더 이상 데이터가 없으면 hasMore를 false로 설정
        this.hasMore = !!data.next;
      } catch (error) {
        console.error("Error fetching tasks:", error);
      } finally {
        this.loadingState.loading = false;
      }
    },
    parseResponseData(responseData) {
      return responseData;
    },
    handleScroll() {
      const bottomOfWindow =
          window.innerHeight + window.scrollY >= document.documentElement.offsetHeight - 10;

      if (bottomOfWindow && this.formStatus.isReady) {
        this.fetchTasks(this.nextPage); // 다음 페이지 데이터 로드
      }
    },
  },
  async created() {
    await this.fetchTasks();

    // 스크롤 이벤트 리스너 추가
    window.addEventListener("scroll", this.handleScroll);
  },
  beforeUnmount() {
    // 스크롤 이벤트 리스너 제거
    window.removeEventListener("scroll", this.handleScroll);
  },
};
</script>

<style scoped>
.container {
  max-width: 1000px;
}

.infinite-scroll-container {
  padding: 20px;
}

.table-responsive {
  margin-top: 20px;
}

/* 열 구분선 추가 */
.custom-table td,
.custom-table th {
  border-right: 1px solid #dee2e6; /* Bootstrap 기본 테이블 경계선 색상 */
}

.custom-table th:last-child,
.custom-table td:last-child {
  border-right: none; /* 마지막 열은 구분선 제거 */
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.text-muted {
  font-size: 1.2rem;
}
</style>
