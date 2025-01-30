<template>
  <ToastView
      ref="toast"
      :message="messages"
  />
  <div id="login" class="wrapper d-flex align-items-center justify-content-center vh-100">
    <div class="card shadow-lg" style="max-width: 400px; width: 100%;">
      <div class="card-body p-4">
        <h2 class="text-center mb-4">Login</h2>
        <form @submit.prevent="login">
          <div class="mb-3">
            <label class="form-label" for="email">Email</label>
            <input
                id="email"
                v-model="email"
                :class="{ 'is-invalid': email && !isEmailValid }"
                class="form-control"
                placeholder="Please enter your email."
                required
                type="email"
            />
            <div v-if="email && !isEmailValid" class="invalid-feedback">
              {{ ERROR_MESSAGES.ERROR_INVALID_EMAIL }}
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label" for="password">Password</label>
            <input
                id="password"
                v-model="password"
                class="form-control"
                placeholder="Please enter your password."
                required
                type="password"
            />
          </div>

          <button :disabled="isButtonDisabled" class="btn btn-primary w-100 py-2" type="submit">
            Login
          </button>
        </form>

        <div class="text-center mt-3">
          <p>
            Don't have an account?
            <router-link class="link text-primary" to="/register">Sign up</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrapper {
  background-color: #f8f9fa;
}

.card {
  border-radius: 15px;
}

.card-body {
  padding: 30px;
}

h2 {
  font-size: 1.8rem;
  color: #333;
}

label {
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
}

input[type="email"],
input[type="password"] {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

input[type="email"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #66a6ff;
}

input.is-invalid {
  border-color: red;
}

.invalid-feedback {
  font-size: 0.875em;
  color: red;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 10px;
  border-radius: 5px;
  border: none;
}

button:hover {
  background-color: #45a049;
}

@media (max-width: 576px) {
  .card-body {
    padding: 20px;
  }

  h2 {
    font-size: 1.5rem;
  }
}
</style>

<script>
import {ERROR_MESSAGES, loginAPI, SUCCESS_MESSAGES} from "@/components/auth/AuthUtils";
import ToastView from "@/components/batch-job/common/ToastView.vue";
import {getErrorMessage} from "@/components/batch-job/utils/CommonFunctions";

export default {
  components: {ToastView},
  data() {
    return {
      email: '',
      password: '',
      error: null,
      success: null,
      isButtonDisabled: false,
      messages: {success: null, error: null},
    };
  },
  computed: {
    ERROR_MESSAGES() {
      return ERROR_MESSAGES
    },
    isEmailValid() {
      const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      return regex.test(this.email);
    },
  },
  methods: {
    clearMessages() {
      this.messages = {success: null, error: null};
    },

    handleMessages(type, message) {
      this.clearMessages();
      this.messages[type] = message;
    },

    async login() {
      if (!this.isEmailValid) {
        this.handleMessages('error', ERROR_MESSAGES.ERROR_INVALID_EMAIL)
        return;
      }

      this.isButtonDisabled = true;

      try {
        const response = await loginAPI(this.email, this.password);

        if (!response) {
          this.handleMessages('error', ERROR_MESSAGES.ERROR_NOT_RESPONSE)
          return;
        }

        this.handleMessages('success', SUCCESS_MESSAGES.SUCCESS_LOGIN)

        setTimeout(() => {
          this.$router.push('/home');
        }, 1000);

      } catch (error) {
        this.isButtonDisabled = false;
        const errorMessage = getErrorMessage(error, `${ERROR_MESSAGES.ERROR_CANNOT_LOGIN}`);
        this.handleMessages("error", errorMessage);
      }
    },
  },
};
</script>
