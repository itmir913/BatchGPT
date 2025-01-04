<template>
  <div id="login" class="wrapper d-flex align-items-center justify-content-center vh-100">
    <div class="container" style="max-width: 400px;">
      <!-- 제목 -->
      <h2 class="text-center mb-4">로그인</h2>

      <!-- 오류 메시지 -->
      <div v-if="message" class="alert alert-danger text-center">
        {{ message }}
      </div>

      <!-- 로그인 폼 -->
      <form @submit.prevent="login">
        <!-- 이메일 입력 -->
        <div class="form-group mb-3">
          <label class="form-label" for="email">이메일</label>
          <input
              id="email"
              v-model="email"
              class="form-control"
              type="email"
              placeholder="이메일을 입력하세요"
              required
          />
        </div>

        <!-- 비밀번호 입력 -->
        <div class="form-group mb-3">
          <label class="form-label" for="password">비밀번호</label>
          <input
              id="password"
              v-model="password"
              class="form-control"
              type="password"
              placeholder="비밀번호를 입력하세요"
              required
          />
        </div>

        <!-- 로그인 버튼 -->
        <button class="btn btn-primary w-100" type="submit">로그인</button>
      </form>

      <!-- 회원가입 링크 -->
      <div class="register-link text-center mt-3">
        <p>
          계정이 없으신가요?
          <router-link class="link text-primary" to="/register">회원가입</router-link>
        </p>
      </div>
    </div>
  </div>
</template>


<script>
import axios from '@/configs/axios';

export default {
  data() {
    return {
      email: '',
      password: '',
      message: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('/api/auth/login/', {
          email: this.email,
          password: this.password
        });
        console.log('Login successful:', response.data);
        await this.$router.push('/home');
      } catch (error) {
        // 오류 처리
        if (error.response && error.response.data) {
          // 서버에서 반환된 오류 메시지 처리
          this.message = '존재하지 않는 계정입니다.';
        } else {
          // 네트워크 또는 기타 오류 처리
          this.message = '서버와 연결할 수 없습니다. 나중에 다시 시도해주세요.';
        }
        console.error('Login failed:', error.response?.data || error.message);
      }
    }
  }
};
</script>

<style scoped>
.wrapper {
  display: flex;
  justify-content: center; /* 가로 중앙 */
  align-items: center; /* 세로 중앙 */
  background-color: #f8f9fa; /* Bootstrap 기본 배경색 */
  height: 100vh; /* 화면 전체 높이 */
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
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

input[type="email"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #66a6ff;
}

.submit-button {
  width: calc(100% - 20px);
  background-color: #4caf50;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 5px;
}

.submit-button:hover {
  background-color: #45a049;
}
</style>