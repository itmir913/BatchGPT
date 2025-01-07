<template>
  <div>
    <!-- Title 입력 -->
    <div class="mb-3">
      <label class="form-label" for="title">Title</label>
      <input
          id="title"
          v-model="localBatchJob.title"
          :class="{ 'is-invalid': isTitleInvalid }"
          class="form-control"
          placeholder="Enter the title of the batch job"
          required
          type="text"
          @input="updateBatchJob"
      />
      <div v-if="isTitleInvalid" class="invalid-feedback">
        Title is required.
      </div>
    </div>

    <!-- Description 입력 -->
    <div class="mb-3">
      <label class="form-label" for="description">Description</label>
      <textarea
          id="description"
          v-model="localBatchJob.description"
          class="form-control"
          placeholder="Enter a description (optional)"
          rows="4"
          @input="updateBatchJob"
      ></textarea>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    batchJob: {
      type: Object,
      required: true,
    },
    isTitleInvalid: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      localBatchJob: {...this.batchJob}, // 로컬 데이터로 복사
    };
  },
  methods: {
    updateBatchJob() {
      this.$emit("update:batchJob", this.localBatchJob); // 부모로 업데이트 이벤트 전달
    },
  },
};
</script>
