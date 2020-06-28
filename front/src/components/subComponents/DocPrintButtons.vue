<template>
<div>    
        
        <ul class="navbar">
          <li> 
            <button :id='id' class="btn"><img src="/src/assets/img/button_data.png" width="60px"  alt="" /></button>
            <b-popover  :target='id' triggers="hover">
            <template v-slot:title><h4 style="color:black; ">{{title}}</h4></template>
              {{doc}}
              </b-popover>
          
        </li>
          <li class="push-right">
          <button @click="print" class="btn">
    <img src="/src/assets/img/print.png" width="60px"  alt="Print" />
  </button>
          </li>
        </ul>
           
</div>
</template>

<script>
export default {
    methods:{
        print(){
        this.$htmlToPaper('print-area');
    }},
    props: [
        'doc',
        'id',
        'title',
        'print-id'
    ]
} 
</script>

<style>
</style>