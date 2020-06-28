  
<template>
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
        <li class="nav-item">
          <button id="popover-3" class="btn"><img src="/src/assets/img/button_data.png" width="60px"  alt="" /></button>
          <b-popover style= "" target="popover-3" triggers="hover focus">
            <template v-slot:title><h6 style="color:black; ">{{title}} </h6></template>
            {{documentation}}
          </b-popover>
        </li>
        
      </ul>
      <!-- <h5 style="transform: rotate(-15deg); margin-top:2%; width: 100%;margin: 0;" v-if="status=='ready'" class="float-left"><i>N°Tablette  N°Groupe</i></h5>
         -->
      </b-col>
      
      <b-col cols=11>
        <b-row>
        <b-col>
        <img style="vertical-align:middle" height="150" id="brand-img" src="/src/assets/img/kalulu_up.png" alt="" />
        {{title}} 
        </b-col>
        </b-row>
        <b-row>
          <b-col>
            <span class="small" style="font-size:18px">Appuyez sur n’importe pastille d’un élève pour en savoir plus sur ses connaissances !</span>
          </b-col>
        </b-row>
        <app-spinner v-if="status == 'loading'"></app-spinner>
        <b-row>
          <!-- <b-col> -->
          <h5 style="transform: rotate(-30deg); margin-left:-5%; margin-top:2%;" v-if="status=='ready'" class="float-left"><i>N°Tablette  N°Groupe</i></h5>
          <!-- </b-col> -->
        </b-row>
        <b-row v-if="status=='ready'">
        <apexchart ref="evo" type=line  height="950px" width="2500px"  :options="chartOptions" :series="formatted_series" v-if="status=='ready'"/>
        </b-row>
         
    </b-col>
    </b-row>
  </b-container>
  
  <!-- <div id="classroom_page">
      <aside id="navbar">
          <ul>
            <li><button class="btn" id="menu"><a href="/">
            <img src="/src/assets/img/button_back_to_menu_up.png" width="60px"  alt="" /></a></button></li>
            <li>
              
              <button class="btn" id="back" @click='$router.go(-1)'>
              <img src="/src/assets/img/button_back_up.png" width="60px"  alt="" />
              </button>
            </li>
            <li>
              <button id="popover-3" class="btn"><img src="/src/assets/img/button_data.png" width="60px"  alt="" /></button>
              <b-popover style= "background-color:pink;" target="popover-3" triggers="hover focus">
                <template v-slot:title><h6 style="color:black; ">{{title}}</h6></template>
                {{documentation}}
              </b-popover>
            </li>
          </ul>
      </aside>
      <header>
        <div id="brand" class="row">
          
          <h2> {{title}}</h2>
          <!-- <h2 class="col-10"> Progression de la classe {{cid}}  <span v-if="ready"> en {{sub_title}}</span></h2> -->
        <!-- </div> 
      </header>
      <main>
        <content v-if="ready">

          <article id="chart" v-if="status">  
            <b-container class="bv-example-row">
            <b-row>
    <b-col><img style="vertical-align:middle" height="150" id="brand-img" src="/src/assets/img/kalulu_up.png" alt="" /></b-col>
    <b-col>{{title}}</b-col>
    <b-col></b-col>
  </b-row>
</b-container>
              

              <apexchart ref="evo" type=line  width="2500px"  :options="chartOptions" :series="formatted_series" v-if="ready"/>
            
          </article>
          <article id="error" v-else>
            <app-error title="Oups..." :msg=msg></app-error>
          </article>
        
        </content>
        <content v-if="loading">
          <article>
            <app-spinner></app-spinner>
          </article>
        </content>
      </main>
    <footer>
    </footer>
  </div> -->
</template>

<script>
import axios from 'axios'
import services from '../services.js'
import Spinner from './subComponents/Spinner.vue'
import ErrorScreen from './subComponents/Error.vue'
import Button from './subComponents/Buttons.vue'

const subjects_name = {'letters':'Français', 'numbers':'Maths'}
const subjects_title = {'letters':'lettres', 'numbers':'nombres'} 
const objects_name = {'letters':'graphème-phonème', 'numbers':'nombre'} 
const subjects_ref = {'letters':'gp', 'numbers':'numbers'}
const colors_ref = {green : "#0A0",  orange : '#ff6600',  red : '#ff0000'}

