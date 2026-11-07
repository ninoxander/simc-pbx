package main

import (
	"fmt"
	"net/http"
)

func main() {
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"go-security ok"}`)
	})

	println("Servidor Golang Middleware escuchando en :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}