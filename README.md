\# 🏎️ F1 Race Predictor



A machine-learning project that predicts Formula 1 race finishing positions using pre-race information and historical F1 performance data.



The project uses a Random Forest regression model to estimate how many positions each driver is expected to gain or lose relative to their starting grid position.



\---



\## 🎯 Project Objective



The goal is to build a machine-learning pipeline that can predict the finishing order of an F1 race using information available before the race begins.



The model does not simply predict finishing position directly.



Instead, it predicts:



\*\*Position Change = Grid Position − Finishing Position\*\*



The predicted position change is then converted into an estimated finishing position and ranked across the field.



\---



\## 📊 Data



Historical Formula 1 race data was collected for:



\- 2022

\- 2023

\- 2024

\- 2025

\- 2026 through the Italian Grand Prix



The pre-Spain training dataset contains:



\- \*\*2,124 driver-race records\*\*

\- \*\*105 races\*\*

\- \*\*13 model features\*\*



The Spanish Grand Prix was deliberately excluded from the training data for a blind historical validation experiment.



\---



\## 🧠 Features



The model uses 13 features derived from qualifying, driver performance, constructor performance and circuit history.



\### Pre-race features



\- Grid position

\- Qualifying position

\- Qualifying-to-grid gap



\### Recent performance



\- Recent average finishing position

\- Recent finishing-position standard deviation

\- Recent average qualifying position

\- Recent average qualifying-to-finish change

\- Recent average constructor finishing position

\- Recent average constructor qualifying position



\### Circuit and position-change history



\- Driver circuit history

\- Circuit average position change

\- Driver circuit average position change

\- Recent average position change



Historical features are calculated using previous races so that information from the current race is not used as an input.



\---



\## 🤖 Model



Several regression models were evaluated during development.



The final production model is:



\*\*Random Forest Regressor\*\*



Configuration:



\- Trees: 400

\- Maximum depth: 8

\- Maximum features: sqrt

\- Random state: 42

\- Minimum samples per leaf: 1

\- Minimum samples per split: 2



Random Forest was selected based on the chronological validation experiments performed during development.



\---



\## 🧪 Blind Spanish GP Test



To test the model on a completely unseen race, the model was trained only on races through the 2026 Italian Grand Prix.



The 2026 Spanish Grand Prix was then supplied only with information available before the race:



\- Driver

\- Constructor

\- Circuit

\- Grid position

\- Qualifying position



The actual Spanish Grand Prix race result was not provided to the model.



\### Result



Excluding the four drivers who retired from the race:



| Metric | Result |

|---|---:|

| Within ±1 position | \*\*55.6%\*\* |

| Within ±2 positions | \*\*77.8%\*\* |

| Mean Absolute Error | \*\*1.83 positions\*\* |

| RMSE | \*\*2.37 positions\*\* |

| Exact position | \*\*11.1%\*\* |



This was a single blind historical test and should not be interpreted as the model's general long-term accuracy.



\---



\## 🔄 Prediction Pipeline



```text

Historical F1 Data

&#x20;       ↓

Data Cleaning

&#x20;       ↓

Feature Engineering

&#x20;       ↓

Historical Driver / Constructor / Circuit Features

&#x20;       ↓

Random Forest Training

&#x20;       ↓

Qualifying + Grid Information

&#x20;       ↓

Predicted Position Change

&#x20;       ↓

Estimated Finishing Position

&#x20;       ↓

Predicted Race Order

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

🚀 How to Run

1\. Create and activate a virtual environment

python -m venv .venv



Windows:



.venv\\Scripts\\activate

2\. Install dependencies

pip install -r requirements.txt

3\. Build the training dataset

python build\_training\_dataset.py

4\. Train the final model

python train\_final\_model.py

5\. Enter the race information



Update:



race\_input.csv



with the drivers, constructors, circuit, grid positions and qualifying positions for the race.



6\. Generate a prediction

python predict\_race.py



The predicted result is saved to:



race\_prediction.csv

🛠️ Technologies

Python

pandas

NumPy

scikit-learn

Random Forest

Git / GitHub

📌 Limitations



Formula 1 races contain unpredictable events that are difficult to model from pre-race information alone.



Examples include:



Mechanical failures

Accidents

Penalties

Safety cars

Weather changes

Strategy decisions

Race incidents



Therefore, the model should be interpreted as a statistical prediction of expected race performance rather than a guaranteed race result.



👤 Author



Muzzammil Siddiqi



GitHub: @MuzzammilSidd

