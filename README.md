# Supernoughts Bot

Named for a better way to play noughts and crosses, but not actually 
providing that facility, Supernoughts is a Discord bot for 
game-mastering text-based games.
These are exactly the games you would play with your friends,
all gathered round with pen and paper.
Except we can't do that right now.

## Using the Bot Yourself

Make sure you have a working Python 3 version.
Clone this repo and set up a virtual environment in that directory.

Then run

```shell script
pip install -r requirements.txt
```

This should install all the dependencies to a local environment,
so as not to disturb your global Python system.

You will need to register a bot on Discord to add it to your server.
Instructions for that can be found elsewhere. But you will,
during that process, attain a Bot Token. Save that token in your clone
of this directory in a file called `.env`
Do that by writing out:

```shell script
DISCORD_BOT_TOKEN=<your-bot-token-not-these-words>
```

inside that file.

**Never** commit this file to version control. That token must be a complete
secret, or some nefarious other can use it to cause mayhem on your server.

You will also need a file called `words_dictionary.json` in this directory. It should hold a single object with lowercase valid words mapped to whatever you like.

To then run the actual bot:

```shell script
python3 bot.py
```

While this is running, your bot is listening to your server.

Instructions for individual games can be found below.


## Boggle
This is based on the game of the same name.
The bot displays the board for 3 minutes: and it can then be redisplayed 
at the user's discretion to see how wild your opponent's moves were.

The idea is that the bot to calculate scores up-to the philosophy of the players.
I.e. you may choose to permit dialect words. The bot will do two things, then:
    
* Exclude words submitted by other players.
* Exclude words that cannot be made on the Boggle board.

Unfortunately, the bot does not at the moment listen to dissent.
So if you score differently, you will have to track that yourself.

### Playing

Once a game has started, and a board is in play (instructions for that below), any message sent by a user is interpreted as a whitespace-separated list of their answers. First messages only are counted. There is some time after the board vanishes to submit your answers too.

I recommend typing your answers, space-separated, in the chatbox while the board is up, and pressing enter as soon as the board disappears.

*Can you copy down other people's answers when they send them?* Yes, but that makes you a bad person. There are many ways to cheat at this game. It isn't my problem.

Importantly: even when the board is up, all messages count as answers.

### Commands

To get the game set up and to manage it while it is running, use the following commands.

The general syntax is: `$boggle <command>`, where some commands are only executable by the current game master.

`$boggle start` -- the game is started and the user who sends this message is the gamemaster.

`$boggle join` -- a user who sends this message is now in the game (requires `start` to have been called).

`$boggle flip off question master` -- the current game master is removed from the game, and the user who executed this command is now the game master. The game master cannot use this command.

`$boggle end` -- ends the current game. (It does not turn off the bot, you have to do that manually.)

#### Gamemaster-Only commands

`$boggle roll` -- a board is displayed to the screen: the game proper has begun.

`$boggle abort` -- the current game is cancelled. Useful if someone accidentally sends a humourous message just as the board appears, and you don't want to wait 3 minutes for it to be over. Usable between the board being rolled and the results being shown.

`$boggle show` -- redisplays the last board after the time runs out. Useful if you don't believe my word-searcher, or if you want to see how on earth Brenda managed to find a 15-letter word.

`$boggle scores` -- shows the current scores as calculated by the bot. However, if you don't like this dictionary or you don't believe Chris knows the meaning of "tryst", you might want to score yourself -- the bot takes most of the work out of it. It also shows which players are currently in the game, in case you lose track.

`$boggle kick <username>` -- kicks the player with that username. This uses the display name, so type in whatever you see on Discord.

