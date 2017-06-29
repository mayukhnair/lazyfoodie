import urllib.parse
import urllib.request
import json

api_baseUrl = "https://developers.zomato.com/api/v2.1"
loc_name = ""
loc_place = ""
loc_code = ""
loc_type = ""
r_name = ""
r_loc = "" 
r_rating = ""
r_votes = ""
r_cuisine = ""
r_costfor2 = ""
zomato_user_key = "89eaf85930e763faf01669d60ff76dee"

def lambda_handler(event, context):
    
    # Stop any other Alexa skill apart from Glutton to access this function
    
    if (event["session"]["application"]["applicationId"] != "amzn1.ask.skill.d8dedb46-8b94-4e39-a496-8872775940b8"):
        raise ValueError("Invalid Application ID") 

    # Figure out what kind of request the user asked for 
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

# Report a new session starting this Lambda function

def on_session_started(session_started_request, session):

    print("on_session_started requestId=" 
    + session_started_request['requestId']
    + ", sessionId=" + session['sessionId'])

# If user starts Glutton without asking it a query

def on_launch(launch_request, session):
    
    return gluttonLaunchResponse()

# If user tells Glutton a specific intent 

def on_intent(intent_request, session):
    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
     
    if(intent_name == "getRating"):
        return gluttonRatingResponse(intent)
    
    elif(intent_name == "getCuisines"):
        return gluttonCuisinesResponse(intent)
         
    elif(intent_name == "getMealEst"):
        return gluttonMealEstimateResponse(intent)
         
    elif(intent_name == "AMAZON.HelpIntent"):
        return gluttonHelpResponse()
        
    elif(intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent"):
        return gluttonEndResponse()
    
# If the session ends        

def on_session_ended(session_ended_request, session):
    
    print("End of Glutton session")

# Glutton's response when the user launches it without a request

def gluttonLaunchResponse():
    
    print("Launch response invoked")
    session_attributes = {}
    card_title = "Welcome to Lazy Foodie!"
    should_end_session = False
    speech_output = "Hey! I'm Lazy Foodie. I'll help you decide if that restaurant you're thinking about is worth the visit. " \
    "Ask me for a quick rating, cuisine description " \
    "or a cost estimate for a meal at a restaurant. "
    reprompt_text = "Ask Lazy Foodie about a restaurant's rating, what cuisine it serves or how much a meal for two would cost there. For example, 'What's the rating for Hakkasan in Mayfair'" 
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# Glutton's response when the user asks for help

def gluttonHelpResponse():
    
    print("Help response invoked")
    session_attributes = {}
    card_title = "How to use Lazy Foodie"
    should_end_session = False
    speech_output = "Lazy Foodie uses restaurant data from Zomato to help you get a quick peek at a restaurant of your choice. " \
    "Just ask me the rating, cuisine or the cost for a meal for two of a restaurant, " \
    "and mention its name and location clearly. For example: 'Alexa, ask Lazy Foodie how much would a meal at Hakkasan in Mayfair cost.' "
    reprompt_text = "Ask Glutton about a restaurant's rating, what cuisine it serves or how much a meal for two would cost there. Please mention the restaurant name and location clearly."
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# Glutton's response when the user wants to exit

def gluttonEndResponse():
    
    print("End response invoked")
    session_attributes = {}
    card_title = "Lazy Foodie"
    should_end_session = True
    speech_output = "Thanks for using Lazy Foodie. Call me whenever you are hungry again. Bon appetit!" 
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# Glutton's response when the user asks it for a restaurant's rating

def gluttonRatingResponse(intent):

    global loc_name
    global loc_place
    global loc_code
    global loc_type
    global r_name
    global r_loc
    global r_rating
    global r_votes
    

    session_attributes = {}
    card_title = "Lazy Foodie: Restaurant rating"
    should_end_session = False
    speech_output = "Oops! Looks like you didn't tell me the restaurant's name and place."
    reprompt_text = "Ask Lazy Foodie the rating for a restaurant at a particular locality eg. McDonald's at Esplanade"
    
    loc_code = ""
    loc_type = ""

    if "value" in intent["slots"]["name"] and "value" in intent["slots"]["place"]:
        name = intent["slots"]["name"]["value"]
        place = intent["slots"]["place"]["value"]
        
        if(name != loc_name or place != loc_place):
            loc_name = name
            loc_place = place
            print("API called")
            zomatoLocationApiCode(place)
            if(loc_code != "gl!err-js-c"):   
                zomatoSearchApiData(name,loc_code,loc_type)
                if(r_name != "gl!err-js-r"):
                    print("Rating: "+r_name+","+r_loc)  
                    speech_output = r_name+" in "+r_loc+" has a Zomato rating of "+r_rating+" from "+r_votes+" votes."
                    reprompt_text = ""
                else:
                    print("Restaurant error - rating")
                    loc_name = ""
                    loc_place = ""
                    speech_output = "Oops! Looks like the restaurant you just mentioned is invalid. Please try again."
                    reprompt_text = "Restaurant not found. Please try again."
            else:
                print("Location error - rating")
                loc_name = ""
                loc_place = ""
                speech_output = "Oops! Looks like the location you just mentioned is invalid. Please try again."
                reprompt_text = "Location not found. Please try again."

        else:
            print("Cached response - rating: "+r_name+","+r_loc)
            speech_output = r_name+" in "+r_loc+" has a Zomato rating of "+r_rating+" from "+r_votes+" votes."
            reprompt_text = ""

    else:
        print("Request error - rating")
        speech_output = "Uh-oh, I was unable to understand your request. Please try again."
        reprompt_text = "Your request was unclear. Please try again."
           

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def gluttonCuisinesResponse(intent):

    global loc_name
    global loc_place
    global loc_code
    global loc_type
    global r_name
    global r_loc
    global r_cuisine
    session_attributes = {}
    card_title = "Lazy Foodie: Restaurant cuisine"
    should_end_session = False
    speech_output = "Oops! Looks like you didn't tell me the restaurant's name and place."
    reprompt_text = "Ask Lazy Foodie the cuisine served by a restaurant at a particular locality eg. McDonald's at Esplanade"
    
    loc_code = ""
    loc_type = ""

    if "value" in intent["slots"]["name"] and "value" in intent["slots"]["place"]:
        name = intent["slots"]["name"]["value"]
        place = intent["slots"]["place"]["value"]
        
        if(name != loc_name or place != loc_place):
            loc_name = name
            loc_place = place
            print("API called")
            zomatoLocationApiCode(place)
            if(loc_code != "gl!err-js-c"):   
                zomatoSearchApiData(name,loc_code,loc_type)
                if(r_name != "gl!err-js-r"):
                    print("Cuisine: "+r_name+","+r_loc)  
                    speech_output = r_name+" in "+r_loc+" is known for serving "+r_cuisine+"."
                    reprompt_text = ""
                else:
                    print("Restaurant error - cuisine")
                    loc_name = ""
                    loc_place = ""
                    speech_output = "Oops! Looks like the restaurant you just mentioned is invalid. Please try again."
                    reprompt_text = "Restaurant not found. Please try again."
            else:
                print("Location error - cuisine")
                loc_name = ""
                loc_place = ""
                speech_output = "Oops! Looks like the location you just mentioned is invalid. Please try again."
                reprompt_text = "Location not found. Please try again."

        else:
            print("Cached response - cuisine: "+r_name+","+r_loc)
            speech_output = r_name+" in "+r_loc+" is known for serving "+r_cuisine+"."
            reprompt_text = ""

    else:
        print("Request error - cuisine")
        speech_output = "Uh-oh, I was unable to understand your request. Please try again."
        reprompt_text = "Your request was unclear. Please try again."

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def gluttonMealEstimateResponse(intent):

    global loc_name
    global loc_place
    global loc_code
    global loc_type
    global r_name
    global r_loc
    global r_costfor2
    session_attributes = {}
    card_title = "Lazy Foodie: Restaurant cost estimate"
    should_end_session = False
    speech_output = "Oops! Looks like you didn't tell me the restaurant's name and place."
    reprompt_text = "Ask Lazy Foodie the estimated cost for a meal at a restaurant at a particular locality eg. McDonald's at Esplanade"
    
    loc_code = ""
    loc_type = ""

    if "value" in intent["slots"]["name"] and "value" in intent["slots"]["place"]:
        name = intent["slots"]["name"]["value"]
        place = intent["slots"]["place"]["value"]

        if(name != loc_name or place != loc_place):
            loc_name = name
            loc_place = place
            print("API called")
            zomatoLocationApiCode(place)
            if(loc_code != "gl!err-js-c"):   
                zomatoSearchApiData(name,loc_code,loc_type)
                if(r_name != "gl!err-js-r"):  
                    print("Cost: "+r_name+","+r_loc)
                    speech_output = r_name+" in "+r_loc+" should cost you around "+str(r_costfor2)+" for a meal for two."
                    reprompt_text = ""
                else:
                    print("Restaurant error - cost")
                    loc_name = ""
                    loc_place = ""
                    speech_output = "Oops! Looks like the restaurant you just mentioned is invalid. Please try again."
                    reprompt_text = "Restaurant not found. Please try again."
            else:
                print("Location error - cost")
                loc_name = ""
                loc_place = ""
                speech_output = "Oops! Looks like the location you just mentioned is invalid. Please try again."
                reprompt_text = "Location not found. Please try again."

        else:
            print("Cached response - cost: "+r_name+","+r_loc)
            speech_output = r_name+" in "+r_loc+" should cost you around "+str(r_costfor2)+" for a meal for two."
            reprompt_text = ""

    else:
        print("Request error - cost")
        speech_output = "Uh-oh, I was unable to understand your request. Please try again."
        reprompt_text = "Your request was unclear. Please try again."
    

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    
# Query Zomato's locations API for accuracy

def zomatoLocationApiCode(place):
    global loc_code
    global loc_type
    if(place != ""):
        loc_code = ""
        loc_type = ""
        renc = urllib.parse.urlencode({'query': place, 'count': 1})
        req = urllib.request.Request(api_baseUrl+"/locations?"+renc)
        req.add_header("Accept", "application/json")
        req.add_header("user-key", zomato_user_key)
        response = json.load(urllib.request.urlopen(req))
        if(response['location_suggestions']):  
            loc_code = str(response['location_suggestions'][0]['entity_id'])
            loc_type = response['location_suggestions'][0]['entity_type']
        else:
            loc_code = "gl!err-js-c"

# Query Zomato's search API to get rating

def zomatoSearchApiData(name,e_code,e_type):
    global r_name
    global r_loc
    global r_rating
    global r_votes
    global r_cuisine
    global r_costfor2
    if(name != "" and e_code != ""):
        renc = urllib.parse.urlencode({'q': name, 'count': 1, 'entity_id': e_code, 'entity_type': e_type})
        req = urllib.request.Request(api_baseUrl+"/search?"+renc)
        req.add_header("Accept", "application/json")
        req.add_header("user-key", zomato_user_key)
        response = json.load(urllib.request.urlopen(req))
        if(response['restaurants']):
            r_name = response['restaurants'][0]['restaurant']['name']
            r_loc = response['restaurants'][0]['restaurant']['location']['locality_verbose']
            r_rating = response['restaurants'][0]['restaurant']['user_rating']['aggregate_rating']
            r_votes = response['restaurants'][0]['restaurant']['user_rating']['votes']
            r_cuisine = response['restaurants'][0]['restaurant']['cuisines']
            r_costfor2 = response['restaurants'][0]['restaurant']['average_cost_for_two']
        else:
            r_name = "gl!err-js-r"

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }   

