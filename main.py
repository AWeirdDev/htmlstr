from htmlstr import Parser

parser = Parser()

with open("./index.html", "r", encoding="utf-8") as f:
    print(parser.parse(f.read()))
