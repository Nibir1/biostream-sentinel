# Stage 1: Build Go Binary
FROM golang:1.22-alpine AS builder
WORKDIR /app

# 1. Install git (Required if dependencies need to be fetched from VCS)
RUN apk add --no-cache git

# 2. Copy BOTH go.mod
COPY go.mod ./

# 3. Download dependencies
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o simulator .

# Stage 2: Tiny Runtime
FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/simulator .
CMD ["./simulator"]