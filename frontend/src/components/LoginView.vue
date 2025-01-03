<template>
  <div id="login" class="wrapper">
    <div class="container">
      <h2>로그인</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">이메일</label>
          <input
              id="email"
              v-model="email"
              placeholder="이메일을 입력하세요"
              required
              type="email"
          />
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
              id="password"
              v-model="password"
              placeholder="비밀번호를 입력하세요"
              required
              type="password"
          />
        </div>
        <button class="submit-button" type="submit">로그인</button>
      </form>

      <!-- 회원가입 링크 추가 -->
      <div class="register-link">
        <p>계정이 없으신가요?
          <router-link class="link" to="/register">회원가입</router-link>
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
      password: ''
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

input[type='email'],
input[type='password'] {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

input[type='email']:focus,
input[type='password']:focus {
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
