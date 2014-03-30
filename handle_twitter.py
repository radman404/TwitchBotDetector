from twython import Twython
from get_passwords import get_passwords, get_twitter_name
import twitter

expected_ratio = 0.60

passes = get_passwords()

#must be a string - ex "day9tv"
twitter_name = get_twitter_name() 

APP_KEY =            passes[0]
APP_SECRET =         passes[1]
OAUTH_TOKEN =        passes[2]
OAUTH_TOKEN_SECRET = passes[3]

tweetter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
api = twitter.Api(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET) 

num_recent_tweets = 7

#get_game_tweet:
#   tailors the name of the game (heh) to what is readable and short enough to tweet
#game is a string
def get_game_tweet(game):
    game_tweet = game.split(":")[0] #manually shorten the tweet, many of these by inspection
    if (game_tweet == "League of Legends"):
        game_tweet = "LoL"
    if (game_tweet == "Call of Duty" and len(game.split(":")) > 1):
        game_tweet = "CoD:" + game.split(":")[1] #CoD: Ghosts, CoD: Modern Warfare
    if (game_tweet == "Counter-Strike" and len(game.split(":")) > 1):
        game_tweet = "CS: " 
        for item in game.split(":")[1].split(" "): 
            if (len(item) > 0):
                game_tweet += item[0] #first initial - CS:S, CS:GO
    if (game_tweet == "StarCraft II" and len(game.split(":")) > 1):
        game_tweet = "SC2: "
        for item in game.split(":")[1].split(" "):
            if (len(item) > 0):
                game_tweet += item[0] #first initial - SC2: LotV
    return game_tweet

#send_tweet
#   if <user> is believed to be viewer botting, sends a tweet via the twitter module
#user is a string representing http://www.twitch.tv/<user>
#ratio is <user>'s chatter to viewer ratio
#game is the game they're playing (Unabbreviated: ex. Starcraft II: Heart of the Swarm)
#viewers is how many viewers the person has - can be used to get number of chatters, with ratio
def send_tweet(user, ratio, game, viewers, tweetmode, ratio_threshold, confirmed, suspicious):
    name = "http://www.twitch.tv/" + user
    if (ratio < ratio_threshold):
        found = 0
        for item in confirmed:
            if item[0] == name:
                item[1] = ratio #update the ratio and game each time
                item[2] = game
        for item in suspicious:
            if item[0] == name:
                item[1] = ratio #update the ratio and game each time
                item[2] = game
                found = 1
        if found:
            suspicious.remove([name, ratio, game])
            if (tweetmode):
                print "Tweeting!"
            else:
                print "(Not actually Tweeting this):"
            confirmed.append([name, ratio, game])
            originame = name[21:]
            chatters = int(viewers * ratio) # TODO: something more intelligent than chatters, take into account the average game ratio and calculate the expected number of viewers
            game_tweet = get_game_tweet(game)
            #TODO: change expected_ratio to be each game - is this a good idea? avg skewed by botting viewers...
            fake_viewers = int(viewers - (1 / expected_ratio) * chatters)
            estimate = "(~" + str(fake_viewers) + " extra viewers of "+ str(viewers) + " total)"
            tweet = name + " (" + game_tweet + ") might have a false-viewer bot " + estimate
            if (ratio < 0.13):
                tweet = name + " (" + game_tweet + ") appears to have a false-viewer bot " + estimate
            if (ratio < 0.09):
                tweet = name + " (" + game_tweet + ") almost definitely has a false-viewer bot " + estimate
            if (len(tweet) + 2 + len(originame) <= 140): #max characters in a tweet
                tweet = tweet + " #" + originame
            if (not tweetmode):
                print "Not",
            print("Tweet text: '" + tweet + "'")
            statuses = api.GetUserTimeline(twitter_name)[:num_recent_tweets]
            found_rec_tweet = False #did we recently tweet about this person?
            for status in statuses:
                names = status.text.split("#")
                if (len(names) == 2):
                    if (names[1] == originame):
                        found_rec_tweet = True
                        break
            if (found_rec_tweet):
                print "Not tweeting because I found recent tweet for", originame
            else:
                if (tweetmode):
                    try:
                        tweetter.update_status(status=tweet)
                    except:
                        print "couldn't tweet :("
                        pass
        if not found:
            for item in confirmed:
                if (item[0] == name):
                    return
            suspicious.append([name, ratio, game])
