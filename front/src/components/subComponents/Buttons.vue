<template>
<div>    
    <!-- <aside id="graph-navbar">
        
        <ul class="navbar">
          <li> -->
            <button :id='id' class="btn"><img src="/src/assets/img/button_data.png" width="60px"  alt="" /></button>
            <b-popover  :target='id' triggers="hover">
            <template v-slot:title><h4 style="color:black; ">{{title}}</h4></template>
              {{doc}}
              </b-popover>
          <!-- </li>
          <li class="push-right">
          <h2> {{title}} </h2>
          </li>
        </ul>
            </aside>
     -->
</div>
</template>

<script>
export default {
    props: [
        'doc',
        'id',
        'title'
    ]
} 
</script>

<style>
</style>