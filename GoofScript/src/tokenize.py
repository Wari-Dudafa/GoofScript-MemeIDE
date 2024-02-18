from GoofScript.src import constants


def Tokenize(content):
  tokens = content.split(" ")
  tokens_array = []

  for token in tokens:
    if token == " " or token == "":
      continue

    if token in constants.ALL_TOKENS:
      tokens_array.append([token, token, True])
      continue
    else:
      tokens_array.append([constants.NOT_TOKEN, token, False])

    if token[-1] == constants.ENDLINE:
      tokens_array.pop()
      new_token = token[0:len(token) - 1]

      if new_token in constants.ALL_TOKENS:
        tokens_array.append([new_token, new_token, True])
      else:
        tokens_array.append([constants.NOT_TOKEN, new_token, False])

      tokens_array.append([constants.ENDLINE, constants.ENDLINE, True])
  return tokens_array
