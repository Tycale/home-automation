FROM golang:alpine as builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o mqtt-daytime-notifier .

FROM scratch
COPY --from=builder /app/mqtt-daytime-notifier /go/bin/mqtt-daytime-notifier
CMD ["/go/bin/mqtt-daytime-notifier"]
