import pickle
import folium
import pandas as pd

FLATSERROR = 0
MISSINGCORD = 0

pickle_in = open("flats.pickle", "rb")
flat_list = pickle.load(pickle_in)

#function for autotest
def addition(x,y):
    return x + y

def colorpicker(flat):

    if df.loc[flat[0]]["Price"] > mean_dist.loc[df.loc[flat[0]]["District"]]["Price"]*1.2:
        return "red"
    if df.loc[flat[0]]["Price"] < mean_dist.loc[df.loc[flat[0]]["District"]]["Price"]*0.8:
        return 'green'
    else:
        return 'gray'

for flat in flat_list:
    flat[2] = flat[2].replace(' ', '')
    flat[2] = flat[2].replace('\n', '')
    flat[2] = flat[2].replace('€', '')
    flat[2] = flat[2].replace('.', '')
    flat[2] = flat[2].replace(',', '.')
    flat[2] = float(flat[2])

    flat[3] = flat[3].replace(' ', '')
    flat[3] = flat[3].replace('€', '')
    flat[3] = flat[3].replace('+', '')
    flat[3] = flat[3].replace('\n', '')
    flat[3] = flat[3].replace('.', '')
    flat[3] = flat[3].replace(',', '.')
    try:
        flat[3] = float(flat[3])
    except Exception as e:
        print("general exception", e)

for flat in flat_list:
    if "immobilienscout24" in flat[0]:
        stringtoseparate = flat[-3]
        stringtoseparate = stringtoseparate.split(", ")
        print(stringtoseparate)
        del flat[-3]
        flat.append(stringtoseparate[0])
        if len(stringtoseparate) < 2:
             flat.append(stringtoseparate[0].split(" ")[1])
             continue
        flat.append(stringtoseparate[1]) 
    if "wg-gesucht.de" in flat[0]:
        stringtoseparate = flat[-3]
        stringtoseparate = stringtoseparate.split(" ")
        print(stringtoseparate)
        del flat[-3]
        flat.append(stringtoseparate[0] + " " + stringtoseparate[1])
        if len(stringtoseparate) > 2:
            flat.append(stringtoseparate[-2] + " " + stringtoseparate[-1])
            continue
        flat.append(stringtoseparate[2]) 

df = pd.DataFrame(flat_list, columns =['Link', 'Name', 'Price', 'Additional costs', 'Rooms', 'Size', 'Street and Number', 'lat', 'long', 'City', 'District'])

mean_dist = df.groupby('District') \
.agg({'District':'size', 'Price':'mean'}) \
.rename(columns={'District':'District count','sent':'mean Price'})\
.reset_index()

decimals = 2    
mean_dist['Price'] = mean_dist['Price'].apply(lambda x: round(x, decimals))

df.set_index("Link", inplace=True)
mean_dist.set_index("District", inplace=True)

map = folium.Map(location=[53.57532,10.01534], zoom_start = 12)

for flat in flat_list:

    try:
        popuptext = "<b>" + flat[1] + "</b></br>"\
         + str(flat[2]) + " € (avg. " + str(mean_dist.loc[df.loc[flat[0]]["District"]]["Price"]) + " €) </br>"\
          + flat[4] + " Zimmer, " + flat[5] + "</br>" + '<a href="{url}" target="_blank">'.format(url = flat[0]) + flat[0] + "</a>"
    except Exception as e:
        popuptext = "<b>" + flat[1] + "</b></br>"\
         + str(flat[2]) + " €</br>"\
          + flat[4] + " Zimmer, " + flat[5] + "</br>" + '<a href="{url}" target="_blank">'.format(url = flat[0]) + flat[0] + "</a>"
        print("general exception while creating a popup: ", e)

    try:

        if len(str(flat[-2])) < 1:
            print("coordinates missing. skipping the marker.")
            MISSINGCORD += 1
            continue
        folium.Marker([flat[-4], flat[-3]], popup=popuptext, icon=folium.Icon(color=colorpicker(flat))).add_to(map)

    except Exception as e:
        FLATSERROR += 1
        print("general exception while placing a marker:", e)

print("Failed to place " + str(FLATSERROR) + " from " + str(len(flat_list)) + " flats on the map")
print("Flats with missing cords: " + str(MISSINGCORD))
map.save("map1.html")
