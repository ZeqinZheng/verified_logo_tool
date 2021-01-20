from PIL import Image, ImageChops
import json
import os

li_exceptions = []
config = {}
config_keys = ["input_folder_path", "output_folder_path"]
gmail_logo_size, verified_logo_size = None, None
pos_x, pos_y = None, None


def load_parameters():
    if "config.json" not in os.listdir():
        print("ERROR", "config.json not found")
        exit(-1)
    with open("config.json", "r") as f:
        js = json.load(f)
        for key in config_keys:
            if key not in js.keys():
                print(f"config file does not have {key}")
                exit(-1)
            config[key] = str(js[key])
    if not os.path.isdir(config["input_folder_path"]) or not os.path.isdir(config["output_folder_path"]):
        print("Invalid input folder path OR output folder path")
        exit(-1)


def get_filenames(abs_path):
    os.chdir(abs_path)
    files = os.listdir()
    return files


def calculate_logo_size(filepath):
    global gmail_logo_size, verified_logo_size
    logo = Image.open(filepath)
    verified_logo_size = logo.size
    gmail_logo_size = (1667, logo.size[1])


def calculate_position():
    global pos_x, pos_y
    width_gmail_logo = gmail_logo_size[0]
    width_verified_logo = verified_logo_size[0]

    pos_x = int(width_gmail_logo/2) - int(width_verified_logo/2)
    pos_y = 0


def merge_images(file_path):
    # new_img.paste(template, (0, 0))
    verified_logo = None
    try:
        verified_logo = Image.open(file_path)
    except Exception as e:
        li_exceptions.append(str(e))
        return None
    new_img = Image.new("RGB", gmail_logo_size, (255, 255, 255))

    new_img.paste(verified_logo, (pos_x, pos_y))

    return new_img


load_parameters()
file_li = get_filenames(config["input_folder_path"])
calculate_logo_size(config["input_folder_path"] + "/" + file_li[0])
calculate_position()

for index, filename in enumerate(file_li):
    filepath = config["input_folder_path"] + "/" + filename
    img = merge_images(filepath)
    if img is None:
        continue
    img.save(config["output_folder_path"] + "/" + filename)
    print(index, filename, "saved")

print("finished")
print(li_exceptions)
