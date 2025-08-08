package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"github.com/kashan16/recipe_blog/backend/db"
)

func main() {
	db.Connect()
	r := gin.Default()
	r.GET("/", func(ctx *gin.Context) {
		ctx.JSON(200, gin.H{"message": "Welcome to Recipe_Blog"})
	})
	log.Fatal(r.Run(":8081"))
}
