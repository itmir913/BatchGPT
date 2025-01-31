<template>
  <div>
    <h2 class="mb-3">Files Preview</h2>
    <LoadingView v-if="filteredData.length <= 0"/>
    <table v-else class="table table-bordered table-hover align-middle">
      <thead class="table-light">
      <tr>
        <th class="text-center text-primary" style="cursor: pointer;">
          Preview
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(row, rowIndex) in filteredData" :key="'row-' + rowIndex">
        <td style="cursor: pointer;">
          <template v-if="row.type === 'image'">
            <div class="row g-4 px-3 py-3">
              <div v-for="(item, idx) in row.preview" :key="'img-' + idx" class="col-md-3 col-sm-6 col-12">
                <img :src="'data:image/jpeg;base64,' + item" alt="Image Preview" class="img-fluid">
              </div>
            </div>
          </template>
          <template v-else-if="row.type === 'text'">
            <div class="text-content">{{ truncateText(row.preview) }}</div>
          </template>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import LoadingView from "@/components/batch-job/common/LoadingSpinner.vue";

export default {
  components: {LoadingView},
  props: {
    data: Array,
  },
  computed: {
    filteredData() {
      return this.data.map(row => {
        return {preview: row.preview, type: row.type};
      });
    }
  },
  methods: {
    truncateText(text) {
      const maxLength = 500;
      return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
    }
  },
};
</script>

<style scoped>
.table td {
  padding: 0.5rem;
  vertical-align: top;
}

.text-content {
  text-align: justify;
  word-wrap: break-word;
  white-space: normal;
}

img {
  max-width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}
</style>
