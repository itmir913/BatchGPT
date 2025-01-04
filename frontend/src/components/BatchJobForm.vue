<template>
  <div>
    <!-- Form 시작 -->
    <form @submit.prevent="submitForm">
      <!-- Title 입력 -->
      <div class="mb-3">
        <label class="form-label" for="title">Title</label>
        <input
            id="title"
            v-model="localBatchJob.title"
            class="form-control"
            placeholder="Enter the title of the batch job"
            required
            type="text"
        />
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
        ></textarea>
      </div>

      <!-- Submit 버튼 -->
      <button class="btn btn-primary" type="submit">Done</button>
    </form>
  </div>
</template>

<script>
export default {
  props: {
    batchJob: { // v-model을 위한 value prop
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      localBatchJob: {...this.batchJob}, // 로컬 상태로 복사
    };
  },
  watch: {
    batchJob: {
      handler(newVal) {
        this.localBatchJob = {...newVal}; // 부모에서 전달된 값이 변경될 때 로컬 상태 업데이트
      },
      deep: true, // 객체의 깊은 변경 감지
    },
  },
  methods: {
    submitForm() {
      this.$emit('input', this.localBatchJob); // 부모에게 로컬 상태 전달 (v-model 동작)
    },
  },
};
</script>

<style scoped>
/* 추가 스타일 필요 시 여기에 작성 */
</style>
