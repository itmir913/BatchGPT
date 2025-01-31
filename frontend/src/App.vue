<template>
  <nav v-show="!isAuthPage" class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/home">BatchGPT</router-link>
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
    <transition
        name="custom-fade"
        @enter="enter"
        @leave="leave"
        @before-enter="beforeEnter"
    >
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
  methods: {
    beforeEnter(el) {
      el.style.opacity = 0;
    },
    enter(el, done) {
      el.offsetHeight;
      el.style.transition = 'opacity 1s ease-in-out';
      el.style.opacity = 1;
      done();
    },
    leave(el, done) {
      el.style.transition = 'opacity 1s ease-in-out';
      el.style.opacity = 0;
      done();
    }
  },
}
</script>

<style>
html {
  overflow-y: scroll;
}
</style>
