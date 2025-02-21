import os
import re
import csv
import json
from collections import defaultdict

def get_stage_value(stage):
    """Convert tournament stage to numerical value"""
    stages = {
        'Group': 1,
        'Round of 16': 2,
        'Quarter-finals': 3,
        'Semi-finals': 4,
        'Match for third place': 5,
        'Final': 6,
        'Winner': 7
    }
    return stages.get(stage, 0)

def extract_team_data_csv(csv_file, year):
    """Extract performance metrics for all teams from a CSV file for a given year.
       Metrics: highest stage reached, wins, clean sheets, matches played, goals scored."""
    team_data = defaultdict(lambda: {
        'matches': 0,
        'wins': 0,
        'clean_sheets': 0,
        'highest_stage': 0,
        'goals_scored': 0
    })
    
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team1 = row['Team1'].strip()
            team2 = row['Team2'].strip()
            try:
                score1 = int(row['Team1 Score'])
                score2 = int(row['Team2 Score'])
            except ValueError:
                continue  # skip malformed rows
                
            stage = row['Stage'].strip()
            stage_val = get_stage_value(stage)
            
            # Update for team1
            team_data[team1]['matches'] += 1
            team_data[team1]['goals_scored'] += score1
            if score1 > score2:
                team_data[team1]['wins'] += 1
            if score2 == 0:
                team_data[team1]['clean_sheets'] += 1
            team_data[team1]['highest_stage'] = max(team_data[team1]['highest_stage'], stage_val)
            
            # Update for team2
            team_data[team2]['matches'] += 1
            team_data[team2]['goals_scored'] += score2
            if score2 > score1:
                team_data[team2]['wins'] += 1
            if score1 == 0:
                team_data[team2]['clean_sheets'] += 1
            team_data[team2]['highest_stage'] = max(team_data[team2]['highest_stage'], stage_val)
    
    # Determine rank per team for this year: rank teams by highest stage then wins.
    teams_by_stage = defaultdict(list)
    for team, data in team_data.items():
        teams_by_stage[data['highest_stage']].append((team, data['wins']))
    
    rank = 1
    for stage in sorted(teams_by_stage.keys(), reverse=True):
        teams = sorted(teams_by_stage[stage], key=lambda x: x[1], reverse=True)
        for team, _ in teams:
            team_data[team]['rank'] = rank
            rank += 1
            
    return team_data

def get_all_year_data_csv():
    """Scan the 'viz3-finaldatas' folder and extract team data for every year using CSV files"""
    base_dir = 'viz3-finaldatas'
    all_data = {}
    for filename in os.listdir(base_dir):
        if filename.lower().endswith('.csv'):
            m = re.match(r'(\d{4})--.+\.csv', filename, re.IGNORECASE)
            if m:
                year = int(m.group(1))
                csv_file = os.path.join(base_dir, filename)
                team_data = extract_team_data_csv(csv_file, year)
                all_data[year] = team_data
    return all_data

def get_host_countries():
    """Extract host countries and years from CSV filenames"""
    host_countries = {}
    base_dir = 'viz3-finaldatas'
    pattern = r'(\d{4})--(.+)\.csv'
    
    for filename in os.listdir(base_dir):
        if filename.lower().endswith('.csv'):
            match = re.match(pattern, filename, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                host = match.group(2).replace('-', ' ').title()
                host_countries[host] = year
    
    return host_countries

def produce_viz_data():
    """
    Prepares data in a format for viz3.html with all host countries.
    """
    host_countries = get_host_countries()
    all_year_data = get_all_year_data_csv()
    viz_data = {}
    
    for country, hostYear in host_countries.items():
        viz_data[country] = {"hostYear": hostYear, "metrics": []}
        for year in sorted(all_year_data.keys()):
            metrics = all_year_data[year].get(country)
            if metrics:
                wins = metrics['wins']
                matches = metrics['matches']
                winPercentage = round((wins / matches * 100) if matches > 0 else 0)
                viz_data[country]["metrics"].append({
                    "year": year,
                    "stageReached": metrics['highest_stage'],
                    "goalsScored": metrics['goals_scored'],
                    "ranking": metrics['rank'],
                    "winPercentage": winPercentage,
                    "cleanSheets": metrics['clean_sheets']
                })
    
    return viz_data

if __name__ == '__main__':
    viz_data = produce_viz_data()
    # Option: output the data as JSON (which viz3.html can load in a separate step)
    print(json.dumps(viz_data, indent=4))