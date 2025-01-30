<template>
  <div aria-atomic="true" aria-live="polite" class="bg-dark position-relative bd-example-toasts">
    <div id="toastPlacement" class="toast-container position-absolute top-0 end-0 p-3">
      <div id="myToast" :class="toastClass" class="toast">
        <div class="toast-header">
          <strong class="me-auto">{{ title }}</strong>
          <button aria-label="Close" class="btn-close" type="button" @click="hideToast"></button>
        </div>
        <div class="toast-body text-white">
          {{ currentMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {Toast} from 'bootstrap';

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
      currentMessage: '',
      title: '',
      toastClass: 'bg-success',
      myToast: null,
    };
  },
  methods: {
    showToast() {
      this.myToast.show();
    },
    hideToast() {
      this.myToast.hide();
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
    this.myToast = new Toast(document.getElementById('myToast'))
    this.setMessage();
  }
};
</script>

<style scoped>
.toast-container {
  z-index: 1050;
}
</style>
