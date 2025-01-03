<template>
  <div>
    <p v-if="isAuthenticated">Welcome, {{ username }}!</p>
    <p v-else>Please log in.</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      isAuthenticated: false,
      username: '',
    };
  },
  async created() {
    try {
      const response = await axios.get('/api/auth/check/', {withCredentials: true});
      this.isAuthenticated = response.data.is_authenticated;
      this.username = response.data.username;
    } catch (error) {
      console.error('Error checking authentication:', error);
      this.isAuthenticated = false;
    }
  },
};
</script>
