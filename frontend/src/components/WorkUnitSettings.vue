<template>
  <div v-if="isReady">
    <h3 class="text-center mt-4 mb-2">Select Number of Items per Task</h3>
    <div class="d-flex justify-content-center align-items-center mb-2">
      <!-- 라디오 버튼들 -->
      <div v-for="unit in [1, 2, 4, 8]" :key="unit" class="form-check me-3">
        <input
            :id="'work_unit' + unit"
            v-model.number="localWorkUnit"
            :disabled="isSupportedType"
            :value="unit"
            class="form-check-input"
            type="radio"
        />
        <label :for="'work_unit' + unit" class="form-check-label">{{ unit }}</label>
      </div>

      <!-- 사용자 입력 필드 -->
      <div class="input-group w-25">
        <span class="input-group-text">Custom Units:</span>
        <input
            v-model.number="localWorkUnit"
            :disabled="isSupportedType"
            class="form-control"
            min="1"
            placeholder="Unit"
            type="number"
        />
      </div>
    </div>

    <!-- 안내 메시지 -->
    <div class="text-info">
      Each time a request is made to GPT, it processes items in groups of {{ localWorkUnit }} items.
    </div>
    <div class="text-dark">
      A total of {{ totalRequests }} requests will be processed.
    </div>

    <div v-if="isSupportedType" class="text-success">
      This option is disabled as the current file type does not support it.
    </div>

    <!-- 경고 메시지 -->
    <div v-if="remainder !== 0" class="text-danger">
      There are {{ remainder }} items left to process with the last request.
    </div>
    <div v-if="localWorkUnit > batchJob.total_size" class="text-bg-danger">
      The {{ localWorkUnit }} work unit cannot exceed the total size.
    </div>
  </div>
</template>

<script>
export default {
  props: {
    batchJob: Object,
    isReady: Boolean,
    work_unit: Number,
  },
  computed: {
    totalRequests() {
      return this.batchJob ? Math.ceil(this.batchJob.total_size / this.work_unit) : 0;
    },
    remainder() {
      return this.batchJob.total_size % this.work_unit;
    },
    isSupportedType() {
      return this.batchJob.file_type !== 'pdf';
    },
  },
  data() {
    return {
      localWorkUnit: this.work_unit
    };
  },
  watch: {
    localWorkUnit(newVal) {
      this.$emit('update:work_unit', newVal);
    }
  },
};
</script>

<style scoped>
/* 선택적인 스타일을 여기에 추가 */
</style>
