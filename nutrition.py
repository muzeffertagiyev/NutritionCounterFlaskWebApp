import requests
import os


NUTRITION_API_KEY = os.environ['API_KEY']
NUTRITION_API_ID = os.environ['API_ID']
NUTRITION_ENDPOINT = 'https://trackapi.nutritionix.com/v2/natural/exercise'


class CalorieCounter:

    def __init__(self,gender,weight_kg,height_cm,age,query):

        self.gender = gender
        self.weight_kg = weight_kg
        self.height_cm = height_cm
        self.age = age
        self.query = query

    
    def count(self):
        nutrition_headers = {
    'x-app-id': NUTRITION_API_ID,
    'x-app-key': NUTRITION_API_KEY
    }
        nutrition_params = {
    'query': self.query,
    'gender': self.gender,
    'weight_kg': self.weight_kg,
    'height_cm': self.height_cm,
    'age': self.age
    }

        nutrition_response = requests.post(url=NUTRITION_ENDPOINT, json=nutrition_params, headers=nutrition_headers)
        nutrition_data = nutrition_response.json()['exercises']

        return nutrition_data
