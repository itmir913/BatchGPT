<template>
  <div class="progress-indicator-wrapper">
    <ul class="nav nav-pills flex-column my-3">
      <li v-for="(step, index) in steps" :key="index" class="nav-item">
        <router-link
            :class="['nav-link', getStepClass(index)]"
            :to="getComputedLink(index)"
            role="tab"
            v-bind:aria-selected="index === currentStep ? 'true' : 'false'"
        >
          {{ step }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import {BATCH_JOB_STATUS} from "@/components/batch-job/utils/BatchJobUtils";

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
    batch_status: {
      type: String,
    },
  },
  computed: {
    steps() {
      return ["Create BatchJob", "Upload File", "Configs", "Previews", "Run Tasks"];
    },
  },
  methods: {
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

    getComputedLink(index) {
      if (!this.batch_status) {
        return index <= this.currentStep ? this.getStepLink(index) : '#';
      }

      const statusLimits = {
        [BATCH_JOB_STATUS.CREATED]: 1,
        [BATCH_JOB_STATUS.UPLOADED]: 2,
        [BATCH_JOB_STATUS.CONFIGS]: 3,
        [BATCH_JOB_STATUS.PENDING]: 4,
        [BATCH_JOB_STATUS.IN_PROGRESS]: 4,
        [BATCH_JOB_STATUS.COMPLETED]: 4,
        [BATCH_JOB_STATUS.FAILED]: 4,
      };

      const maxAllowedIndex = statusLimits[this.batch_status] ?? 0;
      return index <= maxAllowedIndex ? this.getStepLink(index) : "#";
    },
  },
};
</script>

<style scoped>
.progress-indicator-wrapper {
  margin-bottom: 20px;
  overflow-x: auto; /* 수평 스크롤 허용 */
  -webkit-overflow-scrolling: touch; /* iOS에서 부드러운 스크롤 */
}

.nav-pills {
  display: flex;
  flex-direction: column;
  padding-left: 0;
}

.nav-item {
  margin-bottom: 10px;
}

.nav-link {
  background-color: #f8f9fa; /* 기본 배경색 */
  color: #495057; /* 기본 텍스트 색상 */
  padding: 10px 20px;
  border: 1px solid #ccc;
  text-align: left; /* 왼쪽 정렬 */
  font-weight: 600;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.nav-link:hover {
  transform: translateY(-5px);
}

.nav-link.active {
  background-color: #007bff; /* 활성화된 탭 배경색 */
  color: white; /* 텍스트 색상 */
}

.step-past {
  background-color: #d6d8db; /* 더 어두운 회색 배경 */
  color: #6c757d; /* 흐린 텍스트 색상 */
  border: 1px solid #ced4da; /* 좀 더 부드러운 경계선 */
}

.step-future {
  background-color: #f0f2f5; /* 더 밝은 흐린 배경 */
  color: #adb5bd; /* 밝은 회색 텍스트 색상 */
  border: 1px solid #ced4da; /* 경계선 색상 */
}

.step-current {
  background-color: #007bff; /* 활성화된 탭 색상 */
  color: white;
}
</style>
