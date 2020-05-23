import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import MusicUploadView from "../views/MusicUploadView";
import MusicPlayView from "../views/MusicPlayView";
import ListenView from "../views/ListenView";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home
  },
  {
    path: "/about",
    name: "About",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/About.vue")
  },
  {
    path: "/soundboard/upload",
    name: "Upload clip",
    component: MusicUploadView
  },
  {
    path: "/soundboard",
    name: "Soundboard",
    component: MusicPlayView
  },
  {
    path: "/listen",
    name: "Listen",
    component: ListenView
  }
];

const router = new VueRouter({
  routes
});

export default router;
