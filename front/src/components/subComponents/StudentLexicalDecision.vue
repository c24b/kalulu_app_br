<template >
  <div class="">
  <article  id="decision" class="widget" style="background-color:teal;margin-bottom: 10px;
    opacity: 0.8;
    border-radius: 35px;">
    
      <app-buttons :doc="st_data.doc" :title="st_data.title" :id="id"></app-buttons>
      <h2 class="heading">{{st_data.title}}</h2>
      
      <apexchart class="content chart"
      
        style="margin-top:2%; margin-left:2%;"
        type="line"
        height="450"
        width="96%"
        :options="chartOptions"
        :series="series"
      />
    <article class="slider">
      <div class="">
        <label>
          Jardin n°
          <span class="badge badge-pill badge-info .chap2">{{value}}</span>
        </label>
      </div>
      <vue-slider
        class="vue-slider"
        v-model="value"
        :data="chapter_list"
        :process="false"
        :marks="true"
        @change="update_value"
      ></vue-slider>
    </article>
      
    </article>
    
</div>
</template>

<script>
import Buttons from "./Buttons.vue";
import VueSlider from "vue-slider-component";
import "vue-slider-component/theme/default.css";

export default {
  data: function() {
    return {
      // value: 1,
      series_all: {},
      chapter_list: [],
      series: [],
      chartOptions: {
        xaxis: {
          title: {
            text: this.st_data.xaxis_label,
            cssClass: "apexcharts-xaxis-title",
            style:{
              fontSize: '22px',
              fontColor: 'white'
            }
          },
          tickAmount: 1,
          min:2,
          
          labels:{
            style: {
              fontSize:"20px",
              fontWeight: "bold",
              cssClass: "strange-xaxis-title"
            },
            categories: [2, 3, 4, 5, 6],
            show:true,
            maxWidth: 20,
          }
        },
        yaxis: {
          // forceNiceScale: true,
          labels: {
            style:{
              fontSize: '16px',

            },
            formatter: value => {
              return value.toFixed(2);
            }
          },
          title: {
            text: this.st_data.yaxis_label,
            style:{
              fontSize: '22px',
              fontColor: 'white'
            },
            // cssClass: "apexcharts-yaxis-title"
          }
        },
        chart: {
          // height: 400,
          zoom: {
            enabled: false
          },
          animations: {
            enabled: true,
            easing: "easeinout",
            speed: 200
          },
          fontFamily: "Avenir, Helvetica, Arial, sans-serif",
          toolbar: {
            show: false
            
            }
          
        },
        dataLabels: {
          enabled: false
        },
        colors: ["#A52A2A", "#407060"],
        markers: {
          size: 10
        },
        stroke: {
          curve: "straight"
        },
        grid: {
          row: {
            colors: ["#f3f3f3", "white"], // takes an array which will be repeated on columns
            opacity: 1
          }
          // padding: {
          //   top: 20,
          //   right: 20,
          //   bottom: 0,
          //   left: 20
          // }
        },
        legend: {
          show: true,
          // position: 'down',
          // horizontalAlign: 'right',
          floating: false,
          offsetX: 50,
          offsetY: -10
        }
      }
    };
  },
  methods: {
    update_value() {
      this.series = this.series_all[this.value];
      // console.log('>>>>>>>>>>>',this.series)
      // var ch_possible = Object.keys(this.series[0]).concat(Object.keys(this.series[1]))
      // var ch_unique  = [... new Set(ch_possible)]
      // this.chartOptions.xaxis.categories = ch_unique.sort()
    },

    load_graph_data(raw_data) {
      for (let chapter_no in raw_data) {
        let new_chapter_no = chapter_no;
        if (chapter_no == "average") {
          new_chapter_no = "Moyenne";
        }
        this.series_all[new_chapter_no] = raw_data[chapter_no].series.map(v => {
          // console.log(v.data)
          v.data = v.z.map(z => {
            return {
              x: z[0],
              y: z[1]
            };
          });
          return v;
        });
      }
    }
  },

  props: ["st_data", "id"],
  components: {
    VueSlider,
    AppButtons: Buttons
  },
  created() {
    // console.log('>> studentLexicalDecision raw data:', this.st_data.subject)
    this.load_graph_data(this.st_data.decision);
    this.chapter_list = Object.keys(this.series_all);
    // this.firstY = this.chapter_list[0]
    this.value = this.chapter_list[0];
    this.series = this.series_all[this.value];
    }
};
</script>

<style>

#decision > .apexcharts-canvas {
  background-color: white !important;
  opacity: 1;
}

#decision > .apexcharts-canvas > svg.apexcharts-svg {
  background-color: white !important;
  
  opacity: 1;
}
</style>