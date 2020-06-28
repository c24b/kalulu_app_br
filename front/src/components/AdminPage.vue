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
    </header>
    <main>
    <div class="widget-container">
      <article >
        <h2 class="heading"> ADMIN
        </h2>
        
      </article>
    </div>
    <h2 class="heading">Confusion entre {{chart_name}}</h2>
    <app-buttons :title="title"  :link_doc="link_doc" :link_csv="link_csv"></app-buttons>
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

    
    </main>
    
  </div>
</template>

<script>
import widget from './subComponents/Widget.vue'
import Heatmap from './subComponents/Heatmap.vue'
import services from '../services.js'
export default {
  data: function(){
    return {
        subject : 'numbers',
        title: "Confusion entre Nombres",
        data:null, 
        error:null, 
        xaxis_label: null,
        yaxis_label: null,
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
        
        title: {
          text: "", 
          align: 'center',
          margin: 20,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize:  '20px',
            color:  '#263238'
          },
        }, 
        subtitle: {
          text: this.chart_sub, 
            align: 'left',
            margin: 0,
            offsetX: 0,
            offsetY: 30,
            floating: false,
            style: {
              fontSize:  '20px',
              color:  '#263238'
            },
        }, 
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
              fontSize : "10px"
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
  methods:{
    load_series(data) {
      return data.map(chapter_data => {
        return {
          'serie'  : chapter_data.matrix.map(matrix_data => {
            return ({
              'name': matrix_data[0],
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
  },
  components: {
    appWidget: widget,
    appHeatmap: Heatmap,
  },
  async mounted() {
    this.status = 'loading'
    let uri = services.buildUri( {
        'endPoint': "globalConfusion",
        'subjects': "numbers"
        })
    console.log(uri)
    this.response = await services.getData(uri)
    if (this.response[0] == false){
        console.log(this.response)
        this.status = 'error'
        this.title = this.response[1].data.title
        this.msg = this.response[1].data.message
    } else {
        console.log(this.reponse[1].data[0])
        this.status = 'ready'
        this.title = this.response[1].data.title
        this.data = this.reponse[1].data[0] 
        this.xaxis = this.reponse[1].data[0].xaxis
        this.yaxis = this.reponse[1].data[0].yaxis
        this.series = load_series(this.data)
    }
    },
};
    
</script>

<style >



</style>