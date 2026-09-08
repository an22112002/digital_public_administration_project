from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image


config = Cfg.load_config_from_name("vgg_transformer")

config["device"] = "cpu"

detector = Predictor(
    config
)

image = Image.open(
    r"C:\Users\ADMIN\Pictures\phone\test.png"
)

text = detector.predict(
    image
)

print(text)