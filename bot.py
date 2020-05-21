import discord
import re
import dotenv
import asyncio
import json

from boggle import Boggle


def fetch_english_words(fname):
    with open(fname, 'r') as file:
        raw_data = file.read()

    return set(json.loads(raw_data))


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.boggle_game = None
        self.boggle_submission = False
        self.taskboard = None
        self.boggle_time = 150
        self.english_words = fetch_english_words("words_dictionary.json")
        self.delete_queue = []

    def string_of_boggle(self):

        def emojid_padded(face):
            place = face[0].lower()
            return f" :regional_indicator_{place}: "

        rows = ("".join(emojid_padded(face) for face in self.boggle_game.board_list()[i:i + 4])
                for i in [0, 4, 8, 12])
        return ". \n" + "\n".join(rows)

    async def cancel_board(self):
        """Cancels the current board, and deletes all messages associated with it.
        For instance, the board itself is deleted."""
        self.taskboard.cancel()
        self.taskboard = None
        self.boggle_submission = False
        for msg in self.delete_queue:
            await msg.delete()
        self.delete_queue = []

    async def run_board(self, message):
        self.delete_queue.append(await message.channel.send(self.string_of_boggle(), delete_after=self.boggle_time))
        self.boggle_submission = True
        await asyncio.sleep(self.boggle_time)
        self.delete_queue.append(await message.channel.send("Submit your answers now (you have 2 minutes)",
                                                            delete_after=120))
        await asyncio.sleep(120)
        self.boggle_submission = False
        return

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        content = message.content.lower()

        if content.startswith("$boggle"):
            args = re.split(r"\s+", content.strip())[1:]
            user_name = message.guild.get_member(
                message.author.id).display_name
            if args == ['start']:
                if self.boggle_game is None:
                    self.boggle_game = Boggle(
                        message.author.id, self.english_words)
                    await message.channel.send(self.boggle_game.greeting())
                else:
                    await message.channel.send("There's already a running game.\
                     End that game before starting a new one.")
                return

            if args == ['join']:
                if self.boggle_game.new_player(message.author.id):
                    await message.channel.send(f"Welcome to the game {user_name}")
                    return
                await message.channel.send(f"{user_name}, you're already in the game.")
            if self.boggle_game is None:
                await message.channel.send("Soz bud. There ain't a game.")
                return

            if args == ['flip', 'off', 'question', 'master']:
                if self.boggle_game.gm == message.author.id:
                    await message.channel.send("Don't be rude to yourself.")
                    return

                self.boggle_game.kick_player(self.boggle_game.gm)
                self.boggle_game.gm = message.author.id
                await message.channel.send(f"{message.guild.get_member(self.boggle_game.gm).display_name} is now the game master.")
                return

            if args == ['end']:
                self.boggle_game = None
                await message.channel.send("I have ended the game, hotshots.")
                return

            if message.author.id != self.boggle_game.gm:
                await message.channel.send(
                    "\n".join(["Either your command is wrong, or you aren't the game master.",
                               "If the game master has run off, use '$boggle flip off question master' to take control"]))
                return

            if args == ['roll']:

                if self.boggle_submission:
                    return

                self.boggle_game.roll()

                self.taskboard = asyncio.ensure_future(self.run_board(message))

                return

            if args == ['abort']:
                if self.taskboard is not None:
                    await self.cancel_board()
                    await message.channel.send("Current game is cancelled.")
                return

            if args == ['show']:
                await message.channel.send(self.string_of_boggle())
                return

            if args[0] == 'allow':
                self.boggle_game.allow(args[1:])
                return

            if args == ['confirm']:
                self.boggle_game.confirm()
                return

            if args == ['scores']:
                scores = self.boggle_game.scores()
                await message.channel.send("\n".join(f"{message.guild.get_member(user_id).display_name}: {score}" for user_id, score in scores.items()))
                return

            if args[0] == 'kick' and len(args) == 2:
                kickee_id = list(filter(
                    lambda mem: mem.display_name.lower() == args[1], message.guild.members))[0].id
                self.boggle_game.kick_player(kickee_id)
                return

            if args == ['text']:
                await message.channel.send(self.boggle_game.string_of_board())
                return

        if self.boggle_submission \
            and self.boggle_game is not None \
                and self.boggle_game.is_playing(message.author.id):

            users_words = [word for word in re.split(r"\s+", message.content.strip())
                           if word.isalpha()]
            summary = self.boggle_game.input_words(
                message.author.id, users_words)

            if summary is not None:
                def display(ws):
                    return ', '.join(sorted(ws))

                to_send = ".\nRESULTS\n=======\n\n"
                for p_r in summary:
                    user_id = p_r.id
                    user_name = message.guild.get_member(user_id).display_name

                    points = p_r.calculate_points()
                    name = f"{user_name}: scored {points}"
                    get_points = f"Got points for: {display(p_r.get_points_words)}" if p_r.get_points_words else None
                    others_got = f"Other people got: {display(p_r.others_got_words)}" if p_r.others_got_words else None
                    not_on_board = f"You can't even make: {display(p_r.not_on_board_words)}" if p_r.not_on_board_words else None
                    not_in_dict = f"Not in the dictionary: {display(p_r.not_english_words)}" if p_r.not_english_words else None
                    to_send += "\n".join(filter(None, (name, get_points,
                                                       others_got, not_on_board, not_in_dict)))
                    to_send += "\n\n\n"

                await message.channel.send(to_send)
                self.boggle_submission = False
                if self.taskboard is not None:
                    await self.cancel_board()


if __name__ == '__main__':
    client = MyClient()
    client.run(dotenv.get_key('./.env', 'DISCORD_BOT_TOKEN'))
