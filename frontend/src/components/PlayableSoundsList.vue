<template>
  <v-card>
    <v-card-title>
      <v-text-field
        v-model="search"
        append-icon="fa-search"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="songs"
      :search="search"
      @click:row="handleClick"
    ></v-data-table>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      headers: [
        { text: "Uploader", value: "display_name" },
        { text: "Filename", value: "filename" }
      ],
      websocket: null,
      authorized: false,
      search: ""
    };
  },
  computed: {
    songs() {
      return this.$store.state.sound.availableSounds;
    }
  },
  mounted() {
    this.$store.dispatch("requestMeta");
  },
  methods: {
    log(e) {
      console.log(e);
    },
    prepareWebSocket() {
      if (
        this.websocket === null ||
        this.websocket.readyState > WebSocket.OPEN
      ) {
        this.websocket = new WebSocket("wss://fiu.tips/ws/push");
        this.websocket.onmessage = msg => {
          console.log(msg);
          let json = JSON.parse(msg.data);
          if ("status" in json && json["status"].localeCompare("ok") == 0) {
            this.authorized = true;
          }
        };
        this.websocket.onclose = () => console.log("WS closed");
        this.websocket.onerror = e => console.log(e);
        this.websocket.onopen = e => {
          console.log(e);
          console.log(document.cookie.match("oauth-session=([\\w-=]*);?")[1]);
          this.websocket.send(
            JSON.stringify({
              intent: "hello",
              "oauth-session": document.cookie.match(
                "oauth-session=([\\w-=]*);?"
              )[1]
            })
          );
          console.log(this.websocket);
          console.log("Exiting open");
        };
      }
    },
    handleClick(e) {
      this.log(e);
      this.prepareWebSocket();
      setTimeout(
        () => this.trySendingSound({ intent: "push", path: e.path }, 5),
        200
      );
    },
    trySendingSound(sound, retries) {
      if (retries <= 0) {
        return;
      }
      if (
        this.websocket != null &&
        this.websocket.readyState === WebSocket.OPEN &&
        this.authorized
      ) {
        this.websocket.send(JSON.stringify(sound));
      } else {
        console.log("Retrying in 500ms");
        setTimeout(() => this.trySendingSound(sound, retries - 1), 500);
      }
    }
  }
};
</script>

<style scoped>
v-list {
  margin: 20px;
}
</style>
