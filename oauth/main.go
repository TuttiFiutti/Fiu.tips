/*
Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

	http://aws.amazon.com/apache2.0/

	or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

*/

package main

import (
	"context"
	"crypto/rand"
	"encoding/gob"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/sessions"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/twitch"
)

const (
	stateCallbackKey = "oauth-state-callback"
	oauthSessionName = "oauth-session"
	oauthTokenKey    = "oauth-token"
)

var (
	clientID = string(os.Getenv("CLIENT_ID"))
	// Consider storing the secret in an environment variable or a dedicated storage system.
	clientSecret = string(os.Getenv("CLIENT_SECRET"))
	scopes       = []string{"user:read:email"}
	redirectURL  = string(os.Getenv("REDIRECT_URI"))
	oauth2Config *oauth2.Config
	cookieSecret = []byte(os.Getenv("COOKIE_SECRET"))
	cookieStore  = sessions.NewCookieStore(cookieSecret)
)

// HandleRoot is a Handler that shows a login button. In production, if the frontend is served / generated
// by Go, it should use html/template to prevent XSS attacks.
func HandleRoot(w http.ResponseWriter, r *http.Request) (err error) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`<html><body><a href="/oauth/login">Login using Twitch</a></body></html>`))

	return
}

// HandleLogin is a Handler that redirects the user to Twitch for login, and provides the 'state'
// parameter which protects against login CSRF.
func HandleLogin(w http.ResponseWriter, r *http.Request) (err error) {
	session, err := cookieStore.Get(r, oauthSessionName)
	if err != nil {
		log.Printf("corrupted session %s -- generated new", err)
		err = nil
	}

	var tokenBytes [255]byte
	if _, err := rand.Read(tokenBytes[:]); err != nil {
		return AnnotateError(err, "Couldn't generate a session!", http.StatusInternalServerError)
	}

	state := hex.EncodeToString(tokenBytes[:])

	session.AddFlash(state, stateCallbackKey)

	if err = session.Save(r, w); err != nil {
		return
	}

	http.Redirect(w, r, oauth2Config.AuthCodeURL(state), http.StatusTemporaryRedirect)

	return
}

// HandleOauth2Callback is a Handler for oauth's 'redirect_uri' endpoint;
// it validates the state token and retrieves an OAuth token from the request parameters.
func HandleOAuth2Callback(w http.ResponseWriter, r *http.Request) (err error) {
	session, err := cookieStore.Get(r, oauthSessionName)
	if err != nil {
		log.Printf("corrupted session %s -- generated new", err)
		err = nil
	}

	// ensure we flush the csrf challenge even if the request is ultimately unsuccessful
	defer func() {
		if err := session.Save(r, w); err != nil {
			log.Printf("error saving session: %s", err)
		}
	}()

	switch stateChallenge, state := session.Flashes(stateCallbackKey), r.FormValue("state"); {
	case state == "", len(stateChallenge) < 1:
		err = errors.New("missing state challenge")
	case state != stateChallenge[0]:
		err = fmt.Errorf("invalid oauth state, expected '%s', got '%s'\n", state, stateChallenge[0])
	}

	if err != nil {
		return AnnotateError(
			err,
			"Couldn't verify your confirmation, please try again.",
			http.StatusBadRequest,
		)
	}

	token, err := oauth2Config.Exchange(context.Background(), r.FormValue("code"))
	if err != nil {
		return
	}

	// add the oauth token to session
	session.Values[oauthTokenKey] = token
	if err = session.Save(r, w); err != nil {
		return
	}

	fmt.Printf("Access token: %s, %v\n. ", token.AccessToken, token)

	http.Redirect(w, r, "/", http.StatusTemporaryRedirect)

	return
}

const (
	twitchUsersApiUri   = "https://api.twitch.tv/helix/users"
)

type Details struct {
	Email string `json:"email"`
	UserID string `json:"id"`
	DisplayName string `json:"display_name"`
	ProfilePicUri string `json:"profile_image_url"`
}


type TwitchUserAPIResponse struct {
	Data []Details `json:"data"`
}

type FallibleDetails struct {
	Payload Details
	Error error
}

