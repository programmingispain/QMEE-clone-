from otree.api import *
import itertools  # for randomizing participants into balanced groups
import random

author = 'Adam Hardaker, Universitaet Kassel EBGo' \
         'Rachel Hayward, Universitaet Kassel EBGo'

doc = """
oTree App for the Centipede Game as in McKelvey and Palfrey (1992), An Experimental Study of the Centipede Game, 
Econometrica, 60(4): 803-836.
"""


class C(BaseConstants):
    NAME_IN_URL = 'centipede_game'
    PLAYERS_PER_GROUP = 2

    NUM_NODES = 6  # number of decision points ("nodes" or turns) per round. Essentially, how long the centipede is.
    # NOTE: each player thus takes (NUM_NODES/2) turns rach round
    NUM_ROUNDS = 4  # starting with 1 for now to be simple

    # create payoffs for turn 1 in all games, as well as multiplier
    LARGE_PILE = 4
    SMALL_PILE = 1
    MULTIPLIER = 2

    # create list for subsequent payoffs
    LARGE_PILES = []
    SMALL_PILES = []

    # create subsequent payoffs
    for node in range(NUM_NODES + 1):
        LARGE_PILES.append(LARGE_PILE * MULTIPLIER ** node)
        SMALL_PILES.append(SMALL_PILE * MULTIPLIER ** node)


class Subsession(BaseSubsession):
    pass

# creating our session, at round 1 we assign people to groups randomly, and we then assign
# these groups to one of we iterate through the treatments via itertools to ensure balance
# as groups go through all other rounds, groups and treatments are held constant while
# the first-mover of each group is randomized
def creating_session(subsession):
    treatment = itertools.cycle(
        ['control', 'higher_fixed', 'higher_random'])  # make a repeating list of teatments for assignment
    if subsession.round_number == 1:  # if first round
        print(f"subsession round number is {subsession.round_number}")
        subsession.group_randomly()  # assign people to groups randomly
        for group in subsession.get_groups():  # within all groups
            group.treatment = next(treatment)  # assign a treatment in order of the iteration (ensures balance)
            print(f"Group {group.id_in_subsession}: {group.treatment}")
    else:  # if not first round, randomize player roles within their groups
        subsession.group_like_round(1)
        for group in subsession.get_groups():
            previous_group = group.in_round(1)
            group.treatment = previous_group.treatment
            print(f"treatment retained")
            print(f"subsession round number is {subsession.round_number}")
            group.reshuffle_group()  # reshuffles positions within the group, defined below


class Group(BaseGroup):
    treatment = models.StringField()
    node = models.IntegerField(initial=1)
    round_active = models.BooleanField(initial=True) # used to know when to stop the round
    round_outcome = models.IntegerField(initial=0) # used to say who, if anyone, took on Results page
    last_node = models.IntegerField(initial=1) # used to determine how far players got

    # stop round if takes or pass at last node, otherwise round remains active
    @staticmethod
    def stop_round(group: 'Group'):
        players = group.get_players()
        takes = [p.take for p in players if p.take is not None]

        if len(takes) > 0 and takes[0]:
            print(f"Player 1 stops round {group.round_number}")
            group.round_active = False
            group.round_outcome = 1
            group.last_node = group.node
        elif len(takes) > 1 and takes[1]:
            print(f"Player 2 stops round {group.round_number}")
            group.round_active = False
            group.round_outcome = 2
            group.last_node = group.node
        elif group.node == C.NUM_NODES and not any(takes):
            print(f"No one took in {group.round_number}. Round ended")
            group.round_active = False
            group.last_node = group.node

    @staticmethod
    def set_payoffs(group: 'Group'):
        players = group.get_players()  # gets list of players in the group
        takes = [p.take for p in players]  # checks if either player selected take
        for p in players:
            if group.node == C.NUM_NODES and not any(takes):  # if no takes
                if p.id_in_group == 1:
                    p.payoff = C.LARGE_PILES[-1]  # player 1 gets the large pile
                else:
                    p.payoff = C.SMALL_PILES[-1]
            elif group.node < C.NUM_NODES and any(takes):  # if someone takes
                if p.take:
                    p.payoff = C.LARGE_PILES[group.last_node - 1]  # player who took gets large pile
                else:
                    p.payoff = C.SMALL_PILES[group.last_node - 1]  # other player gets small pile
            p.cumulative_payoff = sum(p.payoff for p in p.in_all_rounds())

    @staticmethod
    def advance_node(group: 'Group'):
        group.node += 1  # advance to next node
        players = group.get_players()
        print(
            f"Group {group.id_in_subsession} advanced to node {group.node}/{C.NUM_NODES} in round {group.round_number}")
        print(f"Payoffs increased to: {C.LARGE_PILES[group.node - 1]} & {C.SMALL_PILES[group.node - 1]}")

    def reshuffle_group(group: 'Group'): # used to randomize positions within a group
        players = group.get_players()
        random.shuffle(players)
        group.set_players(players)
        print(f"🔀Shuffled positions for group {group.id_in_subsession}")


