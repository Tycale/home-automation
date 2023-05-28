FROM golang:alpine as builder
ARG TARGETOS TARGETARCH

RUN apk --no-cache add tzdata

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o mqtt-daytime-notifier .

FROM scratch

COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /app/mqtt-daytime-notifier /go/bin/mqtt-daytime-notifier
CMD ["/go/bin/mqtt-daytime-notifier"]
