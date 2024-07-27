from PySide6.QtWidgets import QFileDialog

def FindProjectFile(name: str = None):
    options = QFileDialog.Options()

    title = "Select a project file"

    if name:
        title = f"Please locate the project file for '{name}'"

    fileName, _ = QFileDialog.getOpenFileName(None,
            title, "",
            "Project Files (*.json)", options=options)
    return fileName

def FindVideoFile(name: str = None):
    options = QFileDialog.Options()

    title = "Select a video file"
    if name:
        title = f"Please locate the video file '{name}'"

    fileName, _ = QFileDialog.getOpenFileName(None,
            title, "",
        "Video Files (*.mp4 *.avi *.mov *.mkv);;Other (*)", options=options)
    return fileName
