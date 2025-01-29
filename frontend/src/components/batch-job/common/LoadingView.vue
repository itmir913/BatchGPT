<template>
  <div v-if="loading" class="text-center mb-3">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p>{{ loadingMessage }}</p>
  </div>
</template>

<script>
import {CONFIRM_MESSAGE} from '@/components/batch-job/utils/BatchJobUtils';

export default {
  props: {
    loading: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    loadingMessage() {
      return CONFIRM_MESSAGE.loadingMessage;
    },
  },
};
</script>
