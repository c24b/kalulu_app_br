<template>
<div>
    
  <h3>{{s_title}}</h3>  
  <apexchart  
    class="widget graph"
    ref="heat"
    :width="chartW" 
    :height="chartH" 
    type=heatmap 
    :options="chartOptions" 
    :series="chart_data"
    >
  </apexchart>
<!-- {{chart_data}} -->
</div>
</template>

<script>
import Buttons from '../subComponents/Buttons.vue'

export default {
  data: function() {
    return {
      
      value: 1,
      raw_student_data : [],
      chartOptions: {
        dataLabels: {
          enabled: false
        },
        // colors: ["#FF0000"],
        plotOptions:{
          heatmap:{
            // enableShades: false,
            // shadeIntensity: 0.7,
            reverseNegativeShade: true,
            colorScale: {
              ranges: [
                {
                  from: -1,
                  to: 0,
                  name: 'No data',
                  color: '#bebebe',
                },
                {
                  from: 0,
                  to: 0.25,
                  name: 'Correct',
                  color: '#fceeed'
              },
              {
                  from: 0.26,
                  to: 0.5,
                  name: 'Low',
                  color: '#FF7F7F'
              },
              {
                  from: 0.51,
                  to: 0.75,
                  name: 'Medium',
                  color: '#ED2939'
              },
                {
                  from: 0.76,
                  to: 1,
                  name: 'High',
                  color: '#C4150C'
              }
              ]
            },
            min: -1,
            max: 1
          },
        },
        chart: {
          // offsetY: 80,
          events: {
            beforeMount: (chartContext, config) => {
                // console.log('>> BEFORE MOUNT config', config)
              },
            mounted: (chartContext, config) => {
              // console.log('>> translateXAxisY', config.globals.translateXAxisY)
              // config.globals.translateXAxisY = 0
              // console.log('>> translateXAxisY', config.globals.translateXAxisY)
              // console.log('>> xAxisLabelsHeight', config.globals.xAxisLabelsHeight)
              this.update_xaxis_title_offset(config)
              },
            // updated: (chartContext, config) => {
            //     this.calculate_xaxis_offset(config)
            //   },
          },
          // fontFamily: "Avenir",
          // height: 100,
          animations: { // Due to abug, axis titles don't show up correctly unless this is activated
            enabled: true,
            speed: 1, // this actually means "time" (small number = faster)
            easing: 'easein' ,
            dynamicAnimation: {
              enabled: false //disabling this prevents the animation to trigger innecessarily on data change
            }
          },
          toolbar:{
            show: false,

          },
        },
        // title: {
        //   text: "", 
        //   align: 'center',
        //   margin: 20,
        //   offsetX: 0,
        //   offsetY: 0,
        //   floating: false,
        //   style: {
        //     fontSize:  '20px',
        //     color:  '#263238'
        //   },
        // }, 
        // subtitle: {
        //   text: this.chart_sub, 
        //     align: 'left',
        //     margin: 0,
        //     offsetX: 0,
        //     offsetY: 30,
        //     floating: false,
        //     style: {
        //       fontSize:  '20px',
        //       color:  '#263238'
        //     },
        // }, 
        legend: {
          show: true,
          position: 'bottom',
          horizontalAlign: 'center',
          labels: {
            colors: undefined,
            useSeriesColors: false
          },
          // onItemHover: {
          //   highlightDataSeries: true
          // },
        }, 
        xaxis : {
          position: 'top',
          // offsetY : 0,
          tooltip: {
            enabled: false
          },
          labels: { 
            show: true, 
            offsetY: -16,
            rotate: 90,
            rotateAlways: false,
          },
          title: {
            text: this.xaxis_label,
            offsetY: -90,
            style: {
              fontSize:  '12px',
              cssClass : "axis-tile"
            }
              
          },
          axisTicks: {
            // offsetX: -8
          },
          tickAmount: this.chart_data[0].data.length -2,
        }, 
        yaxis : {
          reversed: true,
          title: {
            text: this.yaxis_label,
            style: {
              cssClass : "axis-title",
              fontSize : "12px"
            }
          }
        }, 
        tooltip: {
          custom: ({series, seriesIndex, dataPointIndex, w}) => {
            let y = w.globals.seriesNames[dataPointIndex]
            let x = w.globals.seriesNames[seriesIndex]
            let z = series[seriesIndex][dataPointIndex]
            if (z != -0.1 ) {
              return ('<span>'+this.xaxis_label+': <b>'+x+'</b>,'+this.yaxis_label+': <b>'+y+'</b><br/> Taux de confusion: <b>'+z+'</b></span>')
            }
            else {
              return ('<span>'+this.xaxis_label+': <b>'+x+'</b>,'+this.yaxis_label+': <b>'+y+'</b><br/> Taux de confusion: <b> NaN</b></span>')
            }
            
          },
        },
      }
    }
  },
  methods: {
    update_xaxis_title_offset(config){
      // console.log('>> mounted/updated config', config)
      // console.log('>> rotateXLabels', config.globals.rotateXLabels)
      // console.log('>> labels', config.globals.labels)
      if (config.globals.rotateXLabels) {
        let label_lens = []
        config.globals.labels.forEach((v)=> {label_lens.push(v.replace('/','').length)})
        // Two other possible values:
        // let xaxis_offset = - config.globals.xAxisLabelsHeight * config.globals.LINE_HEIGHT_RATIO
        // let xaxis_offset = - config.globals.xAxisLabelsHeight - (translateYAxisX)
        let xaxis_offset = - config.globals.xAxisLabelsHeight - (Math.max(...label_lens) *7)
        // console.log('xaxis offset: ', xaxis_offset)
        this.$refs.heat.updateOptions({
          xaxis : {
            title: {
              offsetY: xaxis_offset,
            }
          },
          title:{
            // margin: -xaxis_offset - 80
          },
          grid:{
            padding: {
              top: (Math.max(...label_lens) *7),
              bottom: -(Math.max(...label_lens) *7)
            }
          }
        })
      }
    }
  },
  props:[
    's_title',
    'chart_data',
    'chart_name', 
    'chart_sub', 
    'xaxis_label',
    'yaxis_label',
    'chartH',
    'chartW',
    'click_redirect_to',
  ],
    components:{
    appButtons: Buttons
  },
  mounted(){
    // console.log('>> heatmap.vue: chart_data', this.chart_data)
    // console.log('>> heatmap.vue: this.chart_name', this.chart_name)
    if (this.click_redirect_to){ 
      this.$refs.heat.updateOptions({
        chart: {
          events:{
              dataPointSelection: (event, chartContext, config) => {
                // console.log('>> click en heatmap')
                this.$router.push({
                  name: 'confusionStudentSubject',
              })
  
              },
            }
        }
      })
    }
  }

};
</script>

<style scoped>

</style>
<style>

.popover{
    max-width: 45%; 
}

.apexcharts-canvas {
  background-color:rgba(255, 255, 255, 0.8);
  }


/* .axis-title {
  font-style: italic;
} */

/* .apexcharts-tooltip {
  color: rgb(85, 85, 85);
  transform: translateX(10px) translateY(10px);
  overflow: visible !important;
  white-space: normal !important;
} */

/* .apexcharts-tooltip span {
  padding: 5px 10px;
  display: inline-block;
} */

</style>