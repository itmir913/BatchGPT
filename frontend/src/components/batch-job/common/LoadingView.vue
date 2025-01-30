<template>
  <div class="text-center mb-3">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
import {CONFIRM_MESSAGE} from '@/components/batch-job/utils/BatchJobUtils';

export default {
  computed: {
    loadingMessage() {
      return CONFIRM_MESSAGE.loadingMessage;
    },
  },
};
</script>
