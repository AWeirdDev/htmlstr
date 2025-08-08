from htmlstr import Parser

parser = Parser()
elements = parser.parse("<button>Hello!</button>")

print(elements)
