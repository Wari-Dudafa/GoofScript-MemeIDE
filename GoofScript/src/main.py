from GoofScript.src import tokenize
from GoofScript.src import syntaxAnalysis
from GoofScript.src import interpret

import sys


# path = sys.argv[2]

# if sys.argv[1] == "test":
#   path = "./tests/" + path + ".goof"
# elif sys.argv[1] == "prod":
#   path = path + ".goof"


def main(path):

  with open(path, "r") as file:
    content = file.read()
    tokens = tokenize.Tokenize(content.replace("\n", " "))
    syntax_tree = syntaxAnalysis.SyntaxAnalysis(tokens)

    if syntax_tree[0]:
      interpret.Interpret(syntax_tree[1], True)


# main(path)
