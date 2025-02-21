<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIFA World Cup Match Calendar</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
        }
        .container {
            display: flex;
            align-items: flex-start;
            gap: 50px;
        }
        .calendar-container {
            text-align: center;
        }
        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 100px);
            gap: 8px;
            max-width: 800px;
            margin: 0 auto;
        }
        .legend {
            margin-top: 87px;
            font-size: 12px;
            font-weight: bold;
            background: #f1f1f1;
            padding: 10px;
            border-radius: 5px;
            width: 200px;
            text-align: left;
        }
        .legend-title {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 6px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }
        .legend-box {
            width: 15px;
            height: 15px;
            margin-right: 8px;
            border: 1px solid #333;
        }
        .note {
            font-size: 11px;
            margin-top: 6px;
            color: #666;
        }
        .day-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .day-label {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .day {
            width: 100px;
            height: 100px;
            border: 2px solid #ccc;
            background-color: #f9f9f9;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            padding: 5px;
            position: relative;
        }
        .match-bar {
            height: 12px;
            width: 90%;
            margin: 2px auto;
            border: 1px solid #444;
            position: relative;
            background-color: transparent;
            cursor: pointer;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
        }
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 5px;
            border-radius: 5px;
            font-size: 12px;
            display: none;
            pointer-events: none;
            z-index: 10;
        }
        .bar-chart-container {
            margin-top: 30px;
            width: 200px;
        }
        .bar-chart-title {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
            text-align: center;
        }
        .bar {
            height: 25px;
            margin: 5px 0;
            text-align: right;
            padding-right: 5px;
            color: white;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Calendar Section -->
        <div class="calendar-container">
            <h2>FIFA World Cup Calendar</h2>
            <h3>Nov 20 - Dec 18</h3>
            <div class="calendar" id="calendar"></div>
        </div>

        <!-- Legend Section -->
        <div class="legend">
            <div class="legend-title">Legend</div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: red;"></div>
                <span>Hot (≥ 82.7°F)</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: orange;"></div>
                <span>Moderate (75.3°F - 82.7°F)</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: blue;"></div>
                <span>Cold (≤ 75.3°F)</span>
            </div>
            <div class="note">
                ⚽ Bar fill represents % of total goals (normalized to 8 goals max).
            </div>
             <div class="bar-chart-container">
                <div class="bar-chart-title">Avg Goals per Weather</div>
                <div id="bar-chart"></div>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        const coldThreshold = 40;
        const moderateThreshold = 75.3;
        const hotThreshold = 82.7;
        const maxGoals = 8;

        function getTempColor(temp) {
            temp = +temp;
            if (temp >= hotThreshold) return "red";
            if (temp >= moderateThreshold) return "orange";
            return "blue";
        }

        function getFillWidth(goals) {
            goals = +goals;
            return Math.min((goals / maxGoals) * 100, 100) + "%";
        }

        d3.csv("data/final_wc_d3.csv").then(function(matches) {
            matches.forEach(d => d.date = new Date(d.Date));

            const calendar = d3.select("#calendar");
            const tooltip = d3.select("#tooltip");

            const matchDays = [...new Set(matches.map(d => d.date.getTime()))].sort();
            const dayMatchMap = {};
            matchDays.forEach(day => {
                dayMatchMap[day] = matches.filter(d => d.date.getTime() === day);
            });

            matchDays.forEach(day => {
                const dayMatches = dayMatchMap[day];
                const dateObj = new Date(day);

                const dayContainer = calendar.append("div").attr("class", "day-container");
                dayContainer.append("div").attr("class", "day-label").text(dateObj.getDate());
                const dayBox = dayContainer.append("div").attr("class", "day");

                dayMatches.forEach(match => {
                    const totalGoals = +match.Goals_Team1 + +match.Goals_Team2;
                    const bar = dayBox.append("div")
                        .attr("class", "match-bar")
                        .on("mouseover", function(event, d) {
                            tooltip.style("display", "block")
                                .style("left", (event.pageX + 10) + "px")
                                .style("top", (event.pageY - 20) + "px")
                                .html(`
                                    <strong>${match.Team1} vs ${match.Team2}</strong><br>
                                    ⏰ ${match.Time} | 🌡️ ${match.Temperature}°F <br>
                                    ⚽ ${match.Score} | 💨 Wind: ${match.Wind} mph
                                `);
                        })
                        .on("mouseout", function() {
                            tooltip.style("display", "none");
                        });

                    bar.append("div")
                        .attr("class", "bar-fill")
                        .style("width", getFillWidth(totalGoals))
                        .style("background-color", getTempColor(match.Temperature));
                });
            });

            d3.select("#bar-chart").selectAll(".bar")
                .data([
                    { type: "Hot", avgGoals: 2.5, color: "red" },
                    { type: "Moderate", avgGoals: 1.8, color: "orange" },
                    { type: "Cold", avgGoals: 1.3, color: "blue" }
                ])
                .enter().append("div")
                .attr("class", "bar")
                .style("background-color", d => d.color)
                .text(d => `${d.type}: ${d.avgGoals}`);
        });

    </script>

</body>
</html>
