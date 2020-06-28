import Vue from 'vue'
import App from './App.vue'
import VueRouter from 'vue-router';
import axios from 'axios'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import VueHtmlToPaper from 'vue-html-to-paper';
const options = {
    name: '_blank',
    specs: [
      'fullscreen=yes',
      'titlebar=yes',
      'scrollbars=yes'
    ],
    styles: [
      'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',
      'https://unpkg.com/kidlat-css/css/kidlat.css'
    ]
  }
  
Vue.use(VueHtmlToPaper, options);
  
// Install BootstrapVue
Vue.use(BootstrapVue)
// Optionally install the BootstrapVue icon components plugin
Vue.use(IconsPlugin)

import "regenerator-runtime/runtime";

import { routes } from './routes.js';
Vue.use(VueRouter);


import VueApexCharts from 'vue-apexcharts'
Vue.component('apexchart', VueApexCharts)
axios.defaults.baseURL = "https://research.ludoeducation.fr"
//axios.defaults.baseURL = "http://localhost:5000"
// NOTE START: UPDATING VUE RESOURCE TO AXIOS - THIS WILL BE DELETED WHEN REPLACING IS FINISHED
import VueResource from 'vue-resource';
Vue.use(VueResource)
// Vue.http.options.root = "https://research.ludoeducation.fr"


const router = new VueRouter({
    routes, // routes: routes
    mode: 'history',
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        }
        if (to.hash) {
            return { selector: to.hash };
        }
        // return {x:0, y:700};
    }
})

function filter_int(to, from, next, filter_target, target_name, f_target_name, target_min, target_max, prepend = "") {
    // console.log('DEBUG -  routes.js - to.params.cid, filter_target, target_name, to.params': , to.params.cid, filter_target, target_name, to.params)
    if (target_name in to.params) {
        console.log('Int check - necesario!', filter_target)
        if (filter_target != parseInt(filter_target, 10) && (filter_target > target_min && filter_target < target_max)) {

            console.log('Int check - NO pasa! Path:', to.path)
            next(prepend + '/?invalidform=true&target=' + f_target_name + '&tried=' + filter_target)
        } else {
            next();
        }
    } else {
        console.log('Int check - SI pasa el check (o check innecesario) :)')
        next()
            //next();
    }
}

function filter_subjects(to, from, next, filter_target, target_name, f_target_name, subjects = ['letters', 'numbers']) {
    // console.log('DEBUG -  routes.js - to.params.cid, filter_target, target_name, to.params': , to.params.cid, filter_target, target_name, to.params)  
    if (target_name in to.params) {
        console.log('Subject Check necesario!', filter_target, to.params)
        if (!subjects.includes(filter_target)) {
            console.log('>>>>> Subject check: Subject:', subjects, " Filter target:", filter_target, !subjects.includes(filter_target))
            console.log('Subject Check - NO pasa! Path:', to.path)
            if ('stid' in to.params) {
                next('/student/' + to.params.stid + '/?invalidform=true&target=' + f_target_name + '&tried=' + filter_target)
            } else {
                next('/classroom/' + to.params.cid + '/?invalidform=true&target=' + f_target_name + '&tried=' + filter_target)

            }
        } else {
            next();
        }
    } else {
        console.log('Subject Check - SI pasa (o check innecesario) :)')
        next()
    }
}

router.beforeEach((to, from, next) => {
    // console.log(to.params)
    filter_int(to, from, next, to.params.cid, 'cid', 'classroom ID', 0, 61)
    filter_int(to, from, next, to.params.stid, 'stid', 'student ID', 111, 60830)
    filter_subjects(to, from, next, to.params.sub, 'sub', 'subject')
})


new Vue({
    el: '#app',
    router,
    render: h => h(App)
})
