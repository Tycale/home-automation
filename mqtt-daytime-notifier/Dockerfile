FROM golang:1.19 as builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o mqtt-daytime-notifier .

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/mqtt-daytime-notifier .
CMD ["/root/mqtt-daytime-notifier"]
