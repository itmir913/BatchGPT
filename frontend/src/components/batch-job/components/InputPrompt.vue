<template>
  <div class="mb-3 g-3 p-2">
    <h3>Input Prompt</h3>
    <textarea
        v-model="localPrompt"
        class="form-control"
        placeholder="Enter your prompt..."
        rows="5"
        @input="updatePrompt"
    ></textarea>
  </div>
</template>

<script>
export default {
  props: {
    prompt: {
      type: String,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      localPrompt: this.prompt // props 값을 로컬 데이터로 복사
    };
  },
  watch: {
    // 부모로부터 변경 사항 감지
    prompt(newVal) {
      this.localPrompt = newVal;
    },
  },
  methods: {
    updatePrompt() {
      this.$emit('update:prompt', this.localPrompt); // 상위 컴포넌트로 값 전달
    }
  }
};
</script>

