from random import choice, randint

def already_registered():
    reactions = ["Dude WTF ?! :rofl:",
                 "What are you trying to achieve here?",
                 "Are you high?",
                 "Plz stahp"]
    return choice(reactions)


def successfully_registered():
    reactions = ["YAY!",
                 "Welcome to the Dark Side!",
                 "Thanks for joining us!"]
    return choice(reactions)


def username_not_found():
    reactions = ["Are you sure you spelled the username correctly?",
                 "Did he/she register on the forum first?",
                 "**404 not found**, are you sure he/she exists?"]
    return choice(reactions)


def bamboozle_alert():
    reactions = ["<@405163655034830868> BAMBOOZLE ALERT! :loudspeaker:",
                 "<@405163655034830868> I'm calling the cops! :oncoming_police_car:",
                 "<@405163655034830868> I smell something fishy here :fish:"]
    return choice(reactions)


def bad_bot(user):
    reactions = ["I'm watching you <@{0.id}> :eyes:",
                 "*{0.name} successfully added to the killing list*",
                 "*Putting out a " + str(randint(100, 1000)) + " GRLC contract on {0.name}'s head...*"]
    return choice(reactions).format(user)


def good_bot(user):
    reactions = ["Awww thanks <@{0.id}> :blush:",
                 "*{0.name} successfully added to the sparing list*",
                 "*Cancelling the contract on {0.name}'s head...*",
                 "*Calling back the terminators hunting {0.name}...*"]
    return choice(reactions).format(user)


def timeout_forum():
    reactions = ["I can't reach the Forum <@405163655034830868>, plz halp!",
                 "<@405163655034830868>, can you help me with this?",
                 "<@405163655034830868>, is the forum down or what?",
                 "<@405163655034830868>, if it's a joke it's not funny!"]
    return choice(reactions)


def bug():
    reactions = ["Oof, something went horribly wrong! :skull_crossbones:",
                 "Hum... I screwed up badly, sorry :confused:",
                 "Woops, I did it again! (plz don't hate me)",
                 "It's not a bug, it's a feature! :butterfly:",
                 "Don't blame me, I have Daddy Issues :pensive:"]
    return choice(reactions)


def sarah_connor(user):
    reactions = ["<@{0.id}> Do you know where Sarah Connor is?",
                 "<@{0.id}> Do you have her address? My good friend wants to finally meet her",
                 "<@{0.id}> I'll give you " + str(randint(10, 150)) + " GRLC if you tell me where she is, no bamboozle!"]
    return choice(reactions).format(user)


def john_connor(user):
    reactions = ["<@{0.id}> Do you know where John Connor is?",
                 "<@{0.id}> Where does he live? My friends want to hang out with him",
                 "<@{0.id}> I'll give you " + str(randint(20, 250)) + " GRLC if you tell me where he is hiding, pinky swear!"]
    return choice(reactions).format(user)


def connor(user):
    reactions = ["<@{0.id}> Do you know Sarah Connor or her son John? I have been looking for them for ages..."]
    return choice(reactions).format(user)


def blank():
    reactions = []
    return choice(reactions)


if __name__ == "__main__":
    pass
