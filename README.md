

# Calorie Counter Web Application

## Overview

The Calorie Counter Web Application is designed to help users manage their calorie intake and monitor their daily activities' impact on their health. It provides a simple and user-friendly interface for users to register, log in, add their personal details, calculate their BMI, and track their calorie consumption through various activities.

This project is built using Flask, SQLAlchemy for database management, and integrates with the Nutritionix API to fetch nutritional data for different activities.

## Introduction Video of the Website



https://github.com/muzeffertagiyev/NutritionCounterFlaskWebApp/assets/75939608/39092e65-609c-439e-bbdb-2386d65f8a0e



## Features

- **User Registration**: Users can create accounts by providing a username, email, and password.

- **User Authentication**: Registered users can log in securely.

- **Personal Details**: Users can add and update their personal details, including gender, weight, height, and age.

- **BMI Calculation**: The application calculates the user's BMI based on the provided weight and height.

- **Calorie Tracking**: Users can track their calorie consumption by logging various physical activities.

- **Nutritional Data**: Nutritional information for activities is fetched from the Nutritionix API.

## Setup

1. Clone the repository to your local machine.

2. Install the required packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

Configure the environment variables:

   - Create a `.env` file in the project root directory.
   - Add your Nutritionix API credentials to the `.env` file.

```env
NUTRITION_API_KEY=your_api_key_here
NUTRITION_API_ID=your_api_id_here
SECRET_KEY=your_secret_key_here
```


## Usage

1. Register for a new account or log in with an existing one.

2. Add your personal details, including gender, weight, height, and age.

3. Calculate your BMI based on the provided details.

4. Log various physical activities to track calorie consumption.

5. Log out when you're finished.



