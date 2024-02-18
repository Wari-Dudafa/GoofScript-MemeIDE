from GoofScript.src import constants
import operator
import math

variables = {}
caster = {constants.INT: int, constants.STR: str, constants.BOOL: bool}


def Interpret(syntax_tree, should_chunkize):
  if should_chunkize:
    chunks = Chunkize(syntax_tree)
  else:
    chunks = syntax_tree

  if_stack = []
  while_stack = []

  if_append = False
  while_append = False

  for chunk in chunks:

    if chunk[0][0] == constants.WHILE:
      while_append = True
      while_stack.append(chunk)
    elif chunk[0][0] == constants.ENDWHILE:
      while_stack.append(chunk)
      HandleLooping(while_stack)
      while_append = False
      while_stack = []

    if while_append:
      while_stack.append(chunk)
      continue

    if chunk[0][0] == constants.IF:
      if_append = True
      if_stack.append(chunk)
    elif chunk[0][0] == constants.ENDIF:
      if_stack.append(chunk)
      HandleBranching(if_stack)
      if_append = False
      if_stack = []

    if if_append:
      if_stack.append(chunk)
      continue

    if chunk[0][0] in constants.VARIABLE_DECLARATION:
      Variable(chunk)
    elif chunk[0][0] in constants.BUILT_IN_FUNCTIONS:
      BuiltInFunction(chunk)


def Chunkize(syntax_tree):
  current_chunk = []
  chunks = []

  for statement in syntax_tree:
    current_chunk.append(statement)

    if statement[0] == constants.ENDLINE:
      current_chunk.pop()
      chunks.append(current_chunk)
      current_chunk = []

  return chunks


def Variable(chunk):
  data_type = chunk[0][0]
  name = chunk[1][1]

  if data_type in constants.VARIABLE_DECLARATION:
    if data_type == constants.ARR:
      HandleArray(chunk)
      return

    if chunk[3][0] == constants.ARR:
      MakeVariableArrayItem(chunk)
      return

    if chunk[1][0] != constants.NOT_TOKEN:
      print(f'Interpretation: Error "Invalid variable name"')
      return
    if chunk[2][0] == constants.ASSIGNMENT:
      cast = caster[data_type]

      if data_type == constants.INT:
        variables[name] = HandleMath(chunk)
      elif data_type == constants.STR:

        string_array = chunk[3:len(chunk)]
        string = ""

        for string_chunk in string_array:
          string += string_chunk[1] + " "

        variables[name] = cast(string)
      else:  # it is a bolean
        data = (chunk[3][1].lower() == constants.TRUE.lower())
        variables[name] = data


def HandleMath(chunk):
  expr = chunk[3:len(chunk)]

  if expr[0][1] in variables:
    result = variables[expr[0][1]]
  else:
    result = int(expr[0][1])

  i = 1
  while i < len(expr):
      # Get the operator and the next number
    operator = expr[i][1]

    if expr[i + 1][1] in variables:
      number = variables[expr[i + 1][1]]
    else:
      number = int(expr[i + 1][1])

    # Perform the operation based on the operator
    if operator == constants.PLUS:
      result += number
    elif operator == constants.MINUS:
      result -= number
    elif operator == constants.MULTIPLY:
      result *= number
    elif operator == constants.DIVIDE:
      result /= number
    else:
      print(f'Interpretation: Error "Unknown operator"')
      return None
    # Add more operators here if needed

    # Move to the next operator-number pair
    i += 2
  return result


def BuiltInFunction(chunk):
  if chunk[0][0] == constants.PRINT:
    HandlePrint(chunk)


def HandlePrint(chunk):
  if len(chunk) == 2:
    if chunk[1][1] in variables:
      print(variables[chunk[1][1]])
    else:
      print(chunk[1][1])

  else:
    for i in range(1, len(chunk)):
      if chunk[i][0] == constants.NOT_TOKEN:
        if chunk[i][1] in variables:
          print(variables[chunk[i][1]], end=" ")
        else:
          print(chunk[i][1], end=" ")
      else:
        print(chunk[i][1], end=" ")


