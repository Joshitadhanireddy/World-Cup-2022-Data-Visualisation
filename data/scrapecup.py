import re
from datetime import datetime

def parse_match_data(input_text):
    matches = []
    lines = input_text.split('\n')
    
    current_date = None
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Match pattern for game lines
        match_info = re.search(r'\([\d]+\)\s+([\w]+)\s+([\w]+\/[\d]+)\s+([\d:]+)\s+([\w\s]+?)\s+(\d-\d)\s+\([\d]-[\d]\)\s+([\w\s]+?)(?=\s+@|$)', line)
        
        if match_info:
            weekday = match_info.group(1)
            date = match_info.group(2)
            time = match_info.group(3)
            team1 = match_info.group(4).strip()
            score = match_info.group(5)
            team2 = match_info.group(6).strip()
            
            # Create datetime object
            date_str = f"2022 {date} {time}"
            match_date = datetime.strptime(date_str, '%Y %b/%d %H:%M')
            formatted_date = match_date.strftime('%Y-%m-%d')
            
            matches.append([
                formatted_date,
                time,
                team1,
                team2,
                score,
                "Group Stage"
            ])
    
    return matches

def save_to_csv(matches, output_filename):
    # Create CSV header and content
    csv_content = "Date,Time,Team1,Team2,Score,Type\n"
    for match in matches:
        csv_content += ",".join(f'"{item}"' for item in match) + "\n"
        
    # Write to file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(csv_content)

def main():
    # Read input file
    try:
        with open('cup.txt', 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        # Parse matches
        matches = parse_match_data(input_text)
        
        # Save to CSV
        save_to_csv(matches, 'world_cup_matches.csv')
        print(f"Successfully created world_cup_matches.csv with {len(matches)} matches")
        
    except FileNotFoundError:
        print("Error: Could not find input file 'paste.txt'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()