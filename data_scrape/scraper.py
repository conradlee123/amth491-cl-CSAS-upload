#Scraper.py
#Conrad Lee
#scrapes webpage information and puts into a text file
#This is so that I can get the college soccer scores
#Used with https://github.com/henrygd/ncaa-api?tab=readme-ov-file (not included in this repo yet)


import requests
import csv
from bs4 import BeautifulSoup
import copy

def save_webpage_text(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(text + '\n')
        
        print(f"Text saved to {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")

# Example usage
#url = "http://localhost:3000/scoreboard/soccer-men/d1/2024/12/16/all-conf"
#filename = "output.txt"
#save_webpage_text(url, filename)

def iterate_scores(year, start_month, end_month, end_day):
    s_vyear = str(year)
    vmonth = start_month
    vday = 1
    while (vmonth <= end_month):
        while (vday <= 31 and (vday <= end_day or vmonth < end_month)):
            s_vday = str(vday)
            if vday < 10:
                s_vday = "0" + str(vday)

            s_vmonth = str(vmonth)
            if vmonth < 10:
                s_vmonth = "0" + str(vmonth)
            c_url = "http://localhost:3000/scoreboard/soccer-men/d1/" + s_vyear + "/" + s_vmonth + "/" + s_vday + "/all-conf"
            save_webpage_text(c_url, "scores.txt")
            vday = vday + 1
        
        vmonth = vmonth + 1
        vday = 1

    


#iterate_scores(2024, 8, 11, 19)

def itemize_score_text():
    #(NOTE: score doesn't include penalties, which reflects how RPI is calculated)

    #Game state
    #Home team
    #home team score
    #Away team
    #Away team score
    #Result, for ranking purposes (calculated)
    #was played on neutral setting?
    #date

    #first need to parse

    with open(filename, 'r', encoding='utf-8') as file_txt:
        with open("scores_final.csv", mode="a", newline="") as file_csv:
            writer = csv.writer(file_csv)
            writer.writerow(["GameState", "Home Team", "Home Score", "Away Team", "Away Score", "Result", "Neutral?", "Date"])



import json

def save_json(url):
    # Fetch JSON data from the website
    response = requests.get(url)

    if response.status_code == 200:  # Check if the request was successful
        data = response.json()  # Convert response to JSON format

        # Save JSON data to a file
        with open("scores_temp.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

        print("JSON file saved successfully as 'data.json'.")

        #now append to a csv by parsing
        with open("scores_temp.json", "r", encoding="utf-8") as json_file:
            with open("scores_final.csv", mode="a", newline="") as file_csv:
                writer = csv.writer(file_csv)
                #header = ["GameState", "HomeTeam", "HomeScore", "AwayTeam", "AwayScore", "Result", "WasNeutral", "Date"]
                #writer.writerow(header)
                data = json.load(json_file)["games"]
                for entry in data:
                    """
                    writer.writerow({
                        "GameState": entry["game"]["gameState"],
                        "HomeTeam": entry["game"]["home"]["names"]["short"],
                        "HomeScore": entry["game"]["home"]["score"],
                        "AwayTeam": entry["game"]["away"]["names"]["short"],
                        "AwayScore": entry["game"]["away"]["score"],
                        "Result": entry["game"]["gameState"], #TODO: fix
                        "WasNeutral": entry["game"]["gameState"], #TODO: Fix this after the fact. Could either do it manually-- Or make something that pulls a team's home stadium, and see if the stadium matches up. No other way to do it
                        "Date": entry["game"]["startDate"]
                    })
                    """
                    hscore = entry["game"]["home"]["score"]
                    ascore = entry["game"]["away"]["score"]

                    hresult = 0
                    if hscore > ascore:
                        hresult = 1
                    elif hscore < ascore:
                        hresult = -1

                    writer.writerow([
                        entry["game"]["gameState"],
                        entry["game"]["home"]["names"]["short"],
                        hscore,
                        entry["game"]["away"]["names"]["short"],
                        ascore,
                        hresult, 
                        entry["game"]["gameState"], #TODO: Fix this after the fact. Could either do it manually-- Or make something that pulls a team's home stadium, and see if the stadium matches up. No other way to do it
                        entry["game"]["startDate"],  #TODO: add game id
                        entry["game"]["url"]
                    ])           

    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")


def get_home_fields():
    #Next, for each home team, save the venue.
    #best data structure-- Nested dictionary-- dictionary of dictionaries

    team_homefields = {}

    with open("scores_final.csv", mode="r", newline="") as file_csv:
        reader = csv.reader(file_csv)

        rowNum = 0
        for row in reader:

            homeTeam = row[1]
            if homeTeam not in team_homefields:
                team_homefields[homeTeam] = {}
            homeKey = team_homefields[homeTeam]


            link = row[8]

            response2 = requests.get("http://localhost:3000" + link)
            if response2.status_code == 200:  # Check if the request was successful
                data2 = response2.json()["contests"]
                for entry2 in data2:

                    loc = entry2["location"]
                    if loc is not None:
                        venueName = entry2["location"]["venue"]
                        if venueName not in homeKey:
                            homeKey[venueName] = [link]
                        else:
                            homeKey[venueName].append(link)
                    else:
                        if "None" not in homeKey:
                            homeKey["None"] = [link]
                        else:
                            #print(homeTeam)
                            #print(homeKey)
                            #print(link)
                            #print("HomeKey is: " + str(homeKey["None"]))
                            homeKey["None"].append(link)
                    

                    print("Successfully pulled game number " + str(rowNum))
                    rowNum = rowNum + 1

            #if homeTeam == "VMI":          
                #print(link)
                #print(team_homefields)
            
    #1890 games
    print(team_homefields)

    with open('homefields.txt', 'w') as file:
        json.dump(team_homefields, file)

    return team_homefields







def reduce_homefields(team_homefields):
    #cutoff for home games needed to be NCAA D1: 3
    thf = copy.deepcopy(team_homefields)
    for key in thf:
        numHome = 0
        for field in thf[key]:
            numHome = numHome + len(thf[key][field])

        if numHome >= 3:
            for field in thf[key]:
                #print(thf[key][field])
                if len(thf[key][field]) >= 3:
                    thf[key][field] = []
        else:
            thf[key] = []

        #now unnest the dict
        final_games_neutral = []
        if thf[key] != []:
            for field in thf[key]:
                final_games_neutral = final_games_neutral + thf[key][field]
            thf[key] = final_games_neutral

    print(thf)
    return thf


def add_neutrals(neutral_games):
    #Finally, create a new csv that has the neutral sites
    with open("scores_final.csv", mode="r", newline="") as final_csv:
        #n = 0
        with open("scores_final_neutrals.csv", mode="w", newline="") as neutral_csv:
            writer = csv.writer(neutral_csv)
            reader = csv.reader(final_csv)

            writer.writerow(["Game State", "Home Team", "Home Score", "Away Team", "Away Score", "Result", "Neutral Field?", "Date", "NCAA Game ID Link"])

            for row in reader:
                row_updated = row
                homeTeam = row_updated[1]
                link = row_updated[8]
                isGameNeutral = 0
                for game in neutral_games[homeTeam]:
                    if link == game:
                        isGameNeutral = 1  

                row_updated[6] = isGameNeutral
                writer.writerow(row_updated)




def iterate_scores_json(year, start_month, end_month, end_day):
    s_vyear = str(year)
    vmonth = start_month
    vday = 1
    while (vmonth <= end_month):
        while (vday <= 31 and (vday <= end_day or vmonth < end_month)):
            s_vday = str(vday)
            if vday < 10:
                s_vday = "0" + str(vday)

            s_vmonth = str(vmonth)
            if vmonth < 10:
                s_vmonth = "0" + str(vmonth)
            c_url = "http://localhost:3000/scoreboard/soccer-men/d1/" + s_vyear + "/" + s_vmonth + "/" + s_vday + "/all-conf"
            
            save_json(c_url)
            vday = vday + 1
        
        vmonth = vmonth + 1
        vday = 1



#Comment out as needed
#iterate_scores_json(2024, 8, 11, 19)
#thf = get_home_fields()

loaded_dict = {}
with open('homefields.txt', 'r') as file_c:
    loaded_dict = json.load(file_c)

rhf = reduce_homefields(loaded_dict)

add_neutrals(rhf)
