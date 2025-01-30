<template>
  <div aria-atomic="true" aria-live="polite" class="bg-dark position-relative bd-example-toasts">
    <div id="toastPlacement" class="toast-container position-absolute top-0 end-0 p-3">
      <div
          v-for="toast in toasts.values()"
          :key="toast.id"
          ref="toastRefs"
          :class="toast.class"
          class="toast"
          role="alert"
      >
        <div class="toast-header d-flex justify-content-between w-100">
          <strong class="me-auto">{{ toast.title }}</strong>
          <span class="text-muted" style="font-size: 0.8rem;">{{ toast.timestamp }}</span>
          <button aria-label="Close" class="btn-close" type="button" @click="removeToast(toast.id)"></button>
        </div>
        <div class="toast-body text-white">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {Toast} from "bootstrap";

export default {
  props: {
    message: Object,
    delay: {
      type: Number,
      default: 7000,
    },
  },
  data() {
    return {
      toasts: new Map(),
      toastInstances: new Map(),
      nextId: 1,
    };
  },
  watch: {
    message: {
      handler(newMessage) {
        if (newMessage && (newMessage.success || newMessage.error)) {
          this.addToast(newMessage);
        }
      },
      deep: true,
    },
  },
  methods: {
    addToast(msg) {
      const toastId = this.nextId++;

      const currentTime = new Date();
      const timestamp = currentTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});

      this.toasts.set(toastId, {
        id: toastId,
        title: msg.success ? "Success" : "Error",
        message: msg.success || msg.error,
        class: msg.success ? "bg-success" : "bg-danger",
        timestamp: timestamp,
      });

      this.$nextTick(() => {
        const lastToast = this.$refs.toastRefs[this.$refs.toastRefs.length - 1];
        if (lastToast) {
          const toastInstance = new Toast(lastToast, {
            delay: this.delay,
            autohide: true,
          });

          this.toastInstances.set(toastId, toastInstance);
          toastInstance.show();

          const onToastHidden = () => {
            this.removeToast(toastId);
            lastToast.removeEventListener("hidden.bs.toast", onToastHidden);
          };

          lastToast.addEventListener("hidden.bs.toast", onToastHidden);
        }
      });
    },
    removeToast(id) {
      this.toasts.delete(id);
      const toastInstance = this.toastInstances.get(id);
      if (toastInstance) {
        toastInstance.hide();
        this.toastInstances.delete(id);
      }
    },
  },
};
</script>

<style scoped>
.toast-container {
  z-index: 1050;
}
</style>
