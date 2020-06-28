<template>
<div id="header">
  <!-- HOLA SOY EL HEADER -->
  <!-- {{$route.params}}  -->

<nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #346868;">
  <a class="navbar-brand" href="/">
  <img src="/src/assets/icon.png" width="50" height="50" class="d-inline-block" alt="">
    Kalulu
  </a>
  <!-- This makes a hamburger button appear when the window is resized and made narrower -->
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
  <span class="navbar-toggler-icon"></span>
  </button>
  <!-- end of the hamburger b -->
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
      <router-link 
        tag="li" 
        to="/" 
        class="nav-item"
        active-class="active"
        exact 
        > <a class="nav-link"> Tableau de bord </a>
      </router-link>

      <router-link 
        tag="li" 
        class="nav-item"
        v-for="(link, name) in crumbs" 
        :to= "link"
        v-bind:key="link"
        active-class="active"
        exact 
      > <a class="nav-link"> 
        {{name}}
        </a>
      </router-link>

    </ul>
  </div>
</nav>
<!-- DEBUG: ROUTE PARAMS: {{$route.params}} <br> -->
<!-- DEBUG: ROUTES PARAMS: {{better_crumbs}}<br> -->
<!-- DEBUG: ROUTES HARD: {{crumbs}} -->


</div>

</template>

<script>
export default {
  data: function(){
    return{
      breadcrumbs : [], 
      niceNames : {
        'cid': 'Classe',
        'sub': 'Matière',
        'stid': 'Elève'
      },
      niceSubs: {
        'letters': 'Français', 
        'numbers': 'Maths'
      },
      urlNames : {
        'cid': 'classroom', 
        'sub': 'subject',
        'stid': 'student'
      }, 
      routeNames : {
        'cid': 'subjectSelect', 
        'sub': 'classroomPage',
        'stid': 'studentPage'
      }, 
    }
  }, 
  computed : {
    crumbs: function(){
      if (Object.keys(this.$route.params).length > 0){
        // console.log('>> Header, better_crumbs - $route.params:',  this.$route.params)
        let route_nice_sub = {...this.$route.params}
        if ('sub' in route_nice_sub){
          route_nice_sub['sub'] = this.niceSubs[route_nice_sub['sub']]
        }
        let links = {}
        Object.entries(route_nice_sub).reduce((acc, [param, val], i) => {
          console.log(i, '>> Header, better_crumbs - acc, param, val', acc, param, val)
          return links[[this.niceNames[param], val].join(': ')] = [acc, this.urlNames[param], val].join('/')
        }, '')
        return links
      }
    }
  }
}
</script>

<style scoped>
.navbar {
    
}


.navbar-brand{
  /* font-size: 22px; */
  font-weight: bold;
}

.navbar-nav {
  line-height:18px;
  /* font-size:20px;  */
}
/* .navbar .navbar-nav .nav-item::after { */
.navbar-nav li a::after {
  content: "›";
  padding-left: 12px;
  font-weight: bold;
  /* font-size:24px;  */
}

.navbar-nav li:last-child a::after {
    content: "";
}


#header {
  padding-bottom:1%;
}
</style>