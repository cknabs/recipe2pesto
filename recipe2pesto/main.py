import scrape_schema_recipe
from dict2pesto import dict2pesto

if __name__ == "__main__":
    url = 'https://www.foodnetwork.com/recipes/alton-brown/honey-mustard-dressing-recipe-1939031'
    recipe_list = scrape_schema_recipe.scrape_url(url, python_objects=True)
    recipe = recipe_list[0]
    print(recipe)

    pestoed = dict2pesto(recipe)
    print(pestoed)
