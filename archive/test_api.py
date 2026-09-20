import requests
import pandas as pd

url = "https://api.jolpi.ca/ergast/f1/2024/races/"

headers = {
    "User-Agent": "F1RacePredictor/1.0"
}

response = requests.get(url, headers=headers)

data = response.json()

races = data["MRData"]["RaceTable"]["Races"]

race_list = []

for race in races:
    race_list.append({
        "round": race["round"],
        "race_name": race["raceName"],
        "date": race["date"],
        "circuit": race["Circuit"]["circuitName"]
    })

df = pd.DataFrame(race_list)

print(df)