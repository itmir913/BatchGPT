<template>
  <nav v-show="!isAuthPage" class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link :to="{ name: 'Home' }" class="navbar-brand">BatchGPT</router-link>
      <button aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"
              class="navbar-toggler"
              data-bs-target="#navbarSupportedContent" data-bs-toggle="collapse" type="button"><span
          class="navbar-toggler-icon"></span></button>
      <div id="navbarSupportedContent" class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item"><a class="nav-link" href="https://github.com/itmir913/BatchGPT/"
                                  rel="noopener noreferrer"
                                  target="_blank">Github</a></li>
        </ul>
      </div>
    </div>
  </nav>
  <router-view v-slot="{ Component }">
    <transition>
      <component :is="Component"/>
    </transition>
  </router-view>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isAuthPage() {
      return this.$route.path === '/login' || this.$route.path === '/register';
    }
  },
}
</script>

<style>
html {
  overflow-y: scroll;
}
</style>
