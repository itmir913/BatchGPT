<template>
  <div>
    <h2 class="mb-3">CSV Preview</h2>
    <div class="mb-3">
      <div v-if="selectedColumns.length > 0">
        <div>The columns you have selected can be included in the GPT request prompt.</div>
        <div>To do so, you need to add them in the following format: {{
            selectedColumns.map(col => '{' + `${col}` + '}').join(', ')
          }}
        </div>
      </div>
      <div v-else>
        <div>Please select the columns you want to include in the GPT request.</div>
        <div>Once selected, you can use them in the prompt.</div>
      </div>
    </div>
    <table
        v-if="Array.isArray(filteredData) && filteredData.length > 0"
        class="table table-hover table-bordered table-striped mb-2"
    >
      <thead class="table-primary">
      <tr>
        <!-- 각 열 이름 -->
        <th
            v-for="(value, key) in filteredData[0]"
            :key="'header-' + key"
            :class="{ 'selected-column': selectedColumns.includes(key) }"
            style="cursor: pointer;"
            @click="toggleColumnSelection(key)"
        >
          {{ key }}
        </th>
      </tr>
      </thead>
      <tbody>
      <!-- 데이터 행 렌더링 -->
      <tr v-for="row in filteredData" :key="'row-' + row.id">
        <td
            v-for="(value, key) in row"
            :key="'cell-' + key"
            :class="{ 'selected-column': selectedColumns.includes(key) }"
            style="cursor: pointer;"
            @click="toggleColumnSelection(key)"
        >
          {{ value }}
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  props: {
    previewData: Array,
    selectedColumns: {
      type: Array,
      default: () => []
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    filteredData() {
      // eslint-disable-next-line no-unused-vars
      return this.previewData.map(({index, ...rest}) => rest);
    },
  },
  methods: {
    toggleColumnSelection(column) {
      if (!this.disabled)
        this.$emit('toggle-column', column);
    }
  }
};
</script>

<style scoped>
.selected-column {
  background-color: #d1ecf1 !important;
  font-weight: bold;
}

.table th,
.table td {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.table th {
  cursor: pointer;
}

.table th:hover,
.table td:hover {
  background-color: #f8d7da;
}
</style>
