package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

const (
	AGIPort    = ":4573"
	HTTPPort   = ":8080"
	MaxWorkers = 50
	QueueLimit = 1000
)

var (
	ctx = context.Background()
	rdb *redis.Client
)

func init() {
	rdb = redis.NewClient(&redis.Options{
		Addr:         "redis_service:6379",
		Password:     "",
		DB:           0,
		DialTimeout:  2 * time.Second,
		ReadTimeout:  1 * time.Second,
		WriteTimeout: 1 * time.Second,
	})
}

func main() {
	go startHTTPServer()

	listener, err := net.Listen("tcp", AGIPort)
	if err != nil {
		log.Fatalf("AGI listener error: %v", err)
	}
	defer listener.Close()

	callQueue := make(chan net.Conn, QueueLimit)

	for i := 0; i < MaxWorkers; i++ {
		go worker(callQueue)
	}

	for {
		conn, err := listener.Accept()
		if err != nil {
			continue
		}

		select {
		case callQueue <- conn:
		default:
			conn.Close()
		}
	}
}

func worker(queue <-chan net.Conn) {
	for conn := range queue {
		handleFastAGI(conn)
	}
}

func handleFastAGI(conn net.Conn) {
	defer conn.Close()
	_ = conn.SetDeadline(time.Now().Add(30 * time.Second))

	reader := bufio.NewReader(conn)
	writer := bufio.NewWriter(conn)

	agiEnv := make(map[string]string)
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			return
		}
		line = strings.TrimSpace(line)
		if line == "" {
			break
		}

		parts := strings.SplitN(line, ":", 2)
		if len(parts) == 2 {
			agiEnv[strings.TrimSpace(parts[0])] = strings.TrimSpace(parts[1])
		}
	}

	exten := agiEnv["agi_extension"]

	execute := func(cmd string) error {
		if _, err := writer.WriteString(cmd + "\n"); err != nil {
			return err
		}
		if err := writer.Flush(); err != nil {
			return err
		}
		_, err := reader.ReadString('\n')
		return err
	}

	destino, err := rdb.Get(ctx, fmt.Sprintf("dialplan:route:%s", exten)).Result()
	if err != nil {
		destino = "600"
	}

	_ = execute(fmt.Sprintf("SET VARIABLE DYNAMIC_DEST \"%s\"", destino))
	_ = execute(fmt.Sprintf("EXEC Goto \"default,%s,1\"", destino))
}

func startHTTPServer() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"ok"}`)
	})

	server := &http.Server{
		Addr:    HTTPPort,
		Handler: mux,
	}

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("HTTP listener error: %v", err)
	}
}