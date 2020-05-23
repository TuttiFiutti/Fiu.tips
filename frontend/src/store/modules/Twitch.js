const twitchModule = {
  state: {
    userID: null,
    userDisplayName: null,
    userAvatar: null,
    userEmail: null
  },
  mutations: {
    setupLoginData(state, payload) {
      state.userID = payload.userID;
      state.userDisplayName = payload.userDisplayName;
      state.userAvatar = payload.userAvatar;
      state.userEmail = payload.userEmail;
    }
  },
  getters: {},

  actions: {
    requestDetails({ commit }) {
      fetch("/oauth/details").then(response => {
        if (response.ok) {
          response.json().then(json => {
            let payload = {
              userID: json.id,
              userEmail: json.email,
              userDisplayName: json.display_name,
              userAvatar: json.profile_image_url
            };
            commit("setupLoginData", payload);
          });
        }
      });
    }
  }
};

export default twitchModule;
