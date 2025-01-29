<template>
  <div>
    <h2 class="mb-3">Select Number of Items per Task</h2>
    <div class="d-flex justify-content-center align-items-center mb-3">
      <!-- 라디오 버튼들 -->
      <div v-for="unit in [1, 2, 4, 8]" :key="unit" class="form-check me-3">
        <input
            :id="'work_unit' + unit"
            v-model.number="localWorkUnit"
            :disabled="disabled"
            :value="unit"
            class="form-check-input"
            type="radio"
        />
        <label :for="'work_unit' + unit" class="form-check-label">{{ unit }}</label>
      </div>

      <!-- 사용자 입력 필드 -->
      <div class="input-group w-25">
        <span class="input-group-text">Custom:</span>
        <input
            v-model.number="localWorkUnit"
            :disabled="disabled"
            class="form-control"
            min="1"
            placeholder="Unit"
            type="number"
        />
      </div>
    </div>

    <!-- 정보 메시지 -->
    <div class="text-info mb-1">
      Each request to GPT processes {{ localWorkUnit }} items at a time.
    </div>
    <div class="text-dark mb-1">
      Total requests: {{ totalRequests }}
    </div>

    <!-- 경고 메시지 -->
    <div v-if="remainder !== 0" class="text-danger mb-1">
      {{ remainder }} items will remain in the last request.
    </div>
    <div v-if="localWorkUnit > localTotalSize" class="text-danger mb-1">
      The work unit size cannot exceed the total size.
    </div>
  </div>
</template>

<script>

export default {
  props: {
    batchJob: Object,
    work_unit: Number,
    fileType: String,
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    totalRequests() {
      return this.batchJob ? Math.ceil(this.localTotalSize / this.localWorkUnit) : 0;
    },
    remainder() {
      return this.localTotalSize % this.localWorkUnit;
    },

  },
  data() {
    return {
      localWorkUnit: this.work_unit,  // Initialize with the prop value
      localTotalSize: this.batchJob.total_size,
    };
  },
  watch: {
    // Watch the work_unit prop and sync it to localWorkUnit
    work_unit(newVal) {
      this.localWorkUnit = newVal;
    },
    localWorkUnit(newVal) {
      this.$emit('update:work_unit', newVal); // localWorkUnit이 변경되면 부모로 전달
    }
  },
};
</script>
