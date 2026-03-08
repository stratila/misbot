FIRST_MSG_TEXT = "First time here! Your role is {role}"

GREETING_MSG_TEXT = "Weclome to misbot again! Your role is {role}"

JOIN_MSG_TEXT = (
    "*Player {action}\\!*\n"
    "Nickname: _{player_nickname}_\n"
    "Time {timezone}: _{time}_\n"
    "Secret message: ||{message}||"
)

QUIT_MSG_TEXT = (
    "*Player {action}\\!*\n"
    "Nickname: _{player_nickname}_\n"
    "Time {timezone}: _{time}_\n"
    "Time spent on server: __{spent_time}__"
)

PLAYERS_ONLINE_TEXT = """
IP: {server_address}\n
Players online: {players_count}\n
{players_list}
"""


TIMEFORMAT = "%d/%m/%Y %H:%M:%S"
