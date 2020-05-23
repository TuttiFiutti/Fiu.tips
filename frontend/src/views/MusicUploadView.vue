<template>
  <v-app>
    <v-content>
      <v-container class="fill-height">
        <v-row align="center" justify="center">
          <v-col cols="18" sm="8" md="4">
            <MusicUploader />
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import MusicUploader from "../components/MusicUploader";
export default {
  props: {
    source: String
  },
  components: { MusicUploader }
};
</script>

<style scoped></style>
