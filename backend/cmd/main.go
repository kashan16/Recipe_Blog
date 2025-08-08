package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/kashan16/recipe_blog/backend/internal/database"
	"github.com/kashan16/recipe_blog/backend/internal/handlers"
)

func main() {
	database.InitDB()
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "Recipe Blog API is up!")
	})

	fmt.Println("Server started at :8080")
	http.HandleFunc("/api/recipes", handlers.GetRecipeHanlers)
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal("Server failed : ", err)
	}
}
