FROM golang
RUN mkdir app
COPY . app/
RUN cd app; go get -v .
CMD cd app; go get -v .; go run main.go