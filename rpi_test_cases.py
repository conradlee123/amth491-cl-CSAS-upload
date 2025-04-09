from collections import defaultdict

def calculate_rpi(matches):
    teams = set()
    records = defaultdict(lambda: {'wins': 0, 'games': 0, 'opponents': []})
    
    # Process match results
    gm = 0
    for match in matches:
        gm = gm + 1
        team1, score1, team2, score2 = match
        teams.update([team1, team2])
        records[team1]['games'] += 1
        records[team2]['games'] += 1
        records[team1]['opponents'].append(team2)
        records[team2]['opponents'].append(team1)
        
        if score1 > score2:
            records[team1]['wins'] += 1
        else:
            records[team2]['wins'] += 1
    
    # Compute WP
    wp = {team: (rec['wins'] / rec['games'] if rec['games'] > 0 else 0) for team, rec in records.items()}
    
    # Compute OWP
    owp = {}
    for team in teams:
        opponent_wps = []
        for opp in records[team]['opponents']:
            opp_record = records[opp]
            #if opp_record['games'] > 1:  # Exclude games against current team
            opp_wp = (opp_record['wins']) / (opp_record['games'])
            opponent_wps.append(opp_wp)
        owp[team] = sum(opponent_wps) / len(opponent_wps) if opponent_wps else 0
    
    # Compute OOWP
    oowp = {}
    for team in teams:
        opponent_owps = [owp[opp] for opp in records[team]['opponents'] if opp in owp]
        oowp[team] = sum(opponent_owps) / len(opponent_owps) if opponent_owps else 0
    
    # Compute RPI
    rpi = {team: [0.25 * wp[team] + 0.50 * owp[team] + 0.25 * oowp[team], wp[team], owp[team], oowp[team]] for team in teams}
    #_wp = {team: wp[team] for team in teams}
    #_owp = {team: owp[team] for team in teams}
    #_oowp = {team: oowp[team] for team in teams}
    
    #return [rpi, _wp, _owp, _oowp]
    return rpi

# Example usage
"""
matches = [
    ("A1", 1, "A2", 0),
    ("A1", 1, "A3", 0),
    ("A2", 1, "A3", 0),
    ("B1", 1, "B2", 0),
    ("B1", 1, "B3", 0),
    ("B2", 1, "B3", 0),
    ("C1", 1, "C2", 0),
    ("C1", 1, "C3", 0),
    ("C2", 1, "C3", 0),
    ("A1", 1, "B1", 0),
    ("A1", 1, "C1", 0),
    ("B1", 1, "C1", 0),
    ("A2", 1, "B2", 0),
    ("A2", 1, "C2", 0),
    ("B2", 1, "C2", 0),
    ("A3", 1, "B3", 0),
    ("A3", 1, "C3", 0),
    ("B3", 1, "C3", 0)
]
"""

matches = [
    ("A1", 1, "A2", 0),
    ("A1", 1, "A3", 0),
    ("A2", 1, "A3", 0),
    ("B1", 1, "B2", 0),
    ("B1", 1, "B3", 0),
    ("B2", 1, "B3", 0),
    ("A1", 1, "B3", 0),
    #("A1", 1, "B3", 0),
    #("A2", 1, "B4", 0),
    ("A2", 1, "B2", 0),
    ("B1", 1, "A3", 0),
    #("B1", 1, "A3", 0),
    #("B2", 1, "A4", 0),
    ("A3", 0, "B1", 1)
]


rpi_values = calculate_rpi(matches)

#for team, rpi in sorted(rpi_values.items(), key=lambda x: x[1], reverse=True): 
    #print(f"{team}: {rpi:.4f}")

print("    RPI    WP     OWP    OOWP")
for team in sorted(rpi_values):
    rpi = "{:.4f}".format(round(rpi_values[team][0], 4))
    wp = "{:.4f}".format(round(rpi_values[team][1], 4))
    owp = "{:.4f}".format(round(rpi_values[team][2], 4))
    oowp = "{:.4f}".format(round(rpi_values[team][3], 4))
    print(team + ": " + rpi + " " + wp + " " + owp + " " + oowp)
