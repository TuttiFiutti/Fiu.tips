<template>
  <section>
    <b-field>
      <b-upload v-model="dropFiles" multiple drag-drop>
        <section class="section">
          <div class="content has-text-centered">
            <p>
              <b-icon icon="upload" size="is-large"> </b-icon>
            </p>
            <p>Drop your files here or click to upload</p>
          </div>
        </section>
      </b-upload>
    </b-field>

    <div class="tags">
      <span
        v-for="(file, index) in dropFiles"
        :key="index"
        class="tag is-primary"
      >
        {{ file.name }}
        <button
          class="delete is-small"
          type="button"
          @click="deleteDropFile(index)"
        ></button>
      </span>
    </div>
    <b-button @click="uploadFiles">Upload</b-button>
  </section>
</template>

<script>
export default {
  data() {
    return {
      dropFiles: []
    };
  },
  methods: {
    deleteDropFile(index) {
      this.dropFiles.splice(index, 1);
    },
    clearAllFiles() {
      this.dropFiles = [];
    },
    uploadFiles() {
      this.$store.dispatch("uploadFiles", { files: [...this.dropFiles] });
    }
  }
};
</script>

<style>
section {
  padding: 10px;
}
</style>
