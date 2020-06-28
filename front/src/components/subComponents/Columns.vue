<template class="">
  <article>
    Columns
  <app-buttons  :doc="doc" :title="title" :id="id"></app-buttons>
    <h2 class="heading"> {{title}} </h2>
    <!-- {{series}} -->
    <div id="content" v-if="ready==true">
      <apexchart class="graph"  type="bar" width="800" height="550" :options="chartOptions" :series="this.series"></apexchart>
    </div>
  </article>
</template>

<script>
import Buttons from './Buttons.vue'

export default {
  data: function(){
    return {
      ready: false,
      chartOptions: {
        chart: {
          // fontFamily: 'Avenir',
          type: 'bar',
          stacked: true, 
          height: 350,
          toolbar:{
            show: true,
            tools: {
              download: false,
              selection: false,
              zoom: false,
              zoomin: false,
              zoomout: false,
              pan: false,
              reset: false ,
              
            },
          },
        },
        // colors: ["#346868"],
        colors: ['#346868', '#CB4335'],
        plotOptions: {
          bar: {
            horizontal: false,
            // columnWidth: '55%',
            // endingShape: 'rounded'
          },
        },
        dataLabels: {
          enabled: false
        },
        // stroke: {
        //   show: true,
        //   width: 2,
        //   colors: ['transparent']
        // },
        xaxis: {
          // categories: this.xaxis_labels,
          title: {
            text: this.xaxis_title
          },
          // min: this.minX,
          // max: this.maxX,
          // tickAmount: this.lenX
          // tickPlacement: "between"
          // tooltip: {enabled: false}
        },
        yaxis: {
          title: {
            text: this.yaxis_title
          },
          labels: {
            formatter: (v) => {return v }
          },
          // tooltip: {enabled: false}
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          marker:{
              show: false
            }, 
          y: {
            formatter: (v, { series, seriesIndex, dataPointIndex, w }) => {
              return v + ' ' + w.config.series[seriesIndex].name.toLowerCase()
            },
            title: {
              formatter: (seriesName) => { 
                return false
              }
            },
          },
          x: {
            show: false
          },
        }
      },
    } 
  },
  computed: {
    minX: function() {
      return Math.min(...this.xaxis_labels)
    },
    maxX: function() {
      return Math.max(...this.xaxis_labels)
    },
    lenX: function() {
      return this.xaxis_labels.length
    }

  },
  props: [
    "title", 
    "xaxis_title",
    "yaxis_title",
    "xaxis_labels",
    "series",
    "doc",
    "id",
    "props"
  ], 
  components: {
    AppButtons: Buttons
  },
  mounted() {
    // console.log('>> ', this.title, this.xaxis_labels)
    // console.log('>> ', this.title, this.series)
    // console.log('>> Cols: mounted')
    // this.chartOptions.xaxis.categories = this.xaxis_labels,
    // this.chartOptions.xaxis.min = Math.min(...this.xaxis_labels)
    // this.chartOptions.xaxis.max = Math.max(...this.xaxis_labels)
    // this.chartOptions.xaxis.tickAmount = this.xaxis_labels.length
    this.ready = true


  }
}
</script>

<style>
</style>