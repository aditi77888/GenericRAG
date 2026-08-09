from loaders.textLoader import  TXTLoader

loader = TXTLoader()

docs = loader.load("sample.txt")

print(docs[0].content)
print(docs[0].metadata)