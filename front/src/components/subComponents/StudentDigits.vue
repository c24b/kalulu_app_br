<template class="skills digits">
    <article class="widget text2">
      <app-buttons  :title="st_data.title" :doc="st_data.doc" :id="id"></app-buttons>
      
      <div class="content">
      <h2 class="heading">{{st_data.title}}</h2>
      <!-- counting: caterpillar -->
      <span v-for="(img,size) in imgs" :key="img"> 
        <img src:="img" :alt="title" width:=size>
      </span>
      <!--counting: caterpillar -->
      <img v-if="st_data.title=='Je compte'" src="/src/assets/img/gauge_icon_caterpillar_full.png" :alt="title" width="300">
      
      <!-- identification: ants +turtle -->
      <img v-if="st_data.title=='J\'associe un nombre avec une quantité'" src="/src/assets/img/gauge_icon_ant_full.png" :alt="title" width="150">
      <img v-if="st_data.title=='J\'associe un nombre avec une quantité'" src="/src/assets/img/gauge_icon_turtle_full.png" :alt="title" width="150">
      <!-- association: jellyfish + crabs -->
      <img v-if="st_data.title=='J\'entends et je trouve'" src="/src/assets/img/gauge_icon_jellyfish_full.png" :alt="title" width="150">
      <img v-if="st_data.title=='J\'entends et je trouve'" src="/src/assets/img/gauge_icon_crab_full.png" :alt="title" width="150">
       
      <p v-if="tokens.length == 0" class="error">L'élève n'a pas encore vu de {{title.toLowerCase()}}.</p>
      <p v-if="tokens.length != 0">
      <span :class="ref_colors[tokens[0]['color']]"> {{tokens[0]['%CA']}}%</span> &nbsp;
      de bonnes réponses</p>
      </div>
    </article>
    
  </div>
</template>

<script>
import Buttons from './Buttons.vue'

export default {
  data: function(){
    return{
      ref_colors : {
        'green':'badge badge-success', 
        'orange':'badge badge-warning', 
        'red':'badge badge-danger', 
      }
    }
  },
  computed: {
    tokens(){
      return this.st_data.data
    },
    // title(){
    //   return this.st_data.title
    // }
  },
  props: [
    'st_data', 
    'doc', 
    'title',
    'id'
  ],
  components:{
    appButtons: Buttons
  }
}
</script>

<style scoped>
/* Special case for association: title too long */
div.widget-list article div.heading{
  margin:0;
}
div.widget-list article div.heading{
  font-size: 20px;
  vertical-align: middle;
  margin:5px;
}
</style>