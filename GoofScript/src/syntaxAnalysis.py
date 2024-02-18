from GoofScript.src import constants


def SyntaxAnalysis(tokens):
  next_token = []

  for token in tokens:
    if len(next_token) == 0:
      if token[0] in constants.ALL_TOKENS:
        next_token = constants.NEXT_TOKEN[token[0]]
        continue
      else:
        print(f'Syntax Analysis: Error "{token[1]}"')
        return [False]

    if token[0] == constants.ENDLINE:
      next_token = []
      continue

    if token[0] in next_token:
      next_token = constants.NEXT_TOKEN[token[0]]
    else:
      print(f'Syntax Analysis: Error "{token[1]}"')
      return [False]
  return [True, tokens]
