import random

from enum import Enum, auto

import attr

STD_DICE = 4, \
    [['Z', 'L', 'R', 'H', 'N', 'N'],
     ['E', 'V', 'L', 'R', 'D', 'Y'],
     ['B', 'O', 'A', 'J', 'O', 'B'],
     ['D', 'S', 'Y', 'I', 'T', 'T'],
     ['S', 'I', 'E', 'N', 'E', 'U'],
     ['P', 'O', 'H', 'C', 'A', 'S'],
     ['C', 'T', 'U', 'I', 'O', 'M'],
     ['QU', 'N', 'M', 'I', 'H', 'U'],
     ['T', 'H', 'R', 'V', 'W', 'E'],
     ['G', 'A', 'E', 'A', 'N', 'E'],
     ['W', 'E', 'G', 'H', 'N', 'E'],
     ['K', 'A', 'F', 'P', 'F', 'S'],
     ['E', 'D', 'L', 'X', 'I', 'R'],
     ['T', 'L', 'R', 'Y', 'E', 'T'],
     ['T', 'S', 'E', 'I', 'S', 'O'],
     ['O', 'A', 'T', 'T', 'O', 'W']]


class Boggle():

    def __init__(self, game_master, english_words, dice='std'):
        self.dim, self.dice = STD_DICE
        self.board = None
        self.gm = game_master
        self.answers = {game_master: Player(user_id=game_master)}
        self.round_num = 0
        self.english_words = {word.upper() for word in english_words}

    def confirm(self):
        """Finalises a round, adding round scores to total scores.
        -- Currently unused by the bot"""
        if all(player.isDone() for player in self.answers.values()):
            summaries = self.round_summary()
            for result in summaries:
                self.answers[result.id].score += result.calculate_points()

    def roll(self):
        """Rolls the dice to form a new board, denotes the start of a new game"""
        self.round_num += 1

        self.confirm()

        for key in self.answers.keys():
            self.answers[key].round_words = None

        shuffled_dice = random.sample(self.dice, k=len(self.dice))

        self.board = list(
            map(lambda faces: random.choice(faces), shuffled_dice))

    def new_player(self, user_id):
        """Adds a new player to the game.
        Returns whether they were actually new"""
        if user_id in self.answers.keys():
            return False

        self.answers[user_id] = Player(user_id=user_id)

        return True

    def input_words(self, user_id, word_set):
        """Given a user's id and their words (case not assumed),
        we hold on to that set (all capitalized) until all users have submitted.
        """

        if user_id not in self.answers.keys():
            return

        if self.answers[user_id].round_words is None:
            self.answers[user_id].round_words = {
                word.upper() for word in word_set}

        if None not in (player.round_words for player in self.answers.values()):
            return self.round_summary()

    def is_playing(self, user_id):
        """Returns whether the given user_id is playing"""
        return user_id in self.answers.keys()

    def kick_player(self, user_id):
        """Removes a player from the game."""
        self.answers.pop(user_id, None)

    def scores(self):
        """Returns a dict of player ids => their total scores"""
        return {player.user_id: player.score for player in self.answers.values()}

    def allow(self, words):
        """Add a new word to the internal dictionary.
        Won't persist after instance is killed."""
        self.english_words |= {word.upper() for word in words}

    def round_summary(self):
        """Returns a list of PlayerResult objects, documenting how their various
        word submissions relates to each others in line with the game's rules."""
        summary = []
        for player_id, player in filter(lambda p: p[1].round_words is not None, self.answers.items()):
            unique_words = player.round_words.difference(set().union(*[other_answers.round_words
                                                                       for other_player_id, other_answers
                                                                       in self.answers.items()
                                                                       if other_player_id != player_id
                                                                       and other_answers is not None]))
            others_words = player.round_words - unique_words

            words_on_board = {word for word in player.round_words
                              if self.find_possible_board_path(word) is not None}

            words_not_on_board = player.round_words - words_on_board

            words_in_dictionary = player.round_words & self.english_words

            words_not_in_dictionary = player.round_words - \
                words_in_dictionary - others_words - words_not_on_board

            summary.append(PlayerResult(id=player_id,
                                        get_points_words=unique_words & words_on_board & words_in_dictionary,
                                        others_got_words=others_words,
                                        not_on_board_words=words_not_on_board,
                                        not_english_words=words_not_in_dictionary))

        return summary

    def string_of_board(self):
        """Returns a likely ugly textual representation of the board.
        For debugging."""

        if self.board is None:
            return "None"

        def padded(face):
            if len(face) == 1:
                return face + "    "
            elif len(face) == 2:
                return face + "   "
            else:
                return "     "

        rows = ("".join(padded(face) for face in self.board[i:i + 4])
                for i in [0, 4, 8, 12])
        return "\n" + ("\n").join(rows)

    def board_list(self):
        """Returns the board, ensuring that the return type is List"""
        if self.board is None:
            return []
        return self.board

    def greeting(self):
        """A greeting to display once the game begins"""
        return f'''Welcome to Boggle!
I will show you the board when you are ready (it will be {self.dim}x{self.dim}). 
To join issue the command

$boggle join
'''

    def find_possible_board_path(self, word):
        """Returns a path on the board to make the given word.
        Returns None if no such path exists."""

        class Direction(Enum):
            U = auto()
            L = auto()
            D = auto()
            R = auto()

        def adjacent_poses(pos):
            straights = set([])
            if pos % self.dim != (self.dim - 1):
                straights.add(Direction.R)
            if pos % self.dim != 0:
                straights.add(Direction.L)
            if pos < self.dim*self.dim - self.dim:
                straights.add(Direction.D)
            if pos >= self.dim:
                straights.add(Direction.U)

            adjacencies = set([])

            if Direction.R in straights:
                adjacencies.add(pos + 1)
            if Direction.L in straights:
                adjacencies.add(pos - 1)
            if Direction.U in straights:
                adjacencies.add(pos - self.dim)
            if Direction.D in straights:
                adjacencies.add(pos + self.dim)
            if Direction.L in straights and Direction.U in straights:
                adjacencies.add(pos - self.dim - 1)
            if Direction.R in straights and Direction.U in straights:
                adjacencies.add(pos + 1 - self.dim)
            if Direction.L in straights and Direction.D in straights:
                adjacencies.add(pos + self.dim - 1)
            if Direction.R in straights and Direction.D in straights:
                adjacencies.add(pos + self.dim + 1)

            return adjacencies

        # queue is tracking the word so far, the positions visited, and the position a search is currently at
        queue = [("", set([]), pos) for pos in range(self.dim * self.dim)]

        while len(queue) != 0:
            word_so_far, visited, at_pos = queue.pop()

            word_including_at = word_so_far + self.board[at_pos]

            if not word.startswith(word_including_at):
                continue

            visited_including_at = visited.union([at_pos])

            if word == word_including_at:
                return visited_including_at

            queue.extend((word_including_at, visited_including_at, n)
                         for n in adjacent_poses(at_pos) - visited_including_at)

        return None


@attr.s
class PlayerResult(object):
    id = attr.ib(factory=int)
    get_points_words = attr.ib(default=set())
    others_got_words = attr.ib(default=set())
    not_on_board_words = attr.ib(default=set())
    not_english_words = attr.ib(default=set())

    def calculate_points(self):
        def points_of_length(l):
            if l < 3:
                return 0
            if l in (3, 4):
                return 1
            if l == 5:
                return 2
            if l == 6:
                return 3
            if l == 7:
                return 5
            return 11

        return sum(points_of_length(len(word)) for word in self.get_points_words)


@attr.s
class Player(object):
    user_id = attr.ib(factory=int)
    round_words = attr.ib(default=None)
    score = attr.ib(default=0)

    def isDone(self):
        return self.round_words is not None