export default {
  data: function(){
    // if (this.$route.params.sub == "letters"){
    //   const subject_name = "Français"
    // } else {
    //   const subject_name = "Maths"
    // }
    return {
      classroom : this.$route.params.cid, 
      subject : this.$route.params.sub,
      title : 'Progression de la classe ' + this.$route.params.cid + ' en ' + subjects_name[this.$route.params.sub],
      // student_no : '',
      object_name: objects_name[this.$route.params.sub],
      subject_title: subjects_title[this.$route.params.sub],
      documentation: "Ce graphique vous montre, pour chaque élève, les défis réussis sur le chemin des "+ subjects_title[this.$route.params.sub]+".<br/> La couleur de la pastille vous montre l’aisance que l’élève a eu pour réussir les jeux du défi. <i>Comment avons-nous créé la couleur?</i> : Nous avons étalonné le pourcentage pour chaque défi à partir des résultats de tous les participants dans le projet. La couleur de la pastille indique le résultat par rapport à la moyenne du groupe. En vert, le taux de bonnes réponses de l’enfant était plus de -1 écart-type. Autrement dit, son taux de bonnes réponses était ‘normal’. En jaune, son taux de bonnes réponses était entre -1 et -2 écart-type. En rouge, son taux de bonnes réponses était moins de -2 écart-type par rapport à la moyenne. <br /> <b>Attention<b>, pour réussir un défi, l’enfant doit avoir 70% de réponses correctes. Cette information reflète peut-être une difficulté momentanée pour acquérir un "+objects_name[this.$route.params.sub]+" ou un mini-jeu. <br />Appuyez sur n’importe pastille d’un élève pour en savoir plus sur ses connaissances !",
      api_response: [null, null, null],
      data: undefined,
      response: null,
      status: 'loading',
      formatted_series : [],
      sort_value: 'name',
      sort_value2: 'tablette',
      btncl: {name: "btn btn-secondary", completed: "btn btn-secondary"},
      chartOptions: {  
        markers: {
          size: 10,
          strokeWidth: 0.1,
        }, 
        colors: ['#346868'], //'#346868', '#FFF'
        stroke: {
          width: 1
        },
        chart: {
          foreColor: '#FFF',
          animations: {
            enabled: false,
          },
          zoom: {
            enabled: false,
          },
          toolbar: {
            show: false
          }, 
          events: {
            click: (event, chartContext, config) => {
              this.$router.push({
                name: 'studentPage',
                params: {
                  stid: config.config.series[config.seriesIndex].name,
                  sub: this.subject
                }, 
              })
            }
          }
        },
        xaxis: {
          type: 'category',
          categories: [],
          title: {
            // text: 'Défis réussis sur le chemin des lettres',
            offsetY: 0,
            style: {
              fontSize:  '32px',
              fontWeight:  'bold',
            },
          },
          labels: {
            show: true,
            rotateAlways: true,
            style: {
              colors: [],
              fontSize: '22px',
              cssClass: 'apexcharts-xaxis-title',
            }
          },
          axisBorder: {
            offsetY: 35
            },
          
        },
        yaxis: {
          text: '',
          title: {
            style: {
              fontSize:  '32px',
              fontWeight:  'bold',
            },
            
          },
          labels: {formatter: (value) => {
            let reals = {}
            this.formatted_series.map( (v) => {reals[v.data[0]] = v.name} )
            if (Object.keys(reals).includes(value.toString())) { 
              
              let student_id_str = reals[value].toString()
              return student_id_str.slice(-2).split("").join('    '); }
          },
          style : {
            color: "white",
            fontSize: "32px",
            cssClass: 'apexcharts-yaxis-title',
          }
          }
        },
        grid: {
          show: true,
          column: {
              colors: [],
              opacity: 1
          },
          padding: {
            top: 0,
            right: 10,
            bottom: 80,
            left: 10
          },
          
        }, 
        legend: {
          show: false
        },
        
        tooltip: {
          enabled : true,
          shared : false, //prevents getting only 1 tooltip per column
          intersect : true, // necessary for the click behaviour
          marker: {
            show: false
          },
          fillSeriesColor: true,
          style: {
            fontSize: '22px',
            fontWeight: 'bold'
          },
          y : {
            
            formatter: (val, { series, seriesIndex, dataPointIndex, w }) => {
              return "Défi terminé en " + parseInt(w.config.series[seriesIndex].zscore[dataPointIndex]/60, 10) + " min."
            },
            title: {
              formatter: (seriesName, { series, seriesIndex, dataPointIndex, w }, a) => { 
                return 'Elève ' + seriesName.toString().slice(-2)
              },
            },
          }, 
          
        },
      }
    }
  },
  
  methods: {
    format_series(raw_data, criteria){
      // 1. Get everything in the object structure that Apex needs: 
      // console.log('>>>> RAW DATA:', raw_data)
      var series = raw_data.data
      

      var formatted_series = raw_data.data.map((line, i) => {   
        var formatted_line = raw_data.data.map((v) => {
          return i
        })
        var tablet = series[i].student.toString()
        tablet = tablet.substring(tablet.length - 2, tablet.length -1)
        // console.log("Tablet n°", tablet)
        var formatted_serie = {
          'name': series[i].student, // student_no 
          'data': series[i].lesson_ids, 
          'zscore' : series[i].timespents,
          'color' : series[i]["%CA_colors"],
          'tablet' : parseInt(tablet), 
          'completed' : series[i].lesson_ids.length
        }
        // console.log(series[i]["%CA_colors"])
        return formatted_serie
      })
      // 2. Sort the data by the property specified in "criteria":
      let formatted_sorted_series = formatted_series.sort((a,b) => (a[criteria] > b[criteria]) ? 1 : -1)
      // 3. Put every serie y-value to "i" and update "formatted_series" 
      this.formatted_series = formatted_sorted_series.map((v, i) => {
        let formatted_line = v.data.map((w) => {
          return i
        })
        v.data = formatted_line
        return v
      })     
      // console.log('>> ClassroomPage, format_series result', this.formatted_series)
                
    },

    add_separators(series){
      let tablets = series.map((v) => v.tablet)
      let uniques = Array.from(new Set(tablets))
      let target = uniques.map((v) => tablets.indexOf(v))
      target.splice(0,1) //we remove the first target to avoid getting a gap at the bottom of xaxis
      let found = []
      let acc = 0
      let result = []
      let xx = series.map((v, i, a) => {
        if (target.includes(i) && !found.includes(i)) {
          found.push(i)
          acc += 1
        }
        let new_v = v
        new_v.data = v.data.map(w => w+acc)
        result.push(new_v)
        return a
      })
      // console.log('>>> SEPARATOR ', result)
      return result
    },

    find_all_indices(formatted_series) {
      return formatted_series.map(v => v.data[0])
    },

    fill_markers(formatted_series){
      var all_colors_b = []
      var all_colors = formatted_series.map((v, i) => {
        // console.log('>>>> v.color',v.color )
        var serie_colors = v.color.map((color, j) => {
          var buf = { 
            seriesIndex: i,
            dataPointIndex: j,
            fillColor: color, //"#0A0",
            strokeColor: "#FFF",
            size: 9
          }
          all_colors_b.push(buf)
          return buf
        })
        return serie_colors
      })
      // console.log('>> fill_markers, all_colors', all_colors)
      // console.log('>> fill_markers, all_colors_b', all_colors_b)
      return all_colors_b
    },

    format_axes(raw_data){
      // console.log('>>>raw_data.x_axis_labels', raw_data.x_axis_labels)
      // this.chartOptions.yaxis.tickAmount = Math.max(...this.find_all_indices(this.formatted_series))
      this.chartOptions.yaxis.tickAmount = raw_data.y_axis_index.length
      this.chartOptions.yaxis.min = 0 
      this.chartOptions.yaxis.max = raw_data.y_axis_index.length
      // this.chartOptions.yaxis.title.text = raw_data.y_label
      this.chartOptions.xaxis.tickAmount = raw_data.x_axis_index.length
      this.chartOptions.xaxis.min = 0
      this.chartOptions.xaxis.max = raw_data.x_axis_index.length + 1
      this.chartOptions.xaxis.categories = raw_data.x_axis_labels
      this.chartOptions.xaxis.title.text = raw_data.x_label
      this.chartOptions.xaxis.labels.style.colors = raw_data.chapter_colors
      // this.chartOptions.grid.column.colors = raw_data.chapter_colors
    },

    add_ghost_serie(raw_data, formatted_series){
      // We need to show all X-AXIS LABELS contained in raw_data.x_axis_labels. By default, ApexCharts doesn't allow showing empty categories on the X-AXIS, so we will create a dummy serie with all data points so the X-Axis shows all the values. The Y will be set 2 places above the maximum Y value set in "format_axes" so the dummy serie is invisible. 
      
      // var y_max = Math.max(...this.find_all_indices(formatted_series))
      var y_max = raw_data.y_axis_index.length + 1
      var x_max = raw_data.x_axis_labels.length
      var fake_serie = Array.apply(0, {length: x_max}).map(v => y_max + 2)
      this.formatted_series.push({'data': fake_serie, 'name':'0'})
    },

    // rearrange_series(criteria, separators = false){
    //   this.format_series(this.raw_data, criteria)
    //   if (separators){
    //     this.formatted_series = this.add_separators(this.formatted_series)
    //   }
    //   this.$refs.evo.updateOptions({
    //       markers: {
    //         discrete: this.fill_markers(this.formatted_series)
    //       }, 
    //       yaxis: { 
    //         title : { text: this.raw_data.y_label},
    //         tickAmount: Math.max(...this.find_all_indices(this.formatted_series)),
    //         min : 0,
    //         max : Math.max(...this.find_all_indices(this.formatted_series)),
    //         labels: {formatter: (value) => {
    //           let reals = {}
    //           this.formatted_series.map( (v) => {reals[v.data[0]] = v.name} )
    //           if (Object.keys(reals).includes(value.toString())) { return reals[value] }
    //         }}

    //       }
    //     }
    //   )
    //   this.add_ghost_serie(this.raw_data, this.formatted_series)
    //   // this.format_axes(this.raw_data)
    //   this.btncl = {name: "btn btn-secondary", completed: "btn btn-secondary"}
    //   this.btncl[criteria] = "btn btn-secondary active"
    //   // console.log('formatted_series', this.formatted_series) 
    // },
    

    
  }, 
  components: {
    AppSpinner: Spinner,
    AppError: ErrorScreen,
    
  },

  async mounted() {
    // this.uri = services.buildUri('classroomProgression', this.cid, this.sub) 
    this.uri = services.buildUri({
      'endPoint': 'classroomProgression', 
      'classrooms':this.classroom, 
      'subjects': this.subject
      })
    console.log("URI", this.uri)
    this.api_response = await services.getData(this.uri)
    console.log("URI", this.api_response)
    this.status = this.api_response[2]
    this.data = this.api_response[1]
    this.response = this.api_response[0]
    this.title = this.data.title
    this.message = this.api_response[1].message
    console.log("RESPONSE", this.response)
    console.log("DATA", this.data)
    console.log("STATUS", this.status)
    this.format_series(this.data, 'name')
    this.formatted_series = this.add_separators(this.formatted_series)
    this.format_axes(this.data)
    // this.chartOption.markers.discrete = response.data.chapter_colors
    this.chartOptions.markers.discrete = this.fill_markers(this.formatted_series)
    this.add_ghost_serie(this.data, this.formatted_series)
    this.btncl['name'] = "btn btn-secondary active"
     
    
  }
}
</script>

<style>
article#chart > div > div.apexcharts-canvas {
    background-color: #11ffee00!important; 

}


/* .apexcharts-canvas {
    background-color: #11ffee00!important; 
    
} */

</style>
<style scoped> 
.apexcharts-xaxis-title{

}
.apexcharts-yaxis-title{
  
}
article#chart > div > div.apexcharts-canvas {
    background-color: #11ffee00!important; 

}

</style>
