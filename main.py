from htmlstr import Parser, TextTransformer

parser = Parser()

with open("./index.html", "r", encoding="utf-8") as f:
    transformer = TextTransformer(parser.parse(f.read()))
    transformer.transform()
    print(transformer.text())
