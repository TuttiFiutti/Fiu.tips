<template type="pug">
  <v-app id="inspire">
    <v-content>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="3" md="8">
          <PlayableSoundsList />
        </v-col>
      </v-row>
    </v-content>
  </v-app>
</template>

<script>
import PlayableSoundsList from "../components/PlayableSoundsList";
export default {
  name: "MusicPlayView",
  components: { PlayableSoundsList }
};
</script>

<style scoped>
v-content {
  margin: 100px;
}
</style>
