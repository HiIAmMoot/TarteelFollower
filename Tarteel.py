import pygetwindow as gw
import time
import pyautogui
import win32gui
import win32con
import subprocess

import cv2
import os

import numpy as np
from mss import mss
import configparser

#import detect_pixel

# Disable the pyautogui failsafe feature
pyautogui.FAILSAFE = False

# Create a ConfigParser object and read the config file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the user's local AppData directory
local_appdata = os.getenv('LOCALAPPDATA')
test = True

initalized = False
recording = False
searching = False

config_name = "DEFAULT"
if test:
    config_name = "TEST"
    
# Get values from the config file
tarteel_path = os.path.join(local_appdata, config[config_name]["tarteel_path"])
print(tarteel_path)
tarteel_window_dimensions = eval(config[config_name]["tarteel_window_dimensions"]) # Width and height of the Tarteel window
tarteel_window_location = eval(config[config_name]["tarteel_window_location"]) # Location of the Tarteel window
quran_region = eval(config[config_name]["quran_region"]) # Screen coordinates of the quran text (left, upper, right, lower)
search_region = eval(config[config_name]["search_region"]) # Screen coordinates the search area (left, upper, right, lower)
quran_region = eval(config[config_name]["quran_region"]) # Screen coordinates of the quran text (left, upper, right, lower)
click_location = eval(config[config_name]["click_location"]) # Record click location
ayah_height = int(config[config_name]["ayah_height"]) # The height of one ayah row
search_color = eval(config[config_name]["search_color"]) # The text color of the text that is displayed when Tarteel is searching
ayah_highlight_color = eval(config[config_name]["ayah_highlight_color"]) # The color shown when an ayah is highlighted
word_highlight_color = eval(config[config_name]["word_highlight_color"]) # The color shown when a word is highlighted
background_color = eval(config[config_name]["background_color"]) # The color of the background of tarteel
color_tolerance = int(config[config_name]["color_tolerance"]) # The amoun tolerance to use when looking for a specific color
check_time = int(config[config_name]["check_time"]) # The amount of time to recheck if the recording is going correctly
search_time = int(config[config_name]["search_time"]) # The amount of time to recheck if the recording has finished searching

