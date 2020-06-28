<template id="student_info">
<article class="widget text">
  <app-buttons  :id="id" title="Information sur l'élève" :doc="st_data.doc"></app-buttons>
       
        <h2 class="heading">Tablette n° <span class="badge-pill badge-danger"><b>{{st_data.tablet}}</b></span>
        <br>Groupe n° <span class="badge-pill badge-dark">{{st_data.kid}}</span>
        </h2>
      
        
      <p>
        a réussi <b-button class="badge" id="lesson-tooltip" style="background-color:#FFAF57">{{st_data.lesson}}</b-button> défis <br>dans <span class="badge badge-primary" style="background-color:#3F32A5;">{{st_data.chapter}}</span> jardins
        <br>
        en <span class="badge badge-secondary" style="background-color:#C3C2C4;">{{st_data.nb_days}}</span> jours,
        <br> pour un temps total de <span class="badge badge-info">{{st_data.timespent}}</span>

        
      </p>
      <b-popover  href="#" tabindex="0" v-b-tooltip.focus target="lesson-tooltip" triggers="hover focus click">
        <span v-if="st_data.tags.length == 1">
        La  notion abordée au cours de ce défi est 
        </span>
        <span v-else>
         Les notions abordées au cours de  ce défi sont </br>
        </span>
        
        <span v-for="item in st_data.tags" :key="item">
        <span class="badge badge-pill" style="font-size: 16px; background-color:#9670E0; color:white;"> {{item}} </span> &nbsp;
        </span>
        </b-popover>  
        
        </p>
        
        
</article>
</template>

<script>
import Buttons from './Buttons.vue'

export default {
  
  props: [
      'st_data',
      'id'
  ],
  components: {
    AppButtons: Buttons
  }
}
</script>

<style>
/* article {
  background-color: {{st_data.chapter_color}}
} */
</style>