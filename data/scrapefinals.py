import re
from datetime import datetime

def determine_match_type(match_number):
    """Determine the match type based on match number"""
    if 49 <= match_number <= 56:
        return "Round of 16"
    elif 57 <= match_number <= 60:
        return "Quarter-finals"
    elif 61 <= match_number <= 62:
        return "Semi-finals"
    elif match_number == 63:
        return "Match for third place"
    elif match_number == 64:
        return "Final"
    return "Unknown"

def parse_match_data(input_text):
    matches = []
    lines = input_text.split('\n')
    
    for line in lines:
        if not line.strip() or line.startswith('=') or '|' in line:
            continue

        # Updated regex to match:
        # - Regular matches: "(51) Sun Jul/1 17:00 Spain 3-4 Russia @ Stadium"
        # - Extra time: "(58) Fri Dec/9 18:00 Croatia 1-1 a.e.t. Brazil @ Stadium"
        # - Penalty shootouts: "(58) Fri Dec/9 18:00 Croatia 4-2 pen. 1-1 a.e.t. Brazil @ Stadium"
        match_pattern = re.search(
            r'\((\d+)\)\s+(\w{3})\s+(\w+/\d+)\s+(\d{2}:\d{2})\s+([\w\s]+?)\s+(\d+-\d+)(?:\s+pen\.\s+(\d+-\d))?(?:\s+a\.e\.t\.)?\s+([\w\s]+?)\s+@', 
            line
        )

        if match_pattern:
            match_num, weekday, date, time, team1, score, penalties, team2 = match_pattern.groups()
            match_number = int(match_num)

            # Handle date formatting
            year = "2022" if "2022" in input_text else "2018"
            date_str = f"{year} {date} {time}"
            try:
                match_date = datetime.strptime(date_str, '%Y %b/%d %H:%M')
                formatted_date = match_date.strftime('%Y-%m-%d')
            except ValueError:
                print(f"Skipping due to date error: {line}")
                continue
            
            match_type = determine_match_type(match_number)

            # Adjust score format for penalty shootouts
            final_score = score
            if penalties:
                final_score = f"{score} ({penalties} pen.)"

            print(f"Match found: {match_num}, {formatted_date}, {time}, {team1} vs {team2}, Score: {final_score}, Type: {match_type}")
            
            matches.append([
                formatted_date,
                time,
                team1.strip(),
                team2.strip(),
                final_score,
                match_type
            ])
        else:
            print(f"Skipping line (No match found): {line}")

    return matches

def save_to_csv(matches, output_filename):
    csv_content = "Date,Time,Team1,Team2,Score,Type\n"
    for match in matches:
        csv_content += ",".join(f'"{item}"' for item in match) + "\n"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(csv_content)

def main():
    try:
        with open('cup_finals.txt', 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        matches = parse_match_data(input_text)
        
        save_to_csv(matches, 'world_cup_knockout_matches.csv')
        print(f"Successfully created world_cup_knockout_matches.csv with {len(matches)} matches")
        
    except FileNotFoundError:
        print("Error: Could not find input file 'knockout.txt'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