def start():
    if test:
        return
    # Get the user's local AppData directory
    #tarteel_path = r"C:\Users\Nour el Houda\AppData\Local\Microsoft\WindowsApps\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\WsaClient.exe"
    command_line = [tarteel_path, '/launch', 'wsa://com.mmmoussa.iqra']
    
    try:
        subprocess.run(command_line, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Function to check if a color is within a specified range
def is_color_within_range(color, target_color, grayscale):
    color_range = 1
    if not grayscale:
        color_range = 3
    return all(abs(color[i] - target_color[i]) <= color_tolerance for i in range(color_range))

# Function to find the coordinates of the first pixel with at least two neighboring pixels of the specified color
def find_first_pixel_with_color(image, target_color, grayscale):
    height, width = image.shape[:2]

    for y in range(height - 1):
        for x in range(width - 1):
            pixel_color = image[y, x]
            if is_color_within_range(pixel_color, target_color, grayscale):
                # Check if at least two neighboring pixels have the same color
                neighbor_colors = [
                    image[y, x + 1],
                    image[y + 1, x],
                    #image[y + 1, x + 1]
                ]
                if sum(is_color_within_range(neighbor_color, target_color, grayscale) for neighbor_color in neighbor_colors) >= 2:
                    #print(x)
                    #print(y)
                    return x, y, True

    return 0, 0, False

def check_searching(screenshot):
    # Crop the screenshot to the specified region
    cropped_image = screenshot.crop(search_region)

    # Iterate through pixels in the cropped image
    for x in range(cropped_image.width):
        for y in range(cropped_image.height):
            pixel_color = cropped_image.getpixel((x, y))
            if is_color_within_range(pixel_color, search_color, False):
                return True
    return False


def make_window_always_on_top(window_title):
    if test:
        return
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        hwnd = win32gui.FindWindow(None, window.title)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    except IndexError:
        print(f"Window with title '{window_title}' not found.")

def set_window_size_and_position(window_title, width, height, x, y):
    if test:
        return 1
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.resizeTo(width, height)
        window.moveTo(x, y)
    except IndexError:
        print(f"Window with title '{window_title}' not found.")
        return 0
    return 1

def get_window_size_and_position(window_title):
    if test:
        return None
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        width, height = window.width, window.height
        x, y = window.left, window.top
        return width, height, x, y
    except IndexError:
        print(f"Window with title '{window_title}' not found.")
        return None

def check_image_and_click(image_path, click_location):
    global recording
    if test:
        recording = True
        return
    # Attempt to locate the image on the screen
    try:
        image_location = pyautogui.locateOnScreen(image_path)
        recording = True
        print("Image found! No need to click.")
    except:
        recording = False
        print("Image not found. Clicking at the specified location.")
        click_location_and_return(click_location)

def click_location_and_return(click_location):
    # Store the current mouse position
    original_mouse_position = pyautogui.position()
    
    try:
        # Click at the specific location
        pyautogui.click(click_location)
    finally:
        # Restore the original mouse position
        pyautogui.moveTo(original_mouse_position)


def run():
    global initialized
    global searching
    
    try:
    # Specify the title of the window we want to resize and move
        target_window_title = "Tarteel"
    
        # Specify the size and position you want to set
        window_width, window_height = tarteel_window_dimensions
        window_x, window_y = tarteel_window_location
    
        # Set window size and position
        success = set_window_size_and_position(target_window_title, window_width, window_height, window_x, window_y)
        
        if not success:
            start()
            time.sleep(10)
    
        initalized = True
    
        # Get window size and position
        window_info = get_window_size_and_position(target_window_title)
    
        if window_info:
            print(f"Window size and position: {window_info}")

        # Get current mouse position
        mouse_x, mouse_y = pyautogui.position()
    
        # Print the coordinates
        print(f"Mouse coordinates: x={mouse_x}, y={mouse_y}")
            
        # Specify the path to your PNG image
        image_path = "Record.png"
        
        should_check = True
        check_timestamp = time.time()
    except:
        print("Init failed!")

    #make_window_always_on_top(target_window_title)

    while(True):
        try:
            timestamp = time.time();
            if timestamp - check_timestamp > check_time:
                check_timestamp = timestamp
                # Check for the image and click if necessary
                check_image_and_click(image_path, click_location)
                
                # Capture screenshot of the screen
                screenshot = pyautogui.screenshot()
                
                if recording:
                    searching = check_searching(screenshot)
                
                    if searching:
                        print("Tarteel is searching..")
                        time.sleep(10)
                        searching = check_searching(screenshot)
                        if searching:
                            # Stop recording
                            click_location_and_return(click_location)
                    else:
                        print("Tarteel is not searching")
        except:
            print("Recording and searching failed!")
            break
        
        try:
            bounding_box = {'top': quran_region[0], 'left': quran_region[1], 'width': quran_region[2], 'height': quran_region[3]}
            
            sct = mss()      
            
            # Capture the screen region
            sct_img = sct.grab(bounding_box)
    
            # Convert the screen capture to a NumPy array
            frame = np.array(sct_img)
        except:
            print("Getting frame failed!")
            break

        # Find the coordinates of the first pixel with the specified color
        try:
            first_pixel = find_first_pixel_with_color(frame, word_highlight_color, False)
            x, y, success = first_pixel
            if success:
                # Extract the coordinates of the bounding box around the detected pixel
                left = 0
                width = bounding_box['width']
                height = ayah_height
                top = y
                
                # Crop the region around the detected pixel
                cropped_frame = frame[top:top + height, left:left + width]
        
                # Display the cropped frame
                cv2.imshow('Tarteel Processed', cropped_frame)
            else:
                image = np.zeros((ayah_height, bounding_box["width"], 3), np.uint8)
                # Since OpenCV uses BGR, convert the color first
                color = tuple(reversed(background_color))
                # Fill image with color
                image[:] = color
                # Display the cropped frame
                cv2.imshow('Tarteel Processed', image)
        except:
            print("Finding highlight failed!")
            break
        try:
            # Check for key press to exit
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                break
        except:
            print("Keypress failed!")
            break
    
    # Wait
    try:
        time.sleep(check_time)
    except:
        print("Wait failed!")
        
    run()
        
if __name__ == "__main__":
    run()
