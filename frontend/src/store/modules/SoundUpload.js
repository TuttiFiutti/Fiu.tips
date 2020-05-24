const uploadModule = {
  state: {
    startedUpload: false,
    recentlyFinishedUploading: false,
    availableSounds: []
  },
  mutations: {
    startUpload(state) {
      state.startedUpload = true;
      state.finishedUploadingWhen = new Date();
      state.recentlyFinishedUploading = false;
    },
    finishUpload(state, view) {
      state.startedUpload = false;
      state.finishedUploadingWhen = Date.now();
      state.recentlyFinishedUploading = true;
      view.clearAllFiles();
    },
    markStale(state) {
      state.recentlyFinishedUploading = false;
    },
    failUpload(state) {
      state.startedUpload = false;
    },
    updateMeta(state, meta) {
      state.availableSounds = meta;
    }
  },
  actions: {
    uploadFiles({ commit }, payload) {
      commit("startUpload");
      let formData = new FormData();
      for (let i = 0; i < payload.files.length; ++i) {
        formData.append("sounds", payload.files[i]);
      }

      fetch("https://fiu.tips/api/upload", {
        credentials: "include",
        method: "POST",
        mode: "cors",
        body: formData
      })
        .then(response => {
          console.log(response.body);
          return response.json();
        })
        .then(response => {
          if (response.status === "ok") {
            commit("finishUpload", payload.view);
            setTimeout(() => commit('markStale'), 2000);
          } else {
            commit("failUpload");
          }
        })
        .catch(error => {
          commit("failUpload");
          console.log(error);
        });
    },
    requestMeta({ commit }) {
      fetch("https://fiu.tips/api/meta")
        .then(response => response.json())
        .then(json => commit("updateMeta", json))
        .catch(err => console.log(err));
    }
  }
};
export default uploadModule;
