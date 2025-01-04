<template>
  <div class="container mt-5">
    <!-- 인증된 사용자 -->
    <div v-if="isAuthenticated" class="alert alert-success text-center">
      <p>Welcome, {{ email }}!</p>
      <button class="btn btn-primary mt-3" @click="logout">Logout</button>
    </div>

    <!-- 인증되지 않은 사용자 -->
    <div v-else class="alert alert-warning text-center">
      <p>Please log in.</p>
    </div>
  </div>
</template>

<script>
import axios from '@/configs/axios';

export default {
  data() {
    return {
      isAuthenticated: false,
      email: '',
    };
  },
  async created() {
    try {
      const response = await axios.get('/api/auth/check/', {withCredentials: true});
      this.isAuthenticated = response.data.is_authenticated;
      this.email = response.data.email;
    } catch (error) {
      console.error('Error checking authentication:', error);
      this.isAuthenticated = false;
    }
  },
  methods: {
    async logout() {
      try {
        await axios.post('/api/auth/logout/', {}, {withCredentials: true});
        this.isAuthenticated = false;
        this.email = '';
        alert('You have been logged out.');
        await this.$router.push('/login');
      } catch (error) {
        console.error('Error during logout:', error);
        alert('Logout failed. Please try again.');
      }
    },
  },
};
</script>