func RequestDetailsFromTwitchAPI(queue chan FallibleDetails, accessToken string) {
	var details FallibleDetails
	req, err := http.NewRequest("GET", twitchUsersApiUri, nil)

	if err != nil {
		details.Error = err
		queue <- details
		return
	}

    req.Header.Add("Client-ID", clientID)
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", accessToken))
	log.Printf("Bearer %s", accessToken)
	resp, err := http.DefaultClient.Do(req)
	log.Printf("Response code from twitch: %d", resp.StatusCode)
	if err != nil {
		details.Error = err
		queue <- details
		return
	}



	var apiResponse TwitchUserAPIResponse
	err = json.NewDecoder(resp.Body).Decode(&apiResponse)

	if err != nil {
		details.Error = err
		queue <- details
		return
	}

	if len(apiResponse.Data) != 1 {
		details.Error = fmt.Errorf("Wrong data length in TwitchUserAPIResponse expected: 1 got: %d", len(apiResponse.Data))
		queue <- details
		return
	}

	details.Payload = apiResponse.Data[0]
	queue <- details

}

func HandleDetailsRequest(w http.ResponseWriter, r *http.Request) (err error) {
	session, err := cookieStore.Get(r, oauthSessionName)
	if err != nil {
		return
	}

	val, ok := session.Values[oauthTokenKey]

	if !ok {
		return fmt.Errorf("failed to get session.Values[oauthTokenKey]")
	}

	var token = &oauth2.Token{}
	if token, ok = val.(*oauth2.Token); !ok {
		return errors.New("failed to extract token from session")
	}

	messages := make(chan FallibleDetails, 1)
	go RequestDetailsFromTwitchAPI(messages, token.AccessToken)
	var details FallibleDetails
	select {
		case details = <- messages:
			if details.Error != nil {
				return details.Error
			}
			case <- time.After(2 * time.Second):
				return errors.New("2 seconds timeout")

	}

	err = json.NewEncoder(w).Encode(&details.Payload)
	return
}


// HumanReadableError represents error information
// that can be fed back to a human user.
//
// This prevents internal state that might be sensitive
// being leaked to the outside world.
type HumanReadableError interface {
	HumanError() string
	HTTPCode() int
}

// HumanReadableWrapper implements HumanReadableError
type HumanReadableWrapper struct {
	ToHuman string
	Code    int
	error
}

func (h HumanReadableWrapper) HumanError() string { return h.ToHuman }
func (h HumanReadableWrapper) HTTPCode() int      { return h.Code }

// AnnotateError wraps an error with a message that is intended for a human end-user to read,
// plus an associated HTTP error code.
func AnnotateError(err error, annotation string, code int) error {
	if err == nil {
		return nil
	}
	return HumanReadableWrapper{ToHuman: annotation, error: err}
}

type Handler func(http.ResponseWriter, *http.Request) error

func main() {
	// Gob encoding for gorilla/sessions
	gob.Register(&oauth2.Token{})

	oauth2Config = &oauth2.Config{
		ClientID:     clientID,
		ClientSecret: clientSecret,
		Scopes:       scopes,
		Endpoint:     twitch.Endpoint,
		RedirectURL:  redirectURL,
	}

	var middleware = func(h Handler) Handler {
		return func(w http.ResponseWriter, r *http.Request) (err error) {
			// parse POST body, limit request size
			if err = r.ParseForm(); err != nil {
				return AnnotateError(err, "Something went wrong! Please try again.", http.StatusBadRequest)
			}

			return h(w, r)
		}
	}

	// errorHandling is a middleware that centralises error handling.
	// this prevents a lot of duplication and prevents issues where a missing
	// return causes an error to be printed, but functionality to otherwise continue
	// see https://blog.golang.org/error-handling-and-go
	var errorHandling = func(handler func(w http.ResponseWriter, r *http.Request) error) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if err := handler(w, r); err != nil {
				var errorString string = "Something went wrong! Please try again."
				var errorCode int = 500

				if v, ok := err.(HumanReadableError); ok {
					errorString, errorCode = v.HumanError(), v.HTTPCode()
				}

				log.Println(err)
				w.Write([]byte(errorString))
				w.WriteHeader(errorCode)
				return
			}
		})
	}

	var handleFunc = func(path string, handler Handler) {
		http.Handle(path, errorHandling(middleware(handler)))
	}

	handleFunc("/oauth", HandleRoot)
	handleFunc("/oauth/login", HandleLogin)
	handleFunc("/oauth/redirect", HandleOAuth2Callback)
	handleFunc("/oauth/details", HandleDetailsRequest)
   
	fmt.Println(http.ListenAndServe("0.0.0.0:7001", nil))
}
