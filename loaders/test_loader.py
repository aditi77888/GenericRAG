from loader_factory import LoaderFactory

loader = LoaderFactory.create("sample.jpg")

loaded = loader.load("img.png")

print(type(loaded))

print(loaded)