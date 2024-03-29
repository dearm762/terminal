import os
import cups
import usb.core
import shutil
from flask import send_file
global latestOpen
global currentPath
global osDir
global openFile
currentPath = ""
osDir = "Macintosh HD"
openFile = ""
latestOpen = ""


def get_printer_list():
    try:
        conn = cups.Connection()
        printers = conn.getPrinters()
        return {"status": "success", "printers": list(printers.keys())}
    except cups.IPPError as e:
        return {"status": "error", "message": f"Failed to retrieve printers: {e}"}


def get_usb_devices():
    global currentPath
    try:
        devices = usb.core.find(find_all=True)
        device_list = []
        currentPath = f"/Volumes/"
        for volume_dir in os.listdir("/Volumes/"):
            if not volume_dir.startswith("Macintosh HD"):
                device_list.append(volume_dir)
        if len(device_list) > 0:
            return {
                "status": "success",
                "devices": device_list,
                "path": currentPath,
                "type": "devices",
            }
        else:
            return {"status": "error", "message": "No USB devices found"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve USB devices: {e}"}


def get_usb_device_folders():
    global currentPath
    try:
        devices = usb.core.find(find_all=True)
        device_list = []
        currentPath = f"/Volumes/"
        for volume_dir in os.listdir("/Volumes/"):
            if volume_dir != osDir:
                device_info = {
                    "deviceName": volume_dir,
                    "Path": get_flash_drive_path(currentPath),
                }
                device_list.append(device_info)
        if len(device_list) > 0:
            return {
                "status": "success",
                "devices": device_list,
                "path": currentPath,
                "type": "folder",
            }
        else:
            return {"status": "error", "message": "No USB devices found"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve USB devices: {e}"}


def get_flash_drive_path(current_Path):
    try:
        files = []
        folders = []
        for item in os.listdir(current_Path):
            item_path = os.path.join(current_Path, item)
            if os.path.isfile(item_path):
                if not item.startswith("."):
                    files.append(item)
            elif os.path.isdir(item_path):
                if not item.startswith("."):
                    folders.append(item)
        return {"files": files, "folders": folders}
    except Exception as e:
        return {"error": str(e)}


def get_folder_with_path(folderName):
    global currentPath
    if currentPath.endswith(folderName + "/"):
        pass
    else:
        currentPath = os.path.join(currentPath, folderName + "/")
    try:
        files = []
        folders = []
        for item in os.listdir(currentPath):
            item_path = os.path.join(currentPath, item)
            if os.path.isfile(item_path):
                if not item.startswith("."):
                    files.append(item)
            elif os.path.isdir(item_path):
                if not item.startswith("."):
                    folders.append(item)
        return {
            "status": "success",
            "files": files,
            "folders": folders,
            "path": currentPath,
            "type": "folders",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve contents: {e}"}


def get_folder_with_path_back():
    global currentPath
    parts = currentPath.split("/")  #  Split the URL by '/'
    currentPath = "/".join(parts[:-1])
    try:
        files = []
        folders = []
        for item in os.listdir(currentPath):
            item_path = os.path.join(currentPath, item)
            if not item == osDir:
                if os.path.isfile(item_path):
                    if not item.startswith("."):
                        files.append(item)
                elif os.path.isdir(item_path):
                    if not item.startswith("."):
                        folders.append(item)
        return {
            "status": "success",
            "files": files,
            "folders": folders,
            "path": currentPath,
            "type": "folders",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve contents: {e}"}
def copy_file(source_file):
    try:
        global currentPath
        script_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(currentPath, source_file)
        destination_path = os.path.join(script_dir, source_file)
        shutil.copy(source_path, destination_path)
        
        print({"status": "success", "message": "File copied successfully."})
    except Exception as e:
        print({"status": "error", "message": f"Failed to copy file: {e}"})

def get_document_url(documentName):
    global openFile
    global latestOpen
    global currentPath
    
    # Remove the previous file if it exists
    if os.path.exists(latestOpen):
        os.remove(latestOpen)
    
    # Set the path to the new file
    openFile = os.path.join(currentPath, documentName)
    
    # Copy the file if it doesn't exist
    if not os.path.exists(openFile):
        copy_file(documentName)
        latestOpen = f"./{documentName}"
    
    return {
        "status": "success",
        "filename": documentName,
        "filePath": openFile,
        "path": currentPath,
        "type": "folders",
    }

def get_file():
    return send_file(openFile, as_attachment=False)