def HandleBranching(if_stack):
  if_statement = if_stack[0]
  branch = HandleIf(if_statement)

  if branch:
    to_interpret = []
    loop, i = True, 1

    while loop and i < len(if_stack):
      if if_stack[i][0][0] == constants.ENDIF or if_stack[i][0][0] == constants.ELSE:
        loop = False
      else:
        to_interpret.append(if_stack[i])

        i += 1

    Interpret([to_interpret[1]], False)
  else:
    to_interpret = []
    appending = False

    for i in range(1, len(if_stack)):
      chunk = if_stack[i]

      if appending:
        to_interpret.append(chunk)
      if chunk[0][0] == constants.ELSE:
        appending = True
      if chunk[0][0] == constants.ENDIF:
        if appending:
          to_interpret.pop()
    Interpret(to_interpret, False)


def HandleIf(chunk):

  comparers = {
      constants.LT: operator.lt,
      constants.LE: operator.le,
      constants.EQ: operator.eq,
      constants.NE: operator.ne,
      constants.GE: operator.ge,
      constants.GT: operator.gt,
  }

  comparer = chunk[2][0]

  if comparer in comparers:
    if chunk[1][1] in variables:
      left = variables[chunk[1][1]]
    else:
      left = int(chunk[1][1])

    if chunk[3][1] in variables:
      right = variables[chunk[3][1]]
    else:
      right = int(chunk[3][1])

    return comparers[comparer](left, right)
  else:
    print("Interpretation: Error 'Unknown comparer'")
    return False


def HandleLooping(while_stack):
  while_statement = while_stack[0]
  branch = HandleIf(while_statement)

  while branch:
    to_interpret = []
    loop, i = True, 1

    while loop and i < len(while_stack):
      if while_stack[i][0][0] == constants.ENDWHILE:
        loop = False
      else:
        to_interpret.append(while_stack[i])

        i += 1
    Interpret(to_interpret[1:len(to_interpret)], False)
    branch = HandleIf(while_statement)


def HandleArray(chunk):
  chunk_length = len(chunk)

  if chunk_length < 2:
    print("Interpretation: Error 'Array must have a name'")
    return
  elif chunk_length == 2:
    # Make array
    variables[chunk[1][1]] = []
    return
  elif chunk_length == 3:
    # Pop array
    if len(variables[chunk[1][1]]) > 0:
      variables[chunk[1][1]].pop()
    else:
      print("Interpretation: Error 'Array is empty'")
    return
  elif chunk_length == 4:
    # Either get or append
    HandleArrayMethod(chunk)
    return
  elif chunk_length > 4:
    print("Interpretation: Error 'Array has too many parameters'")
    return


def HandleArrayMethod(chunk):
  if chunk[2][0] == constants.ARR_GET:
    if chunk[3][1] in variables:
      index = variables[chunk[3][1]]
    else:
      index = int(chunk[3][1])

    if index < len(variables[chunk[1][1]]):
      print(variables[chunk[1][1]][index])
    else:
      print("Interpretation: Error 'Index out of range'")
  elif chunk[2][0] == constants.ARR_APPEND:
    if chunk[3][1] in variables:
      if variables[chunk[3][1]] in variables:
        variables[chunk[1][1]].append(variables[chunk[3][1]])
      else:
        variables[chunk[1][1]].append(variables[chunk[3][1]])
    else:
      if math.isnan(int(chunk[3][1])):
        variables[chunk[1][1]].append(chunk[3][1])
      else:
        variables[chunk[1][1]].append(int(chunk[3][1]))
  else:
    print("Interpretation: Error 'Unknown array method'")


def MakeVariableArrayItem(chunk):
  var_name = chunk[1][1]
  array_name = chunk[4][1]
  index = chunk[6][1]

  if array_name in variables:

    if index in variables:
      index = variables[index]

    array = variables[array_name]
    variables[var_name] = array[int(index)]
  else:
    print("Interpretation: Error 'Array not found'")
    return
