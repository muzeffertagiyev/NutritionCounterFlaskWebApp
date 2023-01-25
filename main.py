import requests
import datetime as dt
import os

GENDER = 'male'
WEIGHT_KG = 75
HEIGHT_CM = 173
AGE = 24

NUTRITION_API_KEY = os.environ['NUTRITION_API_KEY']
NUTRITION_API_ID = os.environ['NUTRITION_API_ID']
NUTRITION_ENDPOINT = 'https://trackapi.nutritionix.com/v2/natural/exercise'

SHEET_ENDPOINT = os.environ['SHEET_ENDPOINT']


nutrition_headers = {
    'x-app-id': NUTRITION_API_ID,
    'x-app-key': NUTRITION_API_KEY
}
exercise_text = input('Tell me which exercise you did?: ')
nutrition_params = {
    'query': exercise_text,
    'gender': GENDER,
    'weight_kg': WEIGHT_KG,
    'height_cm': HEIGHT_CM,
    'age': AGE
}

nutrition_response = requests.post(url=NUTRITION_ENDPOINT, json=nutrition_params, headers=nutrition_headers)
nutrition_data = nutrition_response.json()['exercises']

sheet_headers = {
    'Authorization': f"Basic {os.environ['SHEET_TOKEN']}"
}
for exercise in nutrition_data:
    sheet_params = {
        'workout': {
            'date': dt.datetime.now().strftime('%d/%m/%Y'),
            'time': dt.datetime.now().strftime('%X'),
            'exercise': exercise['name'].title(),
            'duration': exercise['duration_min'],
            'calories': exercise['nf_calories']
        }
    }

    sheet_response = requests.post(url=SHEET_ENDPOINT, json=sheet_params, headers=sheet_headers)
    print(sheet_response.text)
