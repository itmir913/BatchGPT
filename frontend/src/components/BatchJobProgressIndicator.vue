<template>
  <div class="progress-indicator d-flex justify-content-between mb-4">
    <div
        v-for="(step, index) in steps"
        :key="index"
        :class="['step', getStepClass(index)]"
    >
      <template v-if="index < currentStep">
        <a :href="getStepLink(index)" class="text-decoration-none text-primary">
          {{ step }}
        </a>
      </template>
      <template v-else>
        {{ step }}
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    currentStep: {
      type: Number,
      required: true,
    },
    batch_id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      steps: ["Create BatchJob", "Upload Files", "Prompt Config", "Previews", "Run Task"], // 워크플로우 단계
    };
  },
  methods: {
    getStepClass(index) {
      if (index === this.currentStep) return "step-current"; // 현재 단계
      if (index < this.currentStep) return "step-past"; // 이전 단계
      return "step-future"; // 이후 단계
    },
    getStepLink(index) {
      const stepLinks = {
        0: `/batch-jobs/create`,
        1: `/batch-jobs/${this.batch_id}`,
        2: "/batch-jobs/${this.batch_id}/prompt",
        3: "/batch-jobs/${this.batch_id}/preview",
        4: "/batch-jobs/${this.batch_id}/run",
      };
      return stepLinks[index] || `/`; // 기본값
    },
  },
};
</script>

<style scoped>
.progress-indicator {
  display: flex;
  justify-content: space-between;
}

.step {
  flex: 1;
  text-align: center;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.step + .step {
  margin-left: 10px;
}

.step-current {
  background-color: #007bff; /* 강조 색상 */
  color: white;
}

.step-past {
  background-color: #e9ecef; /* 흐림 없이 표시 */
}

.step-future {
  background-color: #f8f9fa; /* 흐리게 표시 */
  color: #6c757d; /* 흐린 텍스트 색상 */
}
</style>