class Player(BasePlayer):
    take = models.BooleanField(
        initial=False,
        label='',
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        choices=[
            [True, 'Take'],
            [False, 'Pass'],
        ],
    )
    cumulative_payoff = models.CurrencyField()


class Welcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    def before_next_page(player: Player, timeout_happened):
        wait_for_all_groups = True

class WaitForRoundStart(WaitPage):
    title_text = "Waiting for round to start"

class Decision(Page):
    form_model = 'player'
    form_fields = ['take']

    @staticmethod
    def is_displayed(player: Player):  # display page to the appropriate player using even/odd round numbers
        return (
                (player.id_in_group == 1 and player.group.node % 2 != 0 and player.group.round_active) or
                (player.id_in_group == 2 and player.group.node % 2 == 0 and player.group.round_active)
        )

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            node=group.node,
            large_pile=C.LARGE_PILES[group.node - 1],  # -1 to match the payoff list index under constants
            small_pile=C.SMALL_PILES[group.node - 1]
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.take:  # If the player decides to take
            print(f"Player {player.id_in_group} took at node {player.group.node}")
            player.group.stop_round(player.group)
            player.group.set_payoffs(player.group)
        elif player.group.node == C.NUM_NODES:  # If the last node is reached
            player.group.stop_round(player.group)
            player.group.set_payoffs(player.group)
        else:  # If the player decides to pass
            print(f"Player {player.id_in_group} passes at node {player.group.node}")
            player.group.advance_node(player.group)


class WaitForDecision(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        pass


class Results(Page):  # shows payoffs for this round
    @staticmethod
    def is_displayed(player: Player):
        return not player.group.round_active

    @staticmethod
    def vars_for_template(player: Player):
        cumulative_payoff = sum(p.payoff for p in player.in_all_rounds())
        return dict(
            last_node=player.group.last_node,  # do i need player and group here?
            large_pile=C.LARGE_PILES[player.group.last_node - 1],
            small_pile=C.SMALL_PILES[player.group.last_node - 1],
            large_pile_pass=C.LARGE_PILES[-1],
            small_pile_pass=C.SMALL_PILES[-1],
            cumulative_payoff=cumulative_payoff
        )


class ResultsCombined(Page):
    title_text = 'Combined Results'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    # @staticmethod
    # def vars_for_template(player : Player):
    #     all_players = player.in_all_rounds()
    #     combined_payoff =
    # maybe show their payoffs and relate it to everyone else who has finished


page_sequence = [
    Welcome,
    WaitForRoundStart,
    Decision,
    WaitForDecision,
    Decision,
    WaitForDecision,
    Decision,
    WaitForDecision,
    Decision,
    WaitForDecision,
    Decision,
    WaitForDecision,
    Decision,
    WaitForDecision,
    Results,
    # WaitPage3,  # waits for everyone and advances to next round
    # ResultsCombined
]