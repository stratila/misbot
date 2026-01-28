PLAYER_JOIN_MESSAGE = "**Player join**\n Player \*{player}\* joined.\n Player secret message: ||{join_message}||"


result = PLAYER_JOIN_MESSAGE.format(player="Andy9", join_message="Андрюха играет в русскую рыбалку!")

print(result)