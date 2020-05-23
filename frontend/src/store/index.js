import Vue from "vue";
import Vuex from "vuex";
import TwitchModule from "./modules/Twitch";
import SoundUploadModule from "./modules/SoundUpload";
Vue.use(Vuex);

export default new Vuex.Store({
  state: {},
  mutations: {},
  actions: {},
  modules: { twitch: TwitchModule, sound: SoundUploadModule }
});
