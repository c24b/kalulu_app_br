<template>
<div>
  <header style="display:block">
    <b-row>
    <b-col cols=1>
      <ul class="nav flex-column">
        <li class="nav-item">
          <button class="btn" id="menu">
            <a href="/">
                <img src="/src/assets/img/button_back_to_menu_up.png" width="60px"  alt="" />
            </a>
          </button>
        </li>
        <li class="nav-item">
          <button class="btn" id="back" @click='$router.go(-1)'>
            <img src="/src/assets/img/button_back_up.png" width="60px"  alt="" />
          </button>
        </li>
        </ul>
      </b-col>
      <b-col cols=3>
        </b-col>
      <b-col cols=8>
        <b-row>
        
          <app-widget class="widget" type="" 
      :title ="widgets.studentCheck.title" 
      :status="widgets.studentCheck.status" 
      :response="widgets.studentCheck.data" 
      :msg="widgets.studentCheck.message"
      > 
      </app-widget>
      <span v-if="widgets.studentCheck.status == 'ready'"> 
      <app-widget type="AppStudentInfo"
            :title ="widgets.studentCheck.title"
            :status="widgets.studentInfo.status"
            :response="widgets.studentInfo.data"
            :msg="widgets.studentInfo.message"
            id="popover-1"
            > 
        </app-widget> 
      </span>
      </b-row>
      </b-col>
      <b-col cols=2>
        </b-col>
    </b-row>
    <!-- <header>
    <app-widget class="widget" type="" 
      :title ="widgets.studentCheck.title" 
      :status="widgets.studentCheck.status" 
      :response="widgets.studentCheck.data" 
      :msg="widgets.studentCheck.message"
      > 
      </app-widget>
      <span v-if="widgets.studentCheck.status == 'ready'"> 
      <app-widget type="AppStudentInfo"
            :title ="widgets.studentCheck.title"
            :status="widgets.studentInfo.status"
            :response="widgets.studentInfo.data"
            :msg="widgets.studentInfo.message"
            id="popover-1"
            > 
        </app-widget> 
      </span>
    </header> -->
    </header>
    <main v-if="widgets.studentCheck.status == 'ready'">
      
      <div class="widget-list"> 
          <div id="tokens1" :class="token_style[subjectChosen]">
            <app-widget :type="tokens_or_digits[subjectChosen]"
              :title ="widgets.studentCheck.title"
              :status="widgets.studentTokens1.status"
              :response="widgets.studentTokens1.data"
              :msg="widgets.studentTokens1.message"
              id="popover-2"
              > </app-widget>
          </div>
          <div id="tokens2" :class="token_style[subjectChosen]">
            <app-widget :type="tokens_or_digits[subjectChosen]"
              :title ="widgets.studentCheck.title"
              :status="widgets.studentTokens2.status"
              :response="widgets.studentTokens2.data"
              :msg="widgets.studentTokens2.message"
              id="popover-3"
              > </app-widget>
          </div>
          <div id="tokens3" class="col-4 block" v-if="subjectChosen=='numbers'">
            <app-widget :type="tokens_or_digits[subjectChosen]"
              :title ="widgets.studentCheck.title"
              :status="widgets.studentTokens3.status"
              :response="widgets.studentTokens3.data"
              :msg="widgets.studentTokens3.message"
              id="popover-4"
              >
               </app-widget>
          </div>
      </div>
      <app-widget type="AppStudentLastLesson"
          :title ="widgets.studentCheck.title"
          :status="widgets.studentLastLesson.status"
          :response="widgets.studentLastLesson.data"
          :msg="widgets.studentLastLesson.message"
          id="popover-5"
          > 
          </app-widget>
      <app-widget type="AppHeatmapsSlider"
            :title ="widgets.studentCheck.title"
            :status="widgets.studentConfusion.status"
            :response="widgets.studentConfusion.data"
            :msg="widgets.studentLastLesson.message"
            id="popover-6"
            > 
      </app-widget>
        <app-widget :type="decision_type[subjectChosen]"
          :title ="widgets.studentCheck.title"
          :status="widgets.studentDecision.status"
          :response="widgets.studentDecision.data"
          :msg="widgets.studentLastLesson.message"
          id="popover-7"
          > 
        </app-widget>
      
      </main>
      <footer></footer>
  </div>
