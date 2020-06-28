<template id="student_last_lesson">
  <article id="last_lesson" class="widget graph">
    <app-buttons :doc="st_data.doc" :id="id" :title="st_data.title"></app-buttons>
    <h2 class="heading">
      {{st_data.title}}
    </h2>
    <h3>dans le jardin courant</h3>
    <div id="last_lesson_graph" class="content chart">
      <apexchart
        type="scatter"
        height="100%"
        :options="chartOptions"
        :series="series"
      />
    </div>
  </article>
</template>

<script>
import Buttons from "./Buttons.vue";

export default {
  data: function() {
    return {
      studentChosen: "",
      series: [
        {
          name: "star-dot",
          data: [],
          x: [],
          z: [],
          miss: []
        },
        {
          name: "x",
          data: [],
          x: [],
          z: [],
          miss: []
        }
      ],
      chartOptions: {
        chart: {
          animations: {
            enabled: false
          },
          // background:"#7AD1FF",
          zoom: {
            enabled: true
          },
          toolbar: {
            show: false
          },
          // fontFamily: "Avenir"
        },
        xaxis: {
          type: "category",
          // categories: []
          tickAmount: this.st_data.data[0].x.length - 1,
          min: 1,
          max: this.st_data.data[0].x.length,
          labels: {
            show: true,
            hideOverlappingLabels: false,
            trim: true,
            minHeight: 10,
            maxHeight: 30,
            style: {
                fontSize: '16px',
                fontWeight: 400,
                cssClass: 'apexcharts-xaxis-label',
            },
              showDuplicates: true,
            
          },
          axisBorder: {
            show: false
          },
          
          tooltip: {
            enabled: true
          }
        },
        yaxis: {
          show: false,
          tickAmount: 1,
          // min: 0,
          // max: 3,
          decimalsInFloat: 0,
          axisBorder: {
            show: false
          }
        },
        markers: {
          size: 20,
          strokeColors: "#7AD1FF",
          strokeWidth: 1,
          strokeOpacity: 0,
          onClick: undefined,
          onDblClick: undefined,
          // hover: {
          //   size: 2,
          //   sizeOffset: 1
          // }
          // hover: {
          //   size: undefined,
          //   sizeOffset: 0
          // }
        },
        
        fill: {
          type: "image",
          opacity: 1,
          image: {
            src: ["/src/assets/img/success.png", "/src/assets/img/cross.png"],
            width: 40,
            height: 40
          }
        },
        grid: {
          show: false,
          padding: {
            top: 20,
            right: 30,
            bottom: 50,
            left: 30
          }
        },
        tooltip: {
          enabled: true,
          shared: false, //prevents getting only 1 tooltip per column
          intersect: true,
          marker: {
            show: false
          },
          y: {
            formatter: (val, { series, seriesIndex, dataPointIndex, w }) => {
              console.log(val);
              return (
                this.series[seriesIndex].x[dataPointIndex] +
                " confondu avec " +
                this.series[seriesIndex].z[dataPointIndex].join(" et ")
              );
              // return "'" + this.series[seriesIndex].z[dataPointIndex].join("', '")
              //   + "' " + this.st_data.data[0].zaxis_label + " '" + this.series[seriesIndex].x[dataPointIndex] + "'"
            },
            title: {
              formatter: (
                seriesName,
                { series, seriesIndex, dataPointIndex, w }
              ) => {
                console.log(
                  "StudentLAstLesson ToolTIP",
                  w.config.series[seriesIndex]
                );
                // console.log('>>>>>>>>>>>> a vera', w.config.series[seriesIndex].miss)
                // return 'Elève ' + this.st_data.data.student
                return false;
              }
            }
          },
          x: {
            show: false
          }
        },
        legend: {
          show: false
        }
      }
    };
  },
  methods: {
    populate_graph() {
      console.log(this.st_data.data)
      // console.log('>>>>> FORMATXY: x, y',this.st_data.data.x, this.st_data.data.y)
      // console.log('>>>> SERIES ', this.series)
      
      // set(this.st_data.data[0].colors)
      // this.chartOptions.colors.push(this.st_data.data[0].colors);
      var ref = { star: 0, cross: 1 };
      // this.st_data.data[0].colors.reduce((acc, current, i) => {
      //   // console.log(acc,current,i)
      // this.chartOptions.xaxis.labels.style.colors.push(this.st_data.data[0].colors[i+1])
      // });
      this.st_data.data[0].markers.reduce((acc, current, i) => {
        //this.series[ ref[current] ].miss.push(this.st_data.data[0].text[i])
        
        this.series[ref[current]].x.push(this.st_data.data[0].x[i]);
        this.series[ref[current]].z.push(this.st_data.data[0].z[i]);
        return this.series[ref[current]].data.push([
          i + 1,
          this.st_data.data[0].y[i]
        ]);
      }, "");
      // console.log('>>>>>> SERIES:', this.series)
    }
  },
  props: [
    "st_data",
    "id"
  ],
  components: {
    AppButtons: Buttons
  },
  created() {
    console.log(">> last lesson widget data raw:", this.st_data);
    this.chartOptions.xaxis.categories = this.st_data.data[0].x;
    this.populate_graph();
    // this.series[0].name = this.st_data.data.student
    // this.series[0].name = ""
  }
};
</script>

<style>

div#last_lesson_graph.content.chart > div > .apexcharts-canvas{
  background-color: #7AD1FF !important;
  opacity: 0.8;
}


</style>