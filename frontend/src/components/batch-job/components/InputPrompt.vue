<template>
  <div class="mb-3 g-3 p-2">
    <h2 class="mb-3">Input Prompt</h2>
    <textarea
        v-model="localPrompt"
        class="form-control"
        placeholder="Enter your prompt..."
        rows="5"
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
    prompt(newVal) {
      this.localPrompt = newVal;
    },
    localPrompt(newVal) {
      this.$emit('update:prompt', newVal);
    },
  },
};
</script>

