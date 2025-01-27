<template>
  <!-- 배치 GPT 타이틀 -->
  <h1 class="text-center cursor-pointer hover-effect mb-3" @click="goToHome">BatchGPT</h1>

  <router-view></router-view>  <!-- 라우터 뷰 -->
</template>

<script>

export default {
  name: 'App',
  methods: {
    goToHome() {
      this.$router.push('/home'); // Vue Router를 사용하여 /home으로 이동
    },
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>

<style>
html {
  overflow-y: scroll; /* 항상 세로 스크롤바 표시 */
}

.cursor-pointer {
  cursor: pointer; /* 마우스 포인터가 손가락으로 바뀌도록 설정 */
}

.hover-effect {
  transition: color 0.3s ease, background-color 0.3s ease; /* 색상과 배경색 변화에 부드러운 전환 효과 추가 */
}

.hover-effect:hover {
  color: white; /* 호버 시 텍스트 색상 변경 */
  background-color: rgba(0, 123, 255, 0.7); /* 호버 시 배경색 변경 (Bootstrap의 primary 색상 사용) */
}
</style>