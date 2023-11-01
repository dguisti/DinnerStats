import dropbox
from random import choice
import datetime
from dateutil import parser

dbx = dropbox.Dropbox("TOKEN")

date_format = "%"

try:
    metadata, res = dbx.files_download(path="/MainData.txt")
    text = str(res.content)[2:-1]
    recipes = [y.split(" at ")[0].lower().split(" - ") for y in text.split("\\n")]

    #for recipe, date in recipes:
    #    print(f"We ate {recipe} on {date}")
        
except:
    print("Error retrieving recipe. Please notify Dallin.")
    quit()
    #print("Error...cannot retrieve from database")
    #recipes = [["Recipe1", "Date1"],["Recipe2", "Date2"],["Recipe1", "Date2"],["Recipe2", "Date1"]]


freq_weight = 1
rec_weight = 1

dinners = {}
dinner_list = []
scores = []

for myrecipe, date_string in recipes:
    recipe = myrecipe.split(", ")[0]
    if recipe not in dinners:
        # Calculate last time we ate each dinner, and how many times we have eaten it in the past year. Then append both to the list of stuff for that recipe.
        latrecipes = recipes.copy()
        latrecipes.reverse()
        for latrecipe, date_string in latrecipes:
            if recipe == latrecipe:
                last_date_string = date_string
                last_date = parser.parse(last_date_string).date() # Convert to date object here
                break

        current_date = datetime.date.today()

        date_before_now = current_date - last_date # Replace "-" with date operation syntax
        date_before_now = date_before_now.days

        if (date_before_now < 7): continue
        elif (7 < date_before_now < 14): score_before_now = 10
        elif (14 < date_before_now < 21): score_before_now = 20
        else: score_before_now = 30

        date = parser.parse(date_string).date() # Convert to date object here
        dinners[recipe] = [] # Append empty list to later add parameters for the dinner
        dinner_list.append(recipe)
        
        
        
        reccount = 0
        for check_recipe, date_string in latrecipes:
            if ((current_date - parser.parse(date_string).date()).days < 365):
                if recipe == check_recipe: reccount += 1
            else:
                break
            
        
        score = score_before_now*rec_weight + reccount*freq_weight     
        
        scores.append(score)  
        
        dinners[recipe] = [recipe, last_date, reccount, score]

def randmax(mylist):
    maxes = [0]
    for index, item in enumerate(mylist[1:]):
        if item == mylist[maxes[0]]:
            maxes.append(index+1)
        elif item > mylist[maxes[0]]:
            maxes = [index+1]
    return choice(maxes)

# Choose Dinner
#print(scores)
dinner_options = []
for mydinner in dinners:
    dinner_options += [mydinner]*dinners[mydinner][3]
#print(dinner_options)
#best_index = randmax(scores)
dinner_name = choice(dinner_options)#dinner_list[best_index]
print(f"You should eat {dinner_name}!", end="")
