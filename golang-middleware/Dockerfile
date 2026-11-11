FROM golang:alpine AS builder
WORKDIR /app

ENV GOTOOLCHAIN=auto

COPY go.mod go.sum* ./
RUN go mod download || true

COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/server .
EXPOSE 8080 4573
CMD ["./server"]