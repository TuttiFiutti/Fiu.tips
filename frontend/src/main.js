import Vue from "vue";
import App from "./App.vue";
import "./registerServiceWorker";
import router from "./router";
import store from "./store";
import vuetify from "@/plugins/vuetify";
import "vuetify/dist/vuetify.min.css";
import Buefy from "buefy";
import "buefy/dist/buefy.css";

Vue.config.productionTip = false;
Vue.use(Buefy);

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount("#app");
