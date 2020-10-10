import bs4, glob, json, os, time

SEASON_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>AEGIS League - {$EventName$}</title>
<meta charset="utf-8" />
<link rel="stylesheet" href="/AEGIS/styles.css?version=2" /></head>
	
<body><h1>AEGIS League {$EventName$} {$HeaderText$}</h1>
<p>{$BodyText$}</p>

<h2>{$EventName$} Rankings</h2>
{$EventTable$}
<p><a href="/AEGIS/index.html">Return to Main Page</a></p>
</body>
</html>
"""

def make_file_name(dir, name):
    return dir.lower() + os.path.sep + name.replace(" ",'-').lower() + '.html'

def gen_season_table(data):
    html = "<table>\n<tr>"

    # Header row
    for i in ("Rank", "Player", "Wins", "Losses", "Games Played", "Win Rate",
              "Score"):
        if i in ("Rank", "Player"): html += "<th class=l>" + i + "</th>"         
        else:   html += "<th>" + i + "</th>"
    html += "</tr>"

    # Number crunching
    players = []

    keys = list(data)
    keys.remove(" _$METADATA$_ ")
    
    for player in keys:
        wins = data[player]['wins']
        losses = data[player]['losses']
        games = wins + losses

        rate = wins / games
        
        score = round(rate * wins, 2)
        rate = round(rate*100)    # make percentage
        
        players.append([score, player, str(wins), str(losses), str(games),
                        str(rate)+'%','{:.2f}'.format(score)])

    players.sort(reverse=True)

    # Generate table rows
    rank = 1

    for pd in players:
        column = 0
        html += "\n<tr>"
        
        for entry in pd:
            if column == 0: html += "<td class=l>" + str(rank) + "</td>"
            elif column == 1: # A name
                if rank == 1:   clas = 'n1'
                elif rank == 2:   clas = 'n2'
                elif rank == 3:   clas = 'n3'
                else:   clas = 'n'

                s = "<td><a class={$cl$} href={$lnk$}>" + entry + "</a></td>"

                s = s.replace("{$cl$}", clas).replace("{$lnk$}",
                                                      "/AEGIS/index.html")

                html += s

            elif column == 2:   html += "<td class=w>" + entry + "</td>"
            elif column == 3:   html += "<td class=z>" + entry + "</td>"
            elif column in [4]:   html += "<td class=r>" + entry + "</td>"
                
            else:   html += "<td>" + entry + "</td>"

            column += 1
            
        html += "</tr>"

        rank += 1

    html += "</table>"

    return html


VERBOSE = 0

PLAYERS = {}
SEASONS = {}
TOURNEYS = {}

# Get all the data from league seasons
for season in glob.glob("seasons" + os.path.sep + "*.txt"):
    sname = season.replace("seasons" + os.path.sep, "").replace(".txt","")
    print("Loading", sname)
    
    with open(season) as f:
        data = f.read()
        data, meta = data.split("\n\n")

    table = {}

    # Parse metadata
    md = meta.split("\n")
    meta = {}

    meta["header"] = md[0]
    meta["body"] = md[1]
    table[" _$METADATA$_ "] = meta

    for line in data.split("\n"):
        if VERBOSE: print(line)

        # Transform into a dict
        row = {}
        form = ["player", 'wins', 'losses']
        
        for entry in line.split('\t'):
            if form[0] in ('wins', 'losses'):
                try:    row[form.pop(0).lower()] = int(entry)
                except: row[form.pop(0).lower()] = float(entry)
            else:
                name = entry
                form.pop(0)

        table[name] = row
        if VERBOSE: print(row)


        # Update the player's listing
        listing = {
            'wins': row['wins'],
            'losses': row['losses'],
            }
        
        if name in PLAYERS:
            PLAYERS[name][sname] = listing
                               
        else:
            PLAYERS[name] = {sname: listing}

    SEASONS[sname] = table
    
    if VERBOSE: print(table)

if VERBOSE:
    print(PLAYERS)
    print()
    print(SEASONS)

# Create player pages
for player in PLAYERS:
    pd = PLAYERS[player]

for event in SEASONS:
    ed = SEASONS[event]
    meta = ed[" _$METADATA$_ "]

    html = SEASON_TEMPLATE.replace("{$EventName$}", event).replace(
        "{$EventTable$}", gen_season_table(ed)).replace(
            "{$HeaderText$}", meta['header']).replace(
                "{$BodyText$}", meta['body'])

    fn = make_file_name("events", event)
    with open(fn, 'w') as f:
        print("Writing", fn)
        f.write(html)

input("\nDone")
