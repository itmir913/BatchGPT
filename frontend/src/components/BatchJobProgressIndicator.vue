<template>
  <div>
    <h1 class="text-center cursor-pointer hover-effect" @click="goToHome">BatchGPT</h1>

    <!-- 진행 상태 표시 -->
    <div class="progress-indicator d-flex justify-content-between my-4">
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
  computed: {
    steps() {
      return ["Create BatchJob", "Upload File", "Prompt Configs", "Previews", "Run Tasks"];
    },
  },
  methods: {
    goToHome() {
      this.$router.push('/home'); // Vue Router를 사용하여 /home으로 이동
    },

    getStepClass(index) {
      const stepClasses = ['step-future', 'step-past', 'step-current'];
      return stepClasses[this.currentStep === index ? 2 : index < this.currentStep ? 1 : 0];
    },

    getStepLink(index) {
      const stepLinks = [
        `/batch-jobs/create`,
        `/batch-jobs/${this.batch_id}`,
        `/batch-jobs/${this.batch_id}/configs`,
        `/batch-jobs/${this.batch_id}/preview`,
        `/batch-jobs/${this.batch_id}/run`,
      ];
      return stepLinks[index] || '/';
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

.cursor-pointer {
  cursor: pointer; /* 마우스 포인터가 손가락으로 바뀌도록 설정 */
}

.hover-effect {
  transition: color 0.3s ease, background-color 0.3s ease; /* 색상과 배경색 변화에 부드러운 전환 효과 추가 */
}

.hover-effect:hover {
  color: white; /* 호버 시 텍스트 색상 변경 */
  background-color: rgba(0, 123, 255, 0.7); /* 호버 시 배경색 변경 (Bootstrap의 primary 색상 사용) */
}
</style>
