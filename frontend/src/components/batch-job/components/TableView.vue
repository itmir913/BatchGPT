<template>
  <div>
    <h2 class="mb-3">Files Preview</h2>
    <table
        v-if="Array.isArray(data) && data.length > 0"
        class="table table-bordered table-hover align-middle"
        style="table-layout: fixed;"
    >
      <thead class="table-light">
      <tr>
        <!-- 각 열 이름 -->
        <th
            v-for="(value, key) in data[0]"
            :key="'header-' + key"
            class="text-center text-primary"
            style="cursor: pointer;"
        >
          {{ key }}
        </th>
      </tr>
      </thead>
      <tbody>
      <!-- 데이터 행 렌더링 -->
      <tr v-for="row in data" :key="'row-' + row.id">
        <td
            v-for="(value, key) in row"
            :key="'cell-' + key"
            style="cursor: pointer;"
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
    data: Array,
  },
};
</script>
