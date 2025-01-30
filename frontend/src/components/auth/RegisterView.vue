<template>
  <ToastView
      ref="toast"
      :message="messages"
  />
  <div class="wrapper d-flex align-items-center justify-content-center vh-100 bg-light">
    <div class="card" style="max-width: 500px; width: 100%;">
      <div class="card-body">
        <h2 class="text-center mb-4">Sign Up</h2>

        <form @submit.prevent="register">
          <div class="mb-3">
            <label class="form-label" for="username">Username</label>
            <input
                id="username"
                v-model="username"
                class="form-control"
                placeholder="Enter your username"
                required
                type="text"
            />
          </div>

          <div class="mb-3">
            <label class="form-label" for="email">Email</label>
            <input
                id="email"
                v-model="email"
                class="form-control"
                placeholder="Enter your email"
                required
                type="email"
            />
          </div>

          <div class="mb-3">
            <label class="form-label" for="password">Password</label>
            <input
                id="password"
                v-model="password"
                class="form-control"
                placeholder="Enter your password"
                required
                type="password"
            />
          </div>

          <div class="mb-3">
            <label class="form-label" for="passwordConfirm">Confirm Password</label>
            <input
                id="passwordConfirm"
                v-model="passwordConfirm"
                :class="{'is-invalid': passwordConfirm && passwordConfirm !== password}"
                class="form-control"
                placeholder="Re-enter your password"
                required
                type="password"
            />
            <div v-if="passwordConfirm && passwordConfirm !== password" class="invalid-feedback">
              Passwords do not match.
            </div>
          </div>

          <button :disabled="isButtonDisabled || !isFormValid" class="btn btn-primary w-100" type="submit">
            Sign Up
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
}

.card {
  margin: 0 auto;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.card-body {
  padding: 30px;
}

h2 {
  color: #333;
}

button {
  background-color: #4caf50;
  color: white;
  border-radius: 5px;
  border: none;
  padding: 10px;
}

button:hover {
  background-color: #45a049;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.alert {
  margin-top: 15px;
}
</style>

<script>
import {ERROR_MESSAGES, registerAPI} from "@/components/auth/AuthUtils";
import ToastView from "@/components/batch-job/common/ToastView.vue";
import {getErrorMessage} from "@/components/batch-job/utils/CommonFunctions";

export default {
  name: 'RegisterUser',
  components: {ToastView},
  data() {
    return {
      username: '',
      email: '',
      password: '',
      passwordConfirm: '',
      messages: {success: null, error: null},
      isButtonDisabled: false,
    };
  },
  computed: {
    isFormValid() {
      return this.password && this.passwordConfirm && this.password === this.passwordConfirm;
    }
  },
  methods: {
    clearMessages() {
      this.messages = {success: null, error: null};
    },

    handleMessages(type, message) {
      this.clearMessages();
      this.messages[type] = message;
    },

    async register() {
      try {
        this.isButtonDisabled = true;

        const response = await registerAPI(this.username, this.email, this.password);
        this.handleMessages('success', response.data.message)

        // Redirect to login page after 1 second
        setTimeout(() => {
          this.$router.push("/login");
        }, 1000);
      } catch (error) {
        this.isButtonDisabled = false;
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.ERROR_CANNOT_REGISTER}`);
        this.handleMessages("error", errorMessage);
      }
    },
  },
};
</script>
