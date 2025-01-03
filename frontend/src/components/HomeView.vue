<template>
  <div>
    <p v-if="isAuthenticated">Welcome, {{ email }}!</p>
    <button v-if="isAuthenticated" @click="logout">Logout</button>
    <p v-else>Please log in.</p>
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
