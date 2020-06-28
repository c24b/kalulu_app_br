<template>
  <div>
    <aside id="navbar">
          <ul>
            <li><button class="btn" id="menu"><a href="/">
            <img src="/src/assets/img/button_back_to_menu_up.png" width="60px"  alt="" /></a></button></li>
            <li>
              <button class="btn" id="back" @click='$router.go(-1)'>
              <img src="/src/assets/img/button_back_up.png" width="60px"  alt="" />
              </button>
            </li>
          </ul>
    </aside>
    <header>
    <h2 class="heading" v-if="status=='ready'">
         Matrice de confusion <br>entre 
         
         <b-button size="lg" pill variant="primary">
          <h3>{{subject_name}}</h3>
          </b-button> 
          pour <b-button pill size="lg" variant="info"><h3>{{student_name}}</h3></b-button> 
         
    </h2>
    <h2 class="heading" v-else>
         Matrice de Confusion 
    </h2>
    </header>
    
    <main>
    <div class="widget-container">
      <b-row>
        <b-col></b-col>
        <b-col>
      <article v-if="status=='ready'" class="widget text2 center">
          
          <div id="subject_radio1" v-if='subject=="numbers"'>
            <label>
              <input class="btn btn-space" @change="update" v-model="subject" type="radio"  value="letters" name="optsubject">
              Lettres
              </label>
            <label>
              <input class="btn btn-space" v-model="subject" type="radio"  value="numbers" name="optsubject" checked>
              Nombres
            </label>
          </div>
          <div id="subject_radio" v-else>
            <label>
              <input class="btn btn-space" v-model="subject" type="radio"  value="letters" name="optsubject" checked>
              Lettres
              </label>
            <label>
              <input class="btn btn-space" @change=update v-model="subject" type="radio"  value="numbers" name="optsubject" >
              Nombres
            </label>
          </div>
          <div id="student_radio" v-if="student=='all'">
            <label>
              <input class="btn btn-primary btn-lg active" role="button"  type="radio" v-model="student" value="all" name="optstudent" checked>
              Tous les élèves
            </label>
          </div>
      
          <div id="subject_radio2"  v-else>
            
            <label>
              <input class="btn btn-space" v-model="student" type="radio" :value="student" name="optstudent1" checked>
              {{student_name}}
            </label>
            <label>
              <input class="btn btn-space" @change="update" v-model="student" type="radio" value="all" name="optstudent1" checked>
              Tous les élèves
            </label>
          </div>
      </article>
      </b-col>
      <b-col>
      </b-col>
      </b-row>
    </div>
    <article>
    <app-widget type="AppHeatmapsSlider"
          :status="status"
          :response="data"
          :title="title"
          main_access="True"
          id=22
    >
    </app-widget>
    </article>
    </main>
    </div>    
</template>

<script>
import Spinner from './subComponents/Spinner.vue'
import widget from './subComponents/Widget.vue'
import services from '../services.js'
// When the page is loaded, the API is always called using the endPoint decided in endPoint_c
// Case 1. If the URL doesn't contain any query, it is considered the "welcome screen". The 'globalConfusion' endpoint name is returned by 'endPoint_c', and fetched in 'mounted'. 
// Case 2. If the URL does contain a query with a "student_no" parameter, the value for "student_no" is fetched with the 'studentConfusion' endpoint
// The form where the user can input a student number will simply redirect to this page and the "student_no" provided by the user will be included as a query parameter (triggering case 2)
// Form validation and error messages are handled by api response
// Student number validation via the /admin/students/ endpoint is yet to be implemented

export default {
  data: function(){
    return{
      student: this.$route.params.stid,
      subject: this.$route.params.sub,
      student_options: [
          { value: this.$route.params.stid, text: 'Elève n°'+ this.$route.params.stid},
          { value: 'all', text: 'tous les élèves' }
      ],
      subject_options: [
          { value: 'numbers', text: 'Nombres' },
          { value: 'letters', text: 'Lettres' },
      ],
      subject_name: "",
      student_name: "",
      theme_name: "",
      endPoint: "globalConfusion",
      status : 'loading',
      data : null, 
      msg: null,
      response: null,
      title: 'Confusion'
      
    }
  },
   methods:{
     update(){
      
       this.pageName = "confusion"
        this.path = "/confusion"
      console.log("UPDATE", this.student, this.subject)
       if (this.student == "all"){
         
         this.pageName = "confusionSubject"
         this.path = "/confusion/subject/"+this.subject
       }
       else {
         this.pageName= "confusionStudentSubject"
         this.path = "/confusion/subject/"+this.subject+"/student/"+this.student
       }
       console.log(this.path)
      this.$router.push({
          path: this.path
          // name: this.pageName
      })
      this.$router.go(this.path)
     }
     
  },    
  //   submit(){
  //     // This function is triggered by the "show graphs" button. Every time you press it, you are forwarded to this same confusion page, and the URL now contains the student number 
  //     this.$router.push({
        
  //       name: 'confusion/subject/'+this.subject+"/student/"+this.student,
        
  //     })
  //     this.$router.go()
  //   },
  // },
  components: {
    appWidget: widget,
    appSpinner: Spinner
  },
  async mounted() {
    this.status = "loading"
    this.subject_name = "Lettres"
    console.log("SELECTED", this.student_selected, this.subject_selected)
    console.log("SUBJECT", this.subject)
    if (typeof this.subject == 'undefined') {
        this.subject = 'letters'
        this.subject_name = "Lettres"
      }
    if (this.subject == "letters") {
      this.subject_name = 'lettres'
      this.title = "Confusion entre lettres"
      this.theme_name = "Français"
    }
    if (this.subject == "numbers")  {
      this.subject_name = 'Nombres'
      this.title = "Confusion entre nombres"
      this.theme_name = "Maths"
    }
    if (typeof this.student == 'undefined'){
        this.student = 'all'
        this.student_name = 'tous les élèves' 
        this.endPoint = "globalConfusion"  
        }
    else {
        this.endPoint= "studentConfusion"
        this.student_name = "l'élève n°"+this.student 
      }   
    console.log("ENDPOINT", this.endPoint, "SUBJECT", this.subject, "STUDENT", this.student)
    console.log("SUBJECT_name", this.subject_name, "STUDENT_name", this.student_name)
    let uri = services.buildUri(
      {
        'endPoint': this.endPoint, 
        'students': this.student,
        'subjects': this.subject
      }  
    )
    this.api_response = await services.getData(uri)
    this.status = this.api_response[2]
    this.data = this.api_response[1]
    this.response = this.api_response[0]
    this.title = "Confusion entre " + this.subject_name

    // console.log("RESPONSE", this.response)
    // console.log("DATA", this.data)
    // console.log("STATUS", this.status)
    
    },  
  
};
    
</script>

<style >


</style>