<template>
  <div class="wrapper">
    <div class="container">
      <h2 class="title">회원가입</h2>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="username">아이디:</label>
          <input id="username" v-model="username" placeholder="아이디를 입력하세요" required/>
        </div>
        <div class="form-group">
          <label for="email">이메일:</label>
          <input id="email" v-model="email" placeholder="이메일을 입력하세요" required type="email"/>
        </div>
        <div class="form-group">
          <label for="password">비밀번호:</label>
          <input id="password" v-model="password" placeholder="비밀번호를 입력하세요" required type="password"/>
        </div>
        <div class="form-group">
          <label for="passwordConfirm">비밀번호 확인:</label>
          <input id="passwordConfirm" v-model="passwordConfirm" placeholder="비밀번호를 다시 입력하세요" required type="password"/>
        </div>
        <button type="submit">회원가입</button>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>
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
    };
  },
  methods: {
    async register() {
      try {
        const response = await axios.post('/api/auth/register/', {
          username: this.username,
          email: this.email,
          password: this.password,
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
/* 부모 컨테이너 중앙 정렬 */
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
  width: calc(100% - 20px);
  padding: 10px;
  border-radius: 5px;
  border: solid #ccc thin;
}

input::placeholder {
  color: #aaa;
}

button {
  width: calc(100% - 20px);
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

