<div align="center">



\# 🏎️ F1 Race Predictor



\### Machine Learning for Formula 1 Race Finishing Positions



Predicting race performance from qualifying, grid position, driver history, constructor performance, and circuit history.



<br>



!\[Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)

!\[scikit-learn](https://img.shields.io/badge/scikit--learn-Random%20Forest-F7931E?style=for-the-badge\&logo=scikit-learn\&logoColor=white)

!\[pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?style=for-the-badge\&logo=pandas\&logoColor=white)

!\[Status](https://img.shields.io/badge/Status-Working-2ea44f?style=for-the-badge)



</div>



\---



\## ⚡ Overview



\*\*F1 Race Predictor\*\* is a machine-learning project that predicts the finishing order of a Formula 1 race using information available before the race begins.



Instead of predicting finishing position directly, the model predicts:



> \*\*Position Change = Grid Position − Finishing Position\*\*



The predicted position change is then converted into an estimated finishing position and ranked across the field.



The final model uses a \*\*Random Forest Regressor\*\* trained on historical Formula 1 data.



\---



\## 🧠 How It Works



```text

Historical F1 Data

&#x20;       │

&#x20;       ▼

&#x20;  Data Cleaning

&#x20;       │

&#x20;       ▼

&#x20;Feature Engineering

&#x20;       │

&#x20;       ▼

Driver / Constructor / Circuit History

&#x20;       │

&#x20;       ▼

&#x20; Random Forest Model

&#x20;       │

&#x20;       ▼

Qualifying + Grid Information

&#x20;       │

&#x20;       ▼

&#x20;Predicted Position Change

&#x20;       │

&#x20;       ▼

Estimated Finishing Position

&#x20;       │

&#x20;       ▼

&#x20;  Predicted Race Order

📊 Blind Test — 2026 Spanish GP



One of the main goals of the project was to test the model on a race it had never seen during training.



For this experiment:



Training data ended at the 2026 Italian Grand Prix

The Spanish Grand Prix was excluded from training

Only pre-race information was supplied

The actual Spanish race result was hidden from the model

The prediction was generated before comparing it with the real result

Results



Using the evaluation convention that excludes the four drivers who retired:



Metric	Result

Within ±1 position	55.6%

Within ±2 positions	77.8%

Mean Absolute Error	1.83 positions

RMSE	2.37 positions

Exact position	11.1%



77.8% of classified drivers were predicted within two finishing positions of their actual result.



This is a single blind historical test and should not be interpreted as the model's general long-term accuracy.



🏁 Model



The final production model is a:



Random Forest Regressor

Parameter	Value

Trees	400

Maximum Depth	8

Maximum Features	sqrt

Minimum Samples per Leaf	1

Minimum Samples per Split	2

Random State	42



Random Forest was selected after comparing multiple regression approaches using chronological validation.



🔬 Features



The model uses 13 features covering pre-race information and historical performance.



Qualifying \& Grid

Grid position

Qualifying position

Qualifying-to-grid gap

Recent Driver \& Constructor Performance

Recent average finishing position

Recent finishing-position standard deviation

Recent average qualifying position

Recent average qualifying-to-finish change

Recent average constructor finishing position

Recent average constructor qualifying position

Circuit \& Position-Change History

Driver circuit history

Circuit average position change

Driver circuit average position change

Recent average position change



Historical features are calculated using previous races, preventing information from the current race from being used as an input.



📚 Dataset



The project uses historical Formula 1 race data covering:



2022

2023

2024

2025

2026 through the Italian Grand Prix

Training Dataset



2,124 driver-race records



105 races



13 model features



The Spanish Grand Prix was intentionally excluded from the training data for the blind-test experiment.



🛠️ Tech Stack

Technology	Purpose

Python	Core programming

pandas	Data processing

NumPy	Numerical operations

scikit-learn	Machine learning

Random Forest	Final prediction model

Git	Version control

GitHub	Project hosting

📁 Project Structure

F1-Race-Predictor/

│

├── build\_training\_dataset.py

├── train\_model.py

├── train\_final\_model.py

├── predict\_race.py

├── update\_raw\_data.py

│

├── f1\_2022\_2026\_raw.csv

├── f1\_training\_dataset.csv

├── race\_input.csv

├── requirements.txt

│

├── archive/

│   └── Development scripts

│

├── .gitignore

└── README.md

🚀 Run the Project

1\. Clone the repository

git clone https://github.com/MuzzammilSidd/F1-Race-Predictor.git

cd F1-Race-Predictor

2\. Create a virtual environment

python -m venv .venv

3\. Activate it



Windows:



.venv\\Scripts\\activate

4\. Install dependencies

pip install -r requirements.txt

5\. Build the training dataset

python build\_training\_dataset.py

6\. Train the final model

python train\_final\_model.py

7\. Enter race information



Update:



race\_input.csv



with:



Driver

Constructor

Circuit

Grid position

Qualifying position

8\. Generate a prediction

python predict\_race.py



The resulting prediction is written to:



race\_prediction.csv

🎯 Project Goals



This project was built to explore how machine learning can be applied to a sport where race outcomes depend on both measurable historical patterns and unpredictable events.



The focus was not simply on creating a model, but on building a complete pipeline:



Data → Features → Validation → Model → Prediction → Real-world Test



⚠️ Limitations



Formula 1 contains events that cannot reliably be predicted from pre-race information alone.



Examples include:



Mechanical failures

Accidents

Penalties

Safety cars

Weather changes

Strategy decisions

Race incidents



Because of this, the model should be treated as a statistical prediction system, not a guaranteed race-result generator.



🔮 Future Improvements



Potential improvements include:



Weather data

Practice-session performance

Tyre compounds and strategy

Sector and lap-time data

Pit-stop performance

Separate DNF prediction

Additional machine-learning models

Larger chronological validation sets

Interactive web interface

Live race prediction dashboard

<div align="center">

🏎️ Built with Python \& Machine Learning



Muzzammil Siddiqi



GitHub



</div> ```

