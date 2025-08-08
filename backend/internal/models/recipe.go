package models

import (
	"context"

	"github.com/kashan16/recipe_blog/backend/internal/database"
)

type Recipe struct {
	ID          string `json:"id"`
	UserID      string `json:"user_id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	ImageURL    string `json:"image_url"`
	CreatedAt   string `json:"created_at"`
}

func GetAllRecipes(ctx context.Context) ([]Recipe, error) {
	const sql = `SELECT id, user_id, title, description, image_url, created_at
	FROM recipes
	ORDER BY created_at DESC`

	rows, err := database.DB.Query(ctx, sql)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var recipes []Recipe
	for rows.Next() {
		var r Recipe
		if err := rows.Scan(&r.ID, &r.UserID, &r.Title, &r.Description, &r.ImageURL, &r.CreatedAt); err != nil {
			return nil, err
		}
		recipes = append(recipes, r)
	}
	return recipes, rows.Err()
}
