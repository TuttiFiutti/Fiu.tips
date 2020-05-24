<template>
  <div id="app">
    <v-app-bar color="grey lighten-4" height="60px">
      <router-link to="/"><i class="fa fa-fw fa-2x fa-home" title="Home"></i></router-link>
      <router-link to="/soundboard/upload"><i class="fa fa-fw fa-2x fa-upload" title="Upload"></i></router-link>
      <router-link to="/soundboard"><i class="fa fa-fw fa-2x fa-music" title="Soundboard"></i></router-link>
      <router-link to="/listen" v-if="displayName=='FriendlyFiutonaczi'"><i class="fa fa-fw fa-2x fa-volume-up" title="Listen"></i></router-link>
      <v-spacer />
      <a v-if="!loggedIn" href="/oauth/login"><i class="fa fa-fw fa-2x fa-user"></i></a>
      <v-avatar v-if="loggedIn" size="48">
        <img v-bind:src="avatar" v-bind:alt="displayName" />
      </v-avatar>
    </v-app-bar>
    <v-app>
      <router-view />
    </v-app>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  computed: {
    loggedIn() {
      return this.$store.state.twitch.userID !== null;
    },
    ...mapState({
      email: state => state.twitch.userEmail,
      userID: state => state.twitch.userID,
      displayName: state => state.twitch.userDisplayName,
      avatar: state => state.twitch.userAvatar
    })
  },

  beforeMount() {
    console.log("Token contains oauth-session");
    if (document.cookie.includes("oauth-session")) {
      this.$store.dispatch("requestDetails");
    }
  }
};
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
i {
  marign: 10px
}
#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
