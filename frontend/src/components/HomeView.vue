<template>
  <div>
    <p v-if="isAuthenticated">Welcome, {{ email }}!</p>
    <p v-else>Please log in.</p>
  </div>
</template>

<script>
import axios from 'axios';

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
};
</script>
