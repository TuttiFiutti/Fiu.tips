<template>
    <div>
        <i class="fa fa-5x fa-volume-up"></i>
        <b-field label="Volume">
            <b-slider v-model="volume"></b-slider>
        </b-field>
    </div>
</template>
<script>
export default {
  name: "SoundListener",
  data() {
    return {
      websocket: null,
      volume: 50,
    };
  },
  methods: {
    prepareWebSocket() {
      if (
        this.websocket === null ||
        this.websocket.readyState > WebSocket.OPEN
      ) {
        this.websocket = new WebSocket("wss://fiu.tips/ws/listen");
        this.websocket.onmessage = msg => {
          console.log(msg);
          let json = JSON.parse(msg.data);
          if ("path" in json) {
            let audio = new Audio(json["path"]);
            audio.volume = this.volume/100.;
            audio.play();
          }
        };
        this.websocket.onclose = () => this.prepareWebSocket();
        this.websocket.onerror = e => {
          console.log(e);
          setTimeout(() => this.prepareWebSocket(), 300);
        };
        this.websocket.onopen = e => {
          console.log(e);
          console.log(document.cookie.match("oauth-session=([\\w_=-]*);?")[1]);
          this.websocket.send(
            JSON.stringify({
              intent: "hello",
              "oauth-session": document.cookie.match(
                "oauth-session=([\\w_=-]*);?"
              )[1]
            })
          );
          console.log(this.websocket);
          console.log("Exiting open");
        };
      }
    }
  },
  mounted() {
    this.prepareWebSocket();
  }
};
</script>
