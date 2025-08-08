package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/kashan16/recipe_blog/backend/internal/models"
)

func GetRecipeHanlers(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "public, max-age=60")

	recipes, err := models.GetAllRecipes(r.Context())
	if err != nil {
		http.Error(w, "Could not load recipes", http.StatusInternalServerError)
		return
	}

	if err := json.NewEncoder(w).Encode(recipes); err != nil {
		http.Error(w, "Failed to encode recipes", http.StatusInternalServerError)
		return
	}
}