</template>

<script>
import services from '../services.js'
import widget from './subComponents/Widget.vue'
import error from './subComponents/Error.vue'
export default {
  data: function() {
    return {
      studentChosen: this.$route.params.stid,
      subjectChosen: this.$route.params.sub,
      response: null,
      api_response:  [null, null, null],
      status: "loading",
      widgets : { 
        // Removing the subject key from 'token' prevents calling this endpoint for the subject 
        studentCheck:      {response: {}, status: null, message: null, token: {letters: null, numbers: null}},
        studentInfo:       {response: {}, status: null, message: null, token: {letters: null, numbers: null}},
        studentTokens1:    {response: {}, status: null, message: null, token: {letters:'words', numbers: 'identification'}},
        studentTokens2:    {response: {}, status: null, message: null, token: {letters:'syllabs', numbers: 'counting'}},
        studentTokens3:    {response: {}, status: null, message: null, token: {numbers: 'association'}},
        studentLastLesson: {response: {}, status: null, message: null, token: {letters: null, numbers: null}},
        studentConfusion:  {response: {}, status: null, message: null, token: {letters: null, numbers: null}},
        studentDecision:   {response: {}, status: null, message: null, token: {letters: null, numbers: null}},
      },
      token_style:      {letters: 'col-6 block', numbers:'col-4 block'},
      tokens_or_digits: {letters: 'AppStudentTokens', numbers: 'AppStudentDigits'},
      decision_type:    {letters: 'AppStudentLexicalDecision', numbers: 'AppStudentDigitalDecision'}
    }
  },

  components: {
    appWidget: widget,
    appError: error
    
  },

  methods: {
    async call(endPoint, uri){
      this.widgets[endPoint].status = 'loading'
      this.api_response = await services.getData(uri)
      this.response = await this.api_response[0]
      this.data = this.api_response[1]
      this.widgets[endPoint].response = this.api_response[0]
      this.widgets[endPoint].data = this.api_response[1]
      this.widgets[endPoint].status = this.api_response[2]
      this.widgets[endPoint].title = this.widgets[endPoint].data.title
      this.widgets[endPoint].message = this.widgets[endPoint].data.message 
    }
    //   if (this.widgets[endPoint].response[0] == false){
    //     this.widgets[endPoint].status = 'error'

    //     // console.log(this.widgets[endPoint].response[1])
    //     let msg = this.widgets[endPoint].response[1].data.message.split(".")[0]
    //     // this.widgets[endPoint].title = endpoint + studentChosen + subjectChosen
    //     this.widgets[endPoint].msg = msg
    //     this.widgets[endPoint].response = this.widgets[endPoint].response[1]
         
    //   } else {
    //     // console.log("WIDGET VALUES", this.widgets[endPoint].response)
    //     this.widgets[endPoint].status = 'ready'
    //     // this.widgets[endPoint].msg = "Ok"
    //     this.widgets[endPoint].title = this.widgets[endPoint].response[1].data.title
    //     this.widgets[endPoint].response = this.widgets[endPoint].response[1]
        
    //   }
    // }
  },

  async mounted() {
    // 1. Check if the student exists
    let student_check_uri = services.buildUri({
      'endPoint':'checkStudent', 
      'students': this.studentChosen
    })
    await this.call('studentCheck', student_check_uri)
    
    // 2. If it does, download API data for every widget that has this subject under "token":
    if (this.widgets.studentCheck.status != 'error'){
      // for (let endPoint in this.widgets) {this.widgets[endPoint].status = "loading"}
      for (let endPoint in this.widgets){
        if ( this.subjectChosen in this.widgets[endPoint].token && endPoint != 'studentCheck') {
          let uri = services.buildUri({
            'endPoint': endPoint, 
            'subjects': this.subjectChosen,
            'students': this.studentChosen,
            'tokenType': this.widgets[endPoint].token[this.subjectChosen]
          })
          console.log(endPoint, uri)
          await this.call(endPoint, uri)
          // console.log('<<< LOAD API DATA RESULT: ', key, this.response[key])
        }
      }
    }
  }
}
</script>
<style>

article#last_lesson >> .apexcharts-xaxis{
  font-size: 42px;
  color: white;
  font-weight: bolder;
}


</style>