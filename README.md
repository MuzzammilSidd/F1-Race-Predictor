🏎️ F1 Race Predictor

Machine Learning for Formula 1 Race Finishing Positions



<img src="https://readme-typing-svg.demolab.com?font=Fira+Code\&size=18\&duration=3000\&pause=1000\&center=true\&vCenter=true\&width=650\&lines=Qualifying+%E2%86%92+Features+%E2%86%92+Machine+Learning+%E2%86%92+Race+Prediction;Predicting+F1+finishing+positions+with+historical+data;Built+with+Python+%26+scikit-learn" alt="Typing animation">

🏁 Overview



F1 Race Predictor is a machine-learning project designed to predict Formula 1 race finishing positions using information available before the race.



The model combines qualifying performance, starting grid position, recent driver performance, constructor performance, and circuit history.



Instead of predicting the finishing position directly, the model predicts how many positions a driver is expected to gain or lose from their starting grid position.



⚡ Features

🏎️ Historical Formula 1 data processing

📊 Automated feature engineering

🧠 Random Forest regression

🏁 Race finishing-order prediction

📈 Driver and constructor performance analysis

🌍 Circuit-specific historical features

🧪 Chronological model validation

🔬 Blind historical race testing

📊 Blind Test — 2026 Spanish GP



The model was deliberately trained without the 2026 Spanish Grand Prix.



Training data ended with the 2026 Italian Grand Prix.



The Spanish GP was then supplied only with information available before the race:



Driver · Constructor · Circuit · Grid · Qualifying



The actual race result was kept hidden until after the prediction was generated.



Results

Metric	Result

Within ±1 position	55.6%

Within ±2 positions	77.8%

Mean Absolute Error	1.83 positions

RMSE	2.37 positions



🎯 77.8% of classified drivers were predicted within two finishing positions of their actual result.



The four race retirements were excluded from this particular evaluation.



🧠 Model

Random Forest Regressor



The final model uses:



🌲 400 trees

📏 Maximum depth: 8

🎲 Random state: 42

🔀 Maximum features: sqrt

📦 Minimum samples per leaf: 1

📦 Minimum samples per split: 2



Random Forest was selected after chronological validation against alternative regression approaches.



🔬 Features



The model uses 13 engineered features covering qualifying performance, recent performance, constructor performance, and circuit history.



Qualifying \& Grid

Grid position

Qualifying position

Qualifying-to-grid gap

Recent Performance

Recent average finishing position

Recent finishing-position standard deviation

Recent average qualifying position

Recent average qualifying-to-finish change

Recent average constructor finishing position

Recent average constructor qualifying position

Circuit \& Position History

Driver circuit history

Circuit average position change

Driver circuit average position change

Recent average position change



Historical features are calculated using previous races so that information from the current race is not used as an input.



📚 Dataset



Historical Formula 1 data covers:



2022 → 2026 Italian Grand Prix



The training dataset contains:



2,124 driver-race records

105 races

13 model features



The Spanish Grand Prix was intentionally excluded from training for the blind-test experiment.



🔄 Prediction Pipeline



The system follows a simple pipeline:



Historical F1 Data



↓



Data Cleaning



↓



Feature Engineering



↓



Driver / Constructor / Circuit History



↓



Random Forest Model



↓



Qualifying + Grid Information



↓



Predicted Position Change



↓



Estimated Finishing Position



↓



Predicted Race Order



🛠️ Tech Stack

🐍 Python — Core development

🐼 pandas — Data processing

🔢 NumPy — Numerical operations

🤖 scikit-learn — Machine learning

🌲 Random Forest — Prediction model

🔧 Git — Version control

☁️ GitHub — Project hosting

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

🚀 Run Locally

1\. Clone the repository

git clone https://github.com/MuzzammilSidd/F1-Race-Predictor.git

cd F1-Race-Predictor

2\. Create a virtual environment

python -m venv .venv

3\. Activate the environment



Windows:



.venv\\Scripts\\activate

4\. Install dependencies

pip install -r requirements.txt

5\. Build the training dataset

python build\_training\_dataset.py

6\. Train the model

python train\_final\_model.py

7\. Enter race information



Update race\_input.csv with:



Driver

Constructor

Circuit

Grid position

Qualifying position

8\. Generate a prediction

python predict\_race.py



The predicted race order is saved to:



race\_prediction.csv

⚠️ Limitations



Formula 1 contains unpredictable events that cannot always be inferred from pre-race information.



Examples include:



Mechanical failures

Accidents

Penalties

Safety cars

Weather changes

Strategy decisions

Race incidents



The model should therefore be viewed as a statistical prediction system, not a guaranteed race-result generator.



🔮 Future Development



Potential improvements include:



🌦️ Weather information

🛞 Tyre compounds and strategy

⏱️ Practice and sector times

🔧 Pit-stop performance

🚨 Dedicated DNF prediction

🤖 Additional machine-learning models

📊 Larger chronological validation

🌐 Interactive web interface

📡 Live race prediction dashboard



🏎️ Built with Python • pandas • scikit-learn



👤 Author

Muzzammil Siddiqi





