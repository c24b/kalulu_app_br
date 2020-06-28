<template class="skills tokens">
  
  
  <article id="box" class="widget text2">
  <app-buttons v-if="tokens.length > 0" :doc=st_data.doc :title=title :id=id> </app-buttons>
      
    <div :id=title>
    <h2  class="heading">
      <span class="badge badge-secondary" v-if="tokens.length > 0"> {{tokens.length}}</span>
           {{title}}
    </h2>
    
      <p v-if="tokens.length == 0">L'élève n'a pas encore vu de {{title.toLowerCase()}}.</p>
      <p>
      <span v-for="(token, i) in tokens" :key="i"> 
        <span :class="ref_colors[token.color]"> {{token.word}} </span> &nbsp;
      </span>
      </p>
    </div>
  <button @click="print" class="btn">
    <img src="/src/assets/img/print.jpeg" width="40px"  alt="Print" />
  </button>

  </article>
  
</template>

<script>
import Buttons from './Buttons.vue'

export default {
  data: function() {
    return {
      ref_colors : {
        'green':'badge badge-success', 
        'orange':'badge badge-warning', 
        'red':'badge badge-danger', 
      }
    }
  },
  computed:{
    tokens(){
      return this.st_data.data
    },
    title(){
      return this.st_data.title
    },
    
  },
  mounted: {
    
  },
  methods:{
    print(){
      console.log(this.st_data.title);
      this.$htmlToPaper(this.st_data.title);
    }
  },
  props: [
    'st_data',
    'id',
    
  ], 
  
  components:{
    appButtons: Buttons
  }
}




</script>

<style>

</style>