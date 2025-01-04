<template>
  <div class="wrapper d-flex align-items-center justify-content-center vh-100">
    <div class="container" style="max-width: 500px;">
      <!-- 제목 -->
      <h2 class="text-center mb-4">회원가입</h2>

      <!-- 회원가입 폼 -->
      <form @submit.prevent="register">
        <!-- 아이디 입력 -->
        <div class="form-group mb-3">
          <label class="form-label" for="username">아이디</label>
          <input
              id="username"
              v-model="username"
              class="form-control"
              placeholder="아이디를 입력하세요"
              required
              type="text"
          />
        </div>

        <!-- 이메일 입력 -->
        <div class="form-group mb-3">
          <label class="form-label" for="email">이메일</label>
          <input
              id="email"
              v-model="email"
              class="form-control"
              placeholder="이메일을 입력하세요"
              required
              type="email"
          />
        </div>

        <!-- 비밀번호 입력 -->
        <div class="form-group mb-3">
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

        <!-- 비밀번호 확인 -->
        <div class="form-group mb-3">
          <label class="form-label" for="passwordConfirm">비밀번호 확인</label>
          <input
              id="passwordConfirm"
              v-model="passwordConfirm"
              class="form-control"
              placeholder="비밀번호를 다시 입력하세요"
              required
              type="password"
          />
        </div>

        <!-- 회원가입 버튼 -->
        <button :disabled="isButtonDisabled" class="btn btn-primary w-100" type="submit">회원가입</button>

        <!-- 에러 메시지 -->
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>

        <!-- 성공 메시지 -->
        <div v-if="success" class="alert alert-success mt-3">
          {{ success }}
        </div>
      </form>
    </div>
  </div>
</template>


<script>
import axios from '@/configs/axios';

export default {
  name: 'RegisterUser',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      passwordConfirm: '',
      error: null,
      success: null,
      isButtonDisabled: false,
    };
  },
  methods: {
    async register() {
      try {
        this.isButtonDisabled = true;
        if (this.password !== this.passwordConfirm) {
          this.error = "비밀번호를 올바르게 입력하세요.";
          return
        }

        const response = await axios.post('/api/auth/register/', {
          username: this.username,
          email: this.email,
          password: this.password,
        });
        this.success = response.data.message;
        this.error = null;

        // 3초 후 로그인 페이지로 이동
        setTimeout(() => {
          this.$router.push("/login");
        }, 1000);

      } catch (error) {
        this.isButtonDisabled = false;
        this.error = error.response.data.errors;
        this.success = null;
      }
    },
  },
};
</script>

<style scoped>
/* 부모 컨테이너 중앙 정렬 */
.wrapper {
  display: flex;
  justify-content: center; /* 가로 중앙 */
  align-items: center; /* 세로 중앙 */
  background-color: #f8f9fa; /* Bootstrap 기본 배경색 */
}

/* 카드 스타일 */
.container {
  max-width: 400px;
  width: 100%;
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
}

/* 제목 스타일 */
.title {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

/* 입력 필드와 버튼 스타일 */
.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

input {
  padding: 10px;
  border-radius: 5px;
  border: solid #ccc thin;
}

input::placeholder {
  color: #aaa;
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

/* 에러 및 성공 메시지 스타일 */
.error {
  color: red;
}

.success {
  color: green;
}
</style>

