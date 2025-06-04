# Workshop Forecasting using Classical Models

This repository contains a Flask application designed to perform forecasting using classical models. The application allows users to select from a variety of forecasting models to predict future values based on a dataset collected from a real workshop.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Data Collection](#data-collection)
- [Installation](#installation)
- [Usage](#usage)
- [Models](#models)
- [Demo](#demo)
- [Advantages of Classical Models](#advantages-of-classical-models)
- [Contributions](#contributions)
- [License](#license)

## Overview
This application leverages classical forecasting models due to their efficiency in terms of disk size and speed. Classical models are particularly advantageous for scenarios where quick forecasting and minimal storage requirements are essential.

## Features
- Select from multiple forecasting models.
- Predict future sales based on historical data.
- Visualize forecasting results with plots.
- Lightweight and fast performance.

## Data Collection
Using Selenium and automation in Python, I extracted data from https://apps.semadata.org/Account/Login?ReturnUrl=%2F. A friend provided the necessary credentials, allowing me to scrape large volumes of data by making GET requests with the required parameters to retrieve yearly sales data for each product. The file named final.csv contains the finalized and cleaned dataset collected from the website.

## Installation
To get started with the application, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anasahmedde142002/Workshop-Forecasting-using-classical-models.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd Workshop-Forecasting-using-classical-models
   ```
3. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
## Usage
Once the environment is set up, you can start the Flask application by running:
```bash
flask run
```
The application will be accessible at http://127.0.0.1:5000/.

## Models
The following models are available for selection within the application:

- XGBoost
- EWMA (Exponentially Weighted Moving Average)
- ARIMA (AutoRegressive Integrated Moving Average)
- AUTO ARIMA
- GARCH (Generalized Autoregressive Conditional Heteroskedasticity)

## Demo
Explore the live demo of the project at the following link: [Workshop Forecasting Demo](https://anasahmeddeahmed1462002.pythonanywhere.com/).

> **Note:** When selecting the XGBoost model for forecasting, please be aware that generating the plot might take some additional time due to the model's complexity as the application is depployed using free service of pythonanywhere.com.
![Screenshot 2024-08-19 160231](https://github.com/user-attachments/assets/526a86f2-8bd5-4a13-9d52-6901df3b4444)

## Advantages of Classical Models
Classical models have significant advantages, including:

- Low Disk Size: Classical models require minimal storage space, making them ideal for systems with limited resources.
- Fast Evaluation: These models can quickly generate forecasts, which is critical in real-time applications.
- High Accuracy: Models like XGBoost and EWMA can produce forecasts that closely match actual sales data.

## Contributions
Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## License
This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software in accordance with the terms of the license.

