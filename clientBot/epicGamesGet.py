from epicstore_api import EpicGamesStoreAPI, OfferData
import json

# for image viewing
from datetime import datetime

def get_all_free_games():
    api = EpicGamesStoreAPI()
    data = api.get_free_games() # why did this method return BL3 dlc? Its not even free nor a promotion

    free_games = data['data']['Catalog']['searchStore']['elements'] 
    actual_free_games = [] # dump all the free games data here, getting rid of games that are not actually free

    game_info_objects = [] # this will be returned to the discord request, it will contain the info_objects, each object being a game with information

    for item in free_games:
        if item.get("promotions") != None: # gets rid of non-promotion games, for some reason BL3 dlcs was in here?
            actual_free_games.insert(0, item) # pop REAL free games to actual_free_games array
        
    json_string = json.dumps(free_games, indent=4)

    with open('free_games_request.json', 'w') as json_file:
        json_file.write(json_string)
        
    for game in actual_free_games:
        
        info_object = {} # Store this games information here
        
        game_title = game['title']
        info_object["title"] = game_title
        
        game_id = game['id']
        info_object["id"] = game_id
        
        original_price = game['price']['totalPrice']['fmtPrice']['originalPrice']
        info_object["original_price"] = original_price
        
        # game is a promotion, meaning its free right now
        if len(game['promotions']['promotionalOffers']) > 0:
            start_date = datetime.fromisoformat(game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]["startDate"][:-1])
            end_date = datetime.fromisoformat(game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]["endDate"][:-1])
            info_object["start_date"] = str(start_date)[:10]
            info_object["end_date"] = str(end_date)[:10]
            info_object["status"] = "Free Now!"
        # if game is an upcmming promotion, then it will be free eventually
        elif len(game['promotions']['promotionalOffers']) == 0 and len(game['promotions']['upcomingPromotionalOffers']) > 0:
            start_date = datetime.fromisoformat(game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]["startDate"][:-1])
            end_date = datetime.fromisoformat(game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]["endDate"][:-1])
            info_object["start_date"] = str(start_date)[:10]
            info_object["end_date"] = str(end_date)[:10]
            info_object["status"] = "Upcoming"

        publisher = game['seller']['name']
        info_object["publisher"] = publisher
        
        game_url = f"https://store.epicgames.com/fr/p/{game['catalogNs']['mappings'][0]['pageSlug']}"
        info_object["game_url"] = game_url
        
        # save image file to game object
        image_file = ""
        for image in game['keyImages']:
            if image['type'] == "OfferImageWide":
                image_file = image['url']
        info_object["image_file_URL"] = image_file
        
        # save description to game object   
        game_desc = game["description"] 
        info_object["description"] = game_desc
        
        game_info_objects.append(info_object) # add it to the object list
        
        game_objects_string = json.dumps(game_info_objects, indent=4)

        # with open('gameObjects.json', 'w') as json_file:
        #     json_file.write(game_objects_string)
    
    # sort game objects by dates        
    game_info_objects.sort(key=lambda obj: datetime.strptime(obj['start_date'], '%Y-%m-%d'), reverse=True)
    return game_info_objects
            
get_all_free_games()