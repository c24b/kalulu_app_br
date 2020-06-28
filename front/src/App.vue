<template>
  <div id="app">
    <!-- <app-header></app-header> -->
    <router-view></router-view>
  </div>
</template>

<script>
// import Header from './components/Header.vue'
import Buttons from './components/subComponents/Buttons.vue'

export default {
  name: 'app',  
  components: {
    //AppHeader: Header
    appButtons: Buttons
  },
  };
</script>

<style>
  @import './assets/kalulu.css';
  /* @import './assets/chapter.css'; */
</style>
