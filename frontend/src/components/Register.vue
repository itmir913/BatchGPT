<template>
  <div>
    <h2>회원가입</h2>
    <form @submit.prevent="register">
      <div>
        <label for="username">아이디:</label>
        <input v-model="username" id="username" required/>
      </div>
      <div>
        <label for="email">이메일:</label>
        <input v-model="email" id="email" type="email" required/>
      </div>
      <div>
        <label for="password">비밀번호:</label>
        <input v-model="password" id="password" type="password" required/>
      </div>
      <div>
        <label for="passwordConfirm">비밀번호 확인:</label>
        <input v-model="passwordConfirm" id="passwordConfirm" type="password" required/>
      </div>
      <button type="submit">회원가입</button>
      <p v-if="error">{{ error }}</p>
      <p v-if="success">{{ success }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

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
    };
  },
  methods: {
    async register() {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/register/', {
          username: this.username,
          email: this.email,
          password: this.password,
          password_confirm: this.passwordConfirm,
        });
        this.success = response.data.message;
        this.error = null;
      } catch (error) {
        this.error = error.response.data.errors;
        this.success = null;
      }
    },
  },
};
</script>

<style scoped>
/* 스타일을 세련되게 추가 */
form {
  max-width: 400px;
  margin: auto;
}

div {
  margin-bottom: 10px;
}

button {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
}

button:hover {
  background-color: #45a049;
}

p {
  color: red;
}

p.success {
  color: green;
}
</style>
