# parser imports
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import Optional

class RecommendedRecipe(BaseModel):
    RecipeName: str=Field(description='The name of the recipe')
    Ingredients: list[str]=Field(description='The ingedients required for making the recipe')
    Instructions:list[str]=Field(description='Cooking instructions')
    Cuisine:str=Field(description='Cuisine of the recipe')
    Course:str=Field(description='Course of the recipe')
    Diet:str=Field(description='Diet of the recipe')
    PrepTime: Optional[int]=Field(default=None,description="Preparation time in minutes)")
    CookingTime: Optional[int]=Field(default=None,description="Cooking time in minutes")
    TotalTime: Optional[int]=Field(default=None,description="Total time in minutes")
    Servings:int=Field(default=None,description='Number of servings')
    NumOfIngredients:int=Field(default=None,description='Number of ingredients')
    SourceURL:str=Field('Source URL of the Recipe')
    MissingIngredients:str=Field('Ingredients requested by the user but missing in the recipe')
    Explanation:str=Field('Why this recipe is the closest match')