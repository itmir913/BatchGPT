<template>
  <div>
    <h2 class="mb-3">Select PDF Mode</h2>
    <div class="d-flex flex-wrap justify-content-center mb-3">
      <div v-for="mode in modes" :key="mode.key" class="form-check me-3">
        <input
            :id="mode.key"
            v-model="localSelectedMode"
            :disabled="disabled"
            :value="mode.key"
            class="form-check-input"
            type="radio"
        />
        <label :for="mode.key" class="text-dark mb-1">
          <strong>{{ mode.key }}</strong>: {{ mode.description }}
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import {PDFModeSupportedFileTypes} from '@/components/batch-job/utils/SupportedFileTypes';

export default {
  props: {
    fileType: String,
    supportedMode: {
      type: Object,
      required: true,
      default: () => ({modes: []}),
    },
    selectedMode: String,
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    supportedFileTypes() {
      return PDFModeSupportedFileTypes;
    },
    modes() {
      return this.supportedMode || [];
    },
  },
  data() {
    return {
      localSelectedMode: this.selectedMode,
    };
  },
  watch: {
    selectedMode(newVal) {
      this.localSelectedMode = newVal;
    },
    localSelectedMode(newVal) {
      this.$emit('update:selectedMode', newVal);
    },
  },
};
</script>
