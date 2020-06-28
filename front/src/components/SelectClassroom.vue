<template class="content">
  <div class="content-inside" id="select_classroom_page">
    <aside>
    </aside>
    <header>
      <div id="brand" class="container-fluid">
        <img id="brand-img" src="/src/assets/img/kalulu_up.png" height="150" class="" alt="" />
        <img id="brand-img2" src="/src/assets/img/title.png" height="80" class="" alt="" />
      </div>
    </header>
    <main>
      <content>
        <form id="classroom_login">
          <label>
              Entrez votre identifiant de classe
          </label>
          <div id="error" class="alert" v-if="invalid">
              <app-error title="Numéro invalide" :msg=msg></app-error>
          </div>
          <input 
                type="text"
                inputmode="numeric"
                pattern="[0-9]{2}" maxlength="2" 
                class="input" 
                id="classroom_id" 
                v-model="classroom_id" 
                @keyup.enter="submitted()"
                placeholder="Un nombre entre 1 et 60"
          >
          <button type="submit" class="btn" @click.prevent = "submitted()"><img src="/src/assets/img/button_next_up.png" width="100" height="100" class="d-inline-block" alt="" /></button>  
        </form>
        </content>
    <footer class="footer">

      <div class="container">Un projet NEUROSPIN (CEA) avec la collaboration de l'INSERM</div>
    </footer>
    </main>
    
  </div>
</template>

<script>
import services from '../services.js'
// import Header from './Header.vue'
import ErrorScreen from './subComponents/Error.vue'
  
export default {
  data () {
    return {
      classroom_digits: [],
      classroom_id: '',
      msg: undefined,
      invalid: this.$route.query.invalidform,
      target: this.$route.query.target,
      tried: this.$route.query.tried,
    }
  }, 
  // computed: {
  //   error_text() {
  //     return 'La classe n°' + this.tried + ' n\'a pas été trouvée: le numéro de classe doit être compris entre 1 and 60.'
  //     }
  // },
  methods: {
    submitted (){
      
      if (this.classroom_id == parseInt(this.classroom_id, 10) && 
      this.classroom_id > 0  && this.classroom_id < 61 ) {
        this.msg = ''
        // The input is valid: we can check the API
        // To do: API should be loaded here from component
        // API call should return true or false if the classroom exists or not
        // IF TRUE: the button takes you to classroom data + this module sends the raw api response to the next module (classroom)
        // IF FALSE: the button shows an error  
        this.$router.push('/classroom/' + this.classroom_id)
      } else {
          this.invalid = true
          this.msg = "Le numéro de classe "+this.classroom_id+" est invalide: un nombre entre 1 et 60."
          // this.tried = this.classroom_id
          // this.target = this.$route.query.target
      }
    },
  },
  components: {
    // AppHeader: Header, 
    AppError: ErrorScreen,
  }
}
</script>


<style scoped>
/* main{
  background-image: url(../assets/img/loading_background.png);
} */

</style>
