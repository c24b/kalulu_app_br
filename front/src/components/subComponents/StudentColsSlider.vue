<template id="student_decision">
  <div>
      <div class="box">
        <div class="widget" v-for="dataset in st_data_c.bars" :key="dataset.title">
            <app-columns
              class="widget graph" 
              :title="dataset.title"
              :xaxis_title="dataset.xaxis_label"
              :yaxis_title="dataset.yaxis_label"
              :xaxis_labels="dataset.xaxis_labels"
              :url_doc="st_data.doc"
              :url_csv="st_data.csv"
              :series="find_chapter_data(dataset.graph_data, slider_value)"
            > </app-columns>
          
        </div>
        </div>
    
    <article class="slider" style="">
        <div class="slider_info">
          <label class="chapter"> Jardin: <span class="badge badge-pill badge-info">{{slider_value}}</span></label>
        </div>
        <div class="slider_container"> 
            <vue-slider 
              v-model="slider_value" 
              :data="st_data.chapters" 
              :process="false" 
              :marks="true" 
            />
        </div>
    </article>
    
  </div>
</template>

<script>
import Columns from "./Columns.vue" 
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'
export default {
  data: function(){
    return {
      slider_value : 0,
      slider_enable: true,
      // data_by_chapter: []
    }
  },
  computed:{
    st_data_c(){
      return this.st_data
    },
  },
  components: {
    VueSlider, 
    AppColumns: Columns
  },
  props: [
    'st_data'
  ],
  methods: {
    find_chapter_data(dataset, chapter_no) {
      // console.log('>> dataset', dataset)
      let xx = []
      xx.push(dataset.find(v => {
        // console.log('>> v', v.chapter, chapter_no)
        return v.chapter == chapter_no
}      ))
      // console.log('>> dataset result ',xx[0])
      return xx[0].series
    }
  },
  created() {
    this.slider_value = Math.max(...this.st_data.chapters)
    // console.log('>> StudentColsSlider created, slider value, st_data_c: ', this.slider_value, this.st_data_c)
  }

}
</script>

<style>

</style>