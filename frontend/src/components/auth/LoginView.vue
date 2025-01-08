<template>
  <div id="login" class="wrapper d-flex align-items-center justify-content-center vh-100">
    <div class="container" style="max-width: 400px;">
      <!-- 제목 -->
      <h2 class="text-center mb-4">로그인</h2>

      <!-- 메시지 -->
      <div v-if="message" :class="message.type" class="alert text-center mt-4" role="alert">
        {{ message.text }}
      </div>

      <!-- 로그인 폼 -->
      <form @submit.prevent="login">
        <!-- 이메일 입력 -->
        <div class="mb-3">
          <label class="form-label" for="email">이메일</label>
          <input
              id="email"
              v-model="email"
              :class="{ 'is-invalid': email && !isEmailValid }"
              class="form-control"
              placeholder="이메일을 입력하세요"
              required
              type="email"
          />
          <div v-if="email && !isEmailValid" class="invalid-feedback">
            올바른 이메일을 입력하세요.
          </div>
        </div>

        <!-- 비밀번호 입력 -->
        <div class="mb-3">
          <label class="form-label" for="password">비밀번호</label>
          <input
              id="password"
              v-model="password"
              class="form-control"
              placeholder="비밀번호를 입력하세요"
              required
              type="password"
          />
        </div>

        <!-- 로그인 버튼 -->
        <button :disabled="isButtonDisabled" class="btn btn-primary w-100" type="submit">
          로그인
        </button>
      </form>

      <!-- 회원가입 링크 -->
      <div class="text-center mt-3">
        <p>
          계정이 없으신가요?
          <router-link class="link text-primary" to="/register">회원가입</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>

import {loginAPI} from "@/components/auth/AuthUtils";

export default {
  data() {
    return {
      email: '',
      password: '',
      error: null,
      success: null,
      isButtonDisabled: false,
      message: null,
    };
  },
  computed: {
    isEmailValid() {
      // 이메일 형식 유효성 검사
      const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      return regex.test(this.email);
    },
  },
  methods: {
    async login() {
      if (!this.isEmailValid) {
        this.message = {type: 'alert-danger', text: '올바른 이메일을 입력하세요.'};
        return;
      }

      this.isButtonDisabled = true;

      try {
        const response = await loginAPI(this.email, this.password);

        if (!response) {
          this.message = {type: 'alert-danget', text: "서버로부터 응답을 받지 못했습니다."};
          return;
        }

        this.success = '로그인 성공!';
        this.message = {type: 'alert-success', text: this.success};

        // 로그인 성공 후 홈으로 리디렉션
        setTimeout(() => {
          this.$router.push('/home');
        }, 1000);
      } catch (error) {
        this.isButtonDisabled = false;
        // 서버 오류 처리
        if (error.response && error.response.data) {
          this.error = '존재하지 않는 계정입니다.';
        } else {
          this.error = '서버와 연결할 수 없습니다. 나중에 다시 시도해주세요.';
        }

        this.message = {type: 'alert-danger', text: this.error};
        console.error('Login failed:', error.response?.data || error.message);
      }
    },
  },
};
</script>

<style scoped>
.wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
}

.container {
  max-width: 400px;
  width: 100%;
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
}

h2 {
  text-align: center;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
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

.alert {
  margin-top: 15px;
}
</style>
