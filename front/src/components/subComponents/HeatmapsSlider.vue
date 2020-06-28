<template>
  <div class="widget-container">
  
  <app-buttons :doc=st_data.doc :title=title id=22> </app-buttons>
  <h2>Matrice de Confusion</h2>
    
  
  
  <div v-if="show_graphs">
    <div class="row justify-content-center">
      
        
      
      <a v-for="(serie, s_title) in series_current" :key="s_title">
        <div class="col">
          <app-heatmap
            :s_title=s_title
            :id="id"
            :chart_data="serie[0].serie" 
            :chart_name="title" 
            :chart_sub="chart_sub[s_title]" 
            :xaxis_label="data_separated[s_title].xaxis_label"
            :yaxis_label="data_separated[s_title].yaxis_label"
            :doc="st_data.doc"
            :chartW="chartW" 
            :chartH="chartH"
            :click_redirect_to="click_redirect_to"
          ></app-heatmap>
        </div>
      </a>
    </div>
    <div class="row justify-content-center">
      <div v-if="slider_enable" class="col-4">
        <b> Jardin n°<span class="badge badge-secondary">{{slider_value}}</span> </b>
        <div class="row justify-content-center" v-if="main_access"> 
          <div class="col-10">
            <vue-slider v-model="slider_value" :data="chapters" :process="false" :marks="true" @change="update_series_current"/>
          </div>
        </div>
      </div>
      <div v-else class="col-4">
        <div v-if="chapter_label_enable">
          <b> Jardin: <span class="badge badge-secondary">{{slider_value}}</span></b><br>
          <a v-if="main_access"> L'élève {{st_data.student}} a parcouru 1 seul jardin </a>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'
import Heatmap from './Heatmap.vue'
import Buttons from './Buttons.vue'



export default {
  
  data: function() {
    return {
      student: this.st_data.student,
      subject: this.st_data.subject,
      data_separated: {},
      series : {},
      series_current: {}, 
      chapters: [],
      slider_value: 1,
      slider_enable: true, 
      chapter_label_enable: true,
      chart_sub: {},
      show_graphs : false,
      chartW:0,
      chartH:0,
      // chartW: 1450,
      // chartH: 1700, 
      click_redirect_to: this.st_data.student,
      title: this.st_data.title
    }
  },
  methods:{
    load_series(raw_separated_data) {
      return raw_separated_data.map(chapter_data => {
        // console.log('>>>>> HeatmapsSlider.vue, load series, chapter_data', chapter_data)
        if (!chapter_data.chapter) {
          chapter_data.chapter = 1
          this.chapter_label_enable = false
          
          }
        // console.log('>> chapter_data.chapter', chapter_data.chapter)
        return {
          'chapter': chapter_data.chapter,
          'serie'  : chapter_data.matrix.map(matrix_data => {
            return ({
              'name': matrix_data[0] ,
              'data': matrix_data[1].map(pair => {
                if (pair[1] == null) {pair[1] = -0.1}
                return ({
                  'x' : pair[0].toString(),
                  'y' : pair[1]
                })
              })
            })
          })
        }
      })
    },

    update_series_current(){
      for (var [title, data] of Object.entries(this.data_separated)) {
        if (data.length == 0){
          this.series_current[title] = [{
            'chapter': this.slider_value, 
            'serie' : this.empty_graph_data()
          }]
          this.chart_sub[title] = 'No data available'
        } else {
          this.series_current[title] = this.series[title].filter(v => v.chapter == this.slider_value)
          this.chart_sub[title] = ""
        }
      }
    },

    empty_graph_data(){
      // console.log('>>>> empty_graph_data')
      var buffer = [];
      for (var i=0; i<7; i++) {
        var line = []
        for (var j=0; j<7; j++) {
          line.push({
            x:  '.',
            y:  -0.1
          })
        }
        buffer.push({ 
          name : '.',
          data : line
          })
      }
      return buffer
    }, 
  },
  components: {
    VueSlider, 
    appHeatmap: Heatmap,
    AppButtons: Buttons
  },
  props: [
    'st_data',
    'id',
    // 'limit_to_last', 
    // 'click_redirect_to' 
    'main_access'
  ],
  mounted() {
    // console.log("ST_DATA from props undeclared -st_data", this.st_data)
    // console.log(">>> HeatmapSlider.vue - st_data.data", this.st_data)
    // 1. Separate data in c/v if needed - here we'll take care of API errors
    // console.log('>>> HeatmapsSlider.vue - st_data.data.confusion', this.st_data.data.confusion)
    // console.log('>>> HeatmapsSlider.vue - st_data.confusion', this.st_data.confusion)
    this.st_data.titles.forEach(title_t => {
      // console.log("SEPARATION", title_t)
      this.data_separated[title_t] = this.st_data.confusion.find(v => v.title == title_t)
    });
    
    // console.log('>> HeatmapsSlider.vue - data_separated', this.data_separated)
    
    //2. Load the unified list of chapters for the slider
    // HOTFIX FOR DATA.CHAPTERS: BEGINNING
    if (this.st_data.chapters){
      this.chapters = this.st_data.chapters
      // console.log('>>> this.chapters', this.chapters)
      // console.log('>>> this.data.chapters', this.data.chapters)
      this.slider_value = this.chapters.slice(-1)[0]
    }
    // HOTFIX FOR DATA.CHAPTERS: END
    
    
    //3. Disable slider if only 1 value is present
    if (this.chapters.length <= 1) {this.slider_enable = false}; 

    //4. Load the data in Apex format
    for (var [title, data] of Object.entries(this.data_separated)) {
        
      // console.log("title", title, "data", data)
      
      this.series[title] = this.load_series(data.data)
      // console.log("SERIES for", title,  this.series[title])
      }
      
    
    // console.log('>> HeatmapsSlider.vue - data formatted', this.series)

    // 5. Load shown data: load the chapter currently selected in the slider 
    // + check if any graph is empty, if it is, fill it with some rows of 0s for aesthetic reasons
    // + add "No data available" subtitle 
    this.update_series_current()

    // 6. If the widget is loaded from "HeatmapsPage.vue", we need to deactivate click to redirect:
    // console.log('>> Hetmap main_access: ', this.main_access)
    if (this.main_access){
      this.click_redirect_to = null
    }

    // 7. Find graph size (S/M/L)
    // First we find the length of the largest axis: 
    let candidates = []
    this.st_data.confusion.forEach((v) => {
      v.data.forEach((w) => {
        candidates.push(w.yaxis.length)
        candidates.push(w.xaxis.length)
      })
    })
    let axis_max_len = Math.max(...candidates)
    // console.log('>> candidates', candidates)
    // console.log('>> axis_max_len', axis_max_len)
    // Now we define the sizes and font for each
    if (axis_max_len >= 0 && axis_max_len <= 33){
      this.chartW = 450,
      this.chartH = 500
    }
    if (axis_max_len > 33 && axis_max_len <= 66){
      this.chartW = 950,
      this.chartH = 1000
    }
    if (axis_max_len > 66){
      this.chartW = 1450,
      this.chartH = 1700
    }
    
    // all ready:
    this.show_graphs = true
}
};
</script>

<style>

</style>