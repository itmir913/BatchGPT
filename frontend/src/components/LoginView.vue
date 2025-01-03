<template>
  <div id="login">
    <form @submit.prevent="login">
      <div>
        <label for="email">Email:</label>
        <input id="email" v-model="email" required type="email"/>
      </div>
      <div>
        <label for="password">Password:</label>
        <input id="password" v-model="password" required type="password"/>
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

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
        // 로그인 성공 후 처리 (예: 토큰 저장, 페이지 이동 등)
      } catch (error) {
        console.error('Login failed:', error.response?.data || error.message);
        // 에러 처리 (예: 사용자에게 알림 표시)
      }
    }
  }
};
</script>

<style scoped>
/* 스타일은 필요에 따라 추가 */
</style>
