from webscreenshotter import take_screenshot
from pyzbar.pyzbar import decode
import cv2, os, json, shutil, argparse, re
from pathlib import Path

parser = argparse.ArgumentParser(description="Scan QR Codes on any webpage")
parser.add_argument('-u', '--url', action='store_true', help='grab URLs only')
parser.add_argument('-o', '--output_file', nargs='?' , const='output.json', default=None, help='Output file name')
args = parser.parse_args()

def extract_url(input_string):
    url_pattern = re.compile(r'https?://[^\s"\'\,>\])}]+')
    url_match = url_pattern.search(input_string)
    url = url_match.group() if url_match else None
    return url


def read_qr_codes(image_path) -> list:
    codes = []
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    qr_codes = decode(gray_image)
    for qr_code in qr_codes:
        qr_data = qr_code.data.decode('utf-8')
        codes.append(str(qr_data))
    
    return qr_codes

if __name__ == "__main__":
    scanned_items = []
    temp_dir = ".screencaps"
    
    take_screenshot (
        "https://en.wikipedia.org/wiki/qr_code",
        width=1920, height=1080,
        directory=temp_dir, file_suffix="capture_",
        stitch=False
    )
    
    path_obj = Path(temp_dir)
    
    for item in path_obj.iterdir():
        if item.is_file():
            code_data = read_qr_codes(str(item))
            for item in code_data: scanned_items.append(str(item))
    
    if args.url:
        urls_only = []
        for item in scanned_items:
            if "://" in item: urls_only.append(extract_url(item))
        scanned_items = urls_only
    
    jsonified_data = json.dumps(scanned_items, indent=4)
    
    output_file = args.output_file
    
    with open(output_file, "w") as _file:
        _file.write(jsonified_data)
        _file.close()
        
    shutil.rmtree(temp_dir)
