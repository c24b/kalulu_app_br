<template>
  <div id="select_subject">
    <aside id="navbar">
        <ul>
          <li>
            <button class="btn" id="menu"><a href="/"><img src="/src/assets/img/button_back_to_menu_up.png" width="60px"  alt="" /></a></button>
          </li>
          <li>
            <button class="btn" id="back" @click='$router.go(-1)'>
            <img src="/src/assets/img/button_back_up.png" width="60px"  alt="" />
            </button>
          </li>
        </ul>
    </aside>
    <header>
      
      <div id="brand">
        <img id="brand-img" style="vertical-align:middle" src="/src/assets/img/kalulu_up.png" height="150" class="" alt="" />
        <h2> Classe {{cid}}</h2>
      </div>
      
    </header>
    
    <main>
      
      <content>
          <form id="select_subject">
            <label>Choisissez la matière</label>
            <div id="selection">
              <button class="radio" id="lt" name="letters" value="letters" @click="go('letters')">
                <span>Français</span>
              </button>
                <button id="nb" name="numbers" value="number" @click="go('numbers')">
                  <span>Maths</span>
                </button>
            </div>
          </form>
      </content>
    </main>
    <footer>
      <span>Un projet NEUROSPIN (CEA) avec la collaboration de l'INSERM</span>
    </footer>
  </div>      
</template>

<script>
export default {
  data: function() {
    return {
      cid: this.$route.params.cid
    }
  },
  methods : {
    async go(subject){
      if ('cid' in this.$route.params) {
        // http://github.com/vuejs/vue-router/issues/2881#issuecomment-520554378
        this.$router.push('/classroom/' + this.cid + '/subject/' + subject).catch(err=> {})
      } 
      else if ('stid' in this.$route.params) {
        this.$router.push('/student/' + this.$route.params.stid + '/subject/' + subject).catch(err=> {})
      }
      
    }
    
  }

}
</script>

<style scoped>
</style>