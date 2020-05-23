<template>
  <div id="app">
    <v-app-bar color="grey lighten-4" height="60px">
      <router-link to="/">Home</router-link>
      |
      <router-link to="/about">About</router-link>
      |
      <router-link to="/soundboard/upload">Upload</router-link>
      |
      <router-link to="/soundboard">Soundboard</router-link>
      |
      <router-link to="/listen">Listen</router-link>
      <v-spacer />
      <a v-if="!loggedIn" href="/oauth/login">Login with Twitch</a>
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
