<template>
<div class="widget-container">
  <!-- CHILD: PROP this.status {{status}}<br> -->
  <!-- CHILD: DATA: widget_status {{widget_status}} <br>  -->
  <!-- WIDGET.VUE: COMPUTED isready: {{status_c}}<br>  -->
  <!-- CHILD: API RESPONSE, DATA: {{response}}<br>  -->
  <!-- CHILD: API RESPONSE, PROP: {{response}}<br> -->
  <!-- WIDGET.VUE: API RESPONSE, COMPUTED: {{response_c.data}}<br>  -->

  <app-spinner v-if="status=='loading'">

  </app-spinner>
  
  <component 
    v-if="status=='ready'&&type!=''" 
    v-bind:is="type" 
    :st_data='response'
    :main_access='main_access'
    :id ='id'
  ></component>
  
    
  <b-alert v-else show variant="warning">
    <h4 class="alert-heading"><strong>Oups!</strong>{{response.title}}</h4>
    <p>
    Quelque chose s'est mal passé: 
    <blockquote>{{response.message.split('.')[0]}} </blockquote>    
    </p>
    <hr>
    <p class="mb-0">
      Vous pouvez toujours retournez à l'<a href="/">accueil</a> 
    </p>
  </b-alert>
  
 </div>
</template>

<script>
import StudentInfo from './StudentInfo.vue'
import StudentTokens from './StudentTokens.vue'
import StudentDigits from './StudentDigits.vue'
import StudentLexicalDecision from './StudentLexicalDecision.vue'
import StudentDigitalDecision from './StudentDigitalDecision.vue'
import StudentLastLesson from './StudentLastLesson.vue'
import StudentColsSlider from './StudentColsSlider.vue'
import HeatmapsSlider from './HeatmapsSlider.vue'
import Spinner from './Spinner.vue'
import ErrorScreen from './Error.vue'

export default {
  data: function(){
    return{
      response: null,
      status: "loading",
  //     api_response: [null, null, null],
  //     response: this.response,
  //     status: "loading",
  //     data: this.response,
  //     title: this.response.title,
  //     message: this.response.message,
      }
  },
  // computed: {
  //   status: function(){
  //     return this.response.status
  //   },
  //   response: function(){
  //     return this.response.data
  //   },
  //   title: function(){
  //     return this.response.title
  //   },
  //   message: function(){
  //     return this.response.message
  //   }
  // },
  //   response_c: function(){
  //     return this.response
    // },
    // msg: function(){
    //   return this.msg
    // },
    // title_c: function(){
    //   if ('title' in this.response){
    //     return this.response.title
    //   } else {
    //     return ''
    //   }
    // }
  // },
  components:{
    AppStudentLastLesson: StudentLastLesson, 
    AppStudentInfo: StudentInfo,
    AppStudentTokens: StudentTokens,
    AppStudentDigits: StudentDigits,
    AppStudentLexicalDecision: StudentLexicalDecision,
    AppStudentDigitalDecision: StudentDigitalDecision,
    AppHeatmapsSlider: HeatmapsSlider, 
    AppSpinner: Spinner, 
    // AppError: ErrorScreen,
    AppStudentColsSlider: StudentColsSlider
  },
  props: [
    'type',
    'status',
    'title',
    'msg',
    'response',
    'main_access',
    'id'
  ]
}
</script>

<style>

</style>