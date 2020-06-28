<template id="student_decision">
  <div class="widget_container">
  <article id="decision" class="widget graph">
      <app-buttons :doc="st_data.doc" :title="st_data.title" :id="id"></app-buttons>
      <h2 class="heading">{{st_data.title}}</h2>
      
      <apexchart class="decision-graph content chart"
        background-color="#fff"
        type="line"
        height="450"
        width="1750"
        :options="chartOptions"
        :series="series"
      />
      
    </article>
    <article class="slider">
      <div class="">
        <label>
          Chapitre
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
</div>
</template>

<script>
import Buttons from "./Buttons.vue";
import VueSlider from "vue-slider-component";
import "vue-slider-component/theme/default.css";

export default {
  data: function() {
    return {
      value: 0,
      series_all: {},
      chapter_list: [],
      series: [],
      chartOptions: {
        xaxis: {
          // categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
          title: {
            text: this.st_data.xaxis_label,
            cssClass: "apexcharts-xaxis-title"
          }
        },
        yaxis: {
          // forceNiceScale: true,
          labels: {
            formatter: value => {
              return value.toFixed(2);
            }
          },
          title: {
            text: this.st_data.yaxis_label,
            cssClass: "apexcharts-yaxis-title"
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
            speed: 300
          },
        //   fontFamily: "Avenir, Helvetica, Arial, sans-serif",
          toolbar: {
            show: true,
            tools: {
              
            }
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
            colors: ["#f3f3f3", "transparent"], // takes an array which will be repeated on columns
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
    console.log("Student Decision", this.st_data.decision);
    this.load_graph_data(this.st_data.decision);
    this.chapter_list = Object.keys(this.series_all);
    this.value = this.chapter_list[0];
    this.series = this.series_all[this.value];
    
  }
};
</script>

<style>
.apexcharts-canvas.decision-graph {
  background-color: white !important;
  opacity: 1;
}

</style>