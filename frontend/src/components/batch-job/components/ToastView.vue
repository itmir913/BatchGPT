<template>
  <div class="toast-container position-fixed top-0 end-0 p-3">
    <div v-if="show" :class="toastClass" aria-atomic="true" aria-live="assertive" class="toast show" role="alert">
      <div class="toast-header">
        <strong class="me-auto">{{ title }}</strong>
        <button aria-label="Close" class="btn-close" type="button" @click="hideToast"></button>
      </div>
      <div class="toast-body text-white">
        {{ currentMessage }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    message: Object,
    delay: {
      type: Number,
      default: 7000
    }
  },
  data() {
    return {
      show: false,
      currentMessage: '',
      title: '',
      toastClass: 'bg-success',
      toastTimeout: null,
    };
  },
  methods: {
    showToast() {
      if (this.toastTimeout) {
        clearTimeout(this.toastTimeout);
      }
      this.show = true;
      this.toastTimeout = setTimeout(this.hideToast, this.delay);
    },
    hideToast() {
      this.show = false;
    },
    setMessage() {
      if (this.message.success) {
        this.title = "Success";
        this.currentMessage = this.message.success;
        this.toastClass = 'bg-success';
      } else if (this.message.error) {
        this.title = "Error";
        this.currentMessage = this.message.error;
        this.toastClass = 'bg-danger';
      }
    }
  },
  watch: {
    message: {
      handler() {
        this.setMessage();
        if (this.currentMessage) {
          this.showToast();
        }
      },
      deep: true
    }
  },
  mounted() {
    this.setMessage();
  }
};
</script>

<style scoped>
.toast-container {
  z-index: 1050;
}
</style>
