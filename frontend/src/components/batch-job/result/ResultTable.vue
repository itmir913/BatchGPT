<template>
  <div>
    <h2 class="mb-3">Results</h2>
    <div class="mb-3">
      <select :value="selectedStatus" class="form-select" @change="updateSelectedStatus($event)">
        <option value="">All Status</option>
        <option value="PENDING">Pending</option>
        <option value="IN_PROGRESS">In Progress</option>
        <option value="COMPLETED">Completed</option>
        <option value="FAILED">Failed</option>
      </select>
    </div>

    <div class="mb-5">
      <table class="table table-striped table-hover align-middle">
        <thead class="table-dark">
        <tr>
          <th scope="col" style="width: 10%;">Status</th>
          <th scope="col" style="width: 45%;">Request</th>
          <th scope="col" style="width: 45%;">Response</th>
        </tr>
        </thead>
        <tbody v-if="tasks.length > 0">
        <tr v-for="task in tasks" :key="task.task_unit_id">
          <td>
              <span :class="{
                'badge bg-warning text-dark': task.task_unit_status === 'Pending',
                'badge bg-info': task.task_unit_status === 'In Progress',
                'badge bg-danger': task.task_unit_status === 'Failed',
                'badge bg-success': task.task_unit_status === 'Completed',
              }">
                {{ task.task_unit_status }}
              </span>
          </td>
          <td>
            <div class="text-content badge bg-white text-dark border border-secondary d-block">
              {{ truncateText(task.request_data.prompt) }}
            </div>
            <div v-if="task.request_data.has_files">
              <div class="row g-4 px-3 py-3">
                <div v-for="(item, idx) in task.request_data.files_data" :key="idx"
                     class="col-md-4 col-sm-6 col-12">
                  <img :src="'data:image/jpeg;base64,' + item" alt="Image Preview" class="img-fluid">
                </div>
              </div>
            </div>
          </td>
          <td>
            <div class="text-content">{{ task.response_data }}</div>
          </td>
        </tr>
        </tbody>
        <tbody v-else>
        <tr>
          <td class="text-center" colspan="3">No Data</td>
        </tr>
        </tbody>
      </table>

      <!-- 페이지 버튼 -->
      <div v-if="tasks.length > 0"
           class="d-flex justify-content-center align-items-center mt-4">
        <nav aria-label="Page navigation">
          <ul class="pagination flex-wrap" style="gap: 5px;">
            <li :class="{disabled: currentPage === 1}" class="page-item">
              <button class="page-link" @click="changePage(1)">&lt;&lt;</button>
            </li>
            <li :class="{disabled: currentPage === 1}" class="page-item">
              <button class="page-link" @click="changePage(currentPage - 1)">&lt;</button>
            </li>
            <li v-if="currentPage > 3" class="page-item">
              <span class="page-link">...</span>
            </li>
            <li v-for="page in pageRange" :key="page" :class="{active: currentPage === page}" class="page-item">
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>
            <li v-if="currentPage < totalPages - 2" class="page-item">
              <span class="page-link">...</span>
            </li>
            <li :class="{disabled: currentPage === totalPages}" class="page-item">
              <button class="page-link" @click="changePage(currentPage + 1)">&gt;</button>
            </li>
            <li :class="{disabled: currentPage === totalPages}" class="page-item">
              <button class="page-link" @click="changePage(totalPages)">&gt;&gt;</button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<style>
.text-content {
  text-align: justify;
  word-wrap: break-word;
  white-space: normal;
}
</style>

<script>
export default {
  props: {
    tasks: Array,
    currentPage: Number,
    totalPages: Number,
    selectedStatus: String,
  },
  computed: {
    pageRange() {
      const range = [];
      const start = Math.max(this.currentPage - 3, 1);
      const end = Math.min(this.currentPage + 3, this.totalPages);

      for (let i = start; i <= end; i++) {
        range.push(i);
      }

      return range;
    },
  },
  methods: {
    changePage(page) {
      this.$emit('change-page', page);
    },

    truncateText(text) {
      const maxLength = 500;
      return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
    },

    updateSelectedStatus(event) {
      this.$emit('update:selectedStatus', event.target.value);
    }
  }
};
</script>