<template>
  <div>
    <h2 class="mb-3">Files Preview</h2>
    <table v-if="filteredData.length > 0" class="table table-bordered table-hover align-middle"
           style="table-layout: fixed;">
      <thead class="table-light">
      <tr>
        <th v-if="filteredData.length > 0" class="text-center text-primary" style="cursor: pointer;">
          Preview
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(row, rowIndex) in filteredData" :key="'row-' + rowIndex">
        <td style="cursor: pointer; white-space: pre-wrap; word-wrap: break-word;">
          <template v-if="row.type === 'image'">
            <div class="row g-4 p-3">
              <!-- 이미지들을 4개씩 한 행에 배치 -->
              <div v-for="(item, idx) in row.preview" :key="'img-' + idx" class="col-md-4 col-sm-6 col-12">
                <img :src="'data:image/jpeg;base64,' + item" alt="Image Preview" class="img-fluid">
              </div>
            </div>
          </template>
          <template v-else-if="row.type === 'text'">
            {{ row.preview }}
          </template>
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
  computed: {
    filteredData() {
      return this.data.map(row => {
        return {preview: row.preview, type: row.type};
      });
    }
  }
};
</script>

<style>
.table td {
  white-space: pre-wrap;
  word-wrap: break-word;
}

img {
  max-width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}
</style>
