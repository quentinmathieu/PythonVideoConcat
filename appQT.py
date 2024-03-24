from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os, sys, pyperclip, json,html
from datetime import datetime
import ffmpeg

class ConcatenateThread(QThread):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

        def __init__(self, concat_file_path, output_file, myGui):
            super().__init__()
            self.concat_file_path = concat_file_path
            self.output_file = output_file
            self.myGui = myGui

        def run(self):
            try:
                ffmpeg.input(self.concat_file_path, format='concat', safe=0).output(self.output_file, c='copy').run()
                self.myGui.videoInfos.setText("Videos concatenated and saved as \n"+self.output_file.replace('\\',"/"))
                # output_message = "Concatenation completed successfully."
                print(self.concat_file_path)
                # Clean up temporary files
                os.remove(self.concat_file_path)
                self.myGui.setStatusInterface(True)
                print("Concatenation complete!")
                self.finished.emit("ok")
            except Exception as e:
                self.error.emit(str(e))


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("gui.ui", self)
        self.show()

        #enable D&D
        self.setAcceptDrops(True)

        # add clear & concat & concat/compress action's btn
        self.clearBtn.clicked.connect(lambda: self.clearList())
        self.concatBtn.clicked.connect(lambda: self.on_click())
        self.compressBtn.clicked.connect(lambda: self.crompressVideos())
        self.delListBtn.clicked.connect(lambda: self.deleteFromList())




    

    def on_click(self):
        self.videoInfos.setText("Prosessing...")
        file_paths = [self.filesList.item(x).text() for x in range(self.filesList.count())]
        self.setStatusInterface(False)
        
        if len(file_paths) < 2:
            self.setStatusInterface(True)
            self.videoInfos.setText("Select at least 2 videos to concatenate.")
            return

        codec = None
        for file_path in file_paths:
            # Use ffmpeg to get codec information of the videos
            try:
                probe = ffmpeg.probe(file_path)
            except Exception as error:
                self.setStatusInterface(True)
                self.videoInfos.setText("An exception occurred:", error)
                return 
            video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
            if codec is None:
                codec = video_info['codec_name']
            elif codec != video_info['codec_name']:
                self.setStatusInterface(True)
                self.videoInfos.setText("Videos have different codecs.")
                return

        # Filter videos by codec
        filtered_files = [f for f in file_paths if ffmpeg.probe(f)['streams'][0]['codec_name'] == codec]

        if len(filtered_files) < 2:
            self.videoInfos.setText("No videos with the same codec found.")
            return


        # Get the directory of the last file for the ouput path
        last_file_dir = os.path.dirname(file_paths[-1])

        # Generate the concat demuxer file
        concat_content = [f"file '{file_path}'" for file_path in filtered_files]
        concat_file_path =     output_file = os.path.join(last_file_dir, "concat.txt") 

        with open(concat_file_path, "w") as concat_file:
            concat_file.write('\n'.join(concat_content))


        # Get current timestamp to create output filename to the same directory as the last input file
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(last_file_dir, f"output_{current_time}.mp4") 

        self.concatThread = ConcatenateThread(concat_file_path, output_file, self)
        # self.concatThread.finished.connect(self.concatenationFinished)
        # self.concatThread.error.connect(self.concatenationError)
        self.concatThread.start()

       
        


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        files.sort()
        
        for f in files:
            if (f.lower().endswith(('.mts', '.mp4', '.avi','.mov','.mkv'))):
                self.filesList.addItem(f)

    def clearList(self):
        self.filesList.clear()

    def deleteFromList(self):
        listItems=self.filesList.selectedItems()
        if not listItems: return        
        for item in listItems:
            self.filesList.takeItem(self.filesList.row(item))


    def setStatusInterface(self, status):
        self.clearBtn.setEnabled(status)
        self.concatBtn.setEnabled(status)
        self.compressBtn.setEnabled(status)
        self.delListBtn.setEnabled(status)
        self.compressSlider.setEnabled(status)
        self.filesList.setEnabled(status)
        self.dropArea.setEnabled(status)

        self.setAcceptDrops(status)

    def crompressVideos(self):
        self.videoInfos.setText("WIP")


def main():
    try :
        # Add ffmpeg to the PATH
        ffmpegPath= os.path.dirname(os.path.realpath(__file__))+"\\ffmpeg\\bin"
        print(ffmpegPath)
        os.environ['PATH'] = ffmpegPath
    except Exception as error:
        print("An exception occurred:", error)
    app = QApplication(sys.argv)
    window = MyGUI()
    app.exec()


if __name__ == '__main__':
    main() 