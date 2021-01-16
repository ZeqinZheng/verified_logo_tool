from PIL import Image, ImageChops
import json
import os

li_exceptions = []
template = None
max_x, max_y = 280, 280 

#verified_path = "/Users/Jm 1/Desktop/merge_verified_logo"
#template_name = "verified_logo.png"
#template = Image.open(verified_path+"/"+template_name)
#input_path = "/Users/Jm 1/Desktop/google_img"
#output_path = "/Users/Jm 1/Desktop/output_verified_logo"

config = {}
config_keys = ["template_file_path", "input_folder_path", "output_folder_path"]

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

    global template
    try:
        template = Image.open(config["template_file_path"])
    except Exception as e:
        print(e)
        exit(-1)

def get_filenames(abs_path):
    os.chdir(abs_path)
    files = os.listdir()
    return files

def cal_offset(logo):
    width, height = logo.size
    offset_x = (max_x - width)/2
    offset_y = (max_y - height)/2

    return offset_x, offset_y

def crop_white_space(logo):
    bg = Image.new(logo.mode, logo.size, logo.getpixel((0,0)))
    diff = ImageChops.difference(logo, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return logo.crop(bbox)
    else:
        return logo

def enlarge_image(logo):
    width, height = logo.size
    if width > 2 * height:
        ratio = min((max_x+130)/width, max_y/height)
    else:
        ratio = min(max_x/width, max_y/height)
    logo = logo.resize((int(width*ratio), int(height*ratio)), Image.ANTIALIAS)
    return logo

def merge_images(file_path):
    new_img = Image.new("RGB", (template.size))
    new_img.paste(template, (0,0))

    try:
        logo = Image.open(file_path) 
    except Exception as e:
        li_exceptions.append(str(e))
        return None
    #logo = crop_white_space(logo)
    logo.thumbnail((max_x, max_y), Image.ANTIALIAS)
    if logo.size[0] < max_x or logo.size[1] < max_y:
        logo = enlarge_image(logo)
    offset_x, offset_y = cal_offset(logo)
    position_x, position_y = int(pos_x+offset_x), int(pos_y+offset_y)
    new_img.paste(logo, (position_x, position_y))

    return new_img

load_parameters()
file_li = get_filenames(config["input_folder_path"])
pos_y_offset = 250
pos_x, pos_y = (template.size[0]/2 - max_x/2), 250

for index, filename in enumerate(file_li):
    filepath = config["input_folder_path"] + "/" + filename
    img = merge_images(filepath)
    if img is None:
        continue
    img.save(config["output_folder_path"] + "/" + filename) 
    print(index, filename, "saved")

print("finished")
print(li_exceptions)

