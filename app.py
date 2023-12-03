import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import ffmpeg
import os

try :
    
    # Add ffmpeg to the PATH
    ffmpegPath= os.path.dirname(os.path.realpath(__file__))+"\\ffmpeg\\bin"
    print(ffmpegPath)
    os.environ['PATH'] = ffmpegPath
except Exception as error:
     print("An exception occurred:", error)



print(os.getcwd())

def concatenate_videos():
    file_paths = file_list.get(0, tk.END)
    if len(file_paths) < 2:
        status_label.config(text="Select at least 2 videos to concatenate.")
        return
 
    codec = None
    for file_path in file_paths:
        # Use ffmpeg to get codec information of the videos
        try:
            probe = ffmpeg.probe(file_path)
        except Exception as error:
            print("An exception occurred:", error)
            return 
        video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        if codec is None:
            codec = video_info['codec_name']
        elif codec != video_info['codec_name']:
            status_label.config(text="Videos have different codecs.")
            return
 
    # Filter videos by codec
    filtered_files = [f for f in file_paths if ffmpeg.probe(f)['streams'][0]['codec_name'] == codec]
 
    if len(filtered_files) < 2:
        status_label.config(text="No videos with the same codec found.")
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
    # Concatenate videos using ffmpeg
    try:
        ffmpeg.input(concat_file_path, format='concat', safe=0).output(output_file, c='copy').run()
        status_label.config(text=f"Videos concatenated and saved as \n{output_file}.")
    except ffmpeg.Error as e:
        status_label.config(text=f"Error concatenating videos: {str(e)}")
 
    # Clean up temporary files
    os.remove(concat_file_path)
 
def add_files(event=None):
    files = filedialog.askopenfilenames(filetypes=[("Video files", "*.MTS;*.mp4;*.avi;*.mov;*mkv")])
    for file in files:
        file_list.insert(tk.END, file)
 
# Create the main window
root = tk.Tk()
root.title("Video Concatenator")
root.geometry('500x300')

 
# Create and pack the listbox
file_list = tk.Listbox(root, selectmode=tk.MULTIPLE)
file_list.config(height=13, width=75)
file_list.pack()
 
# Create the buttons
add_button = tk.Button(root, text="Add Files", command=add_files)
add_button.pack()
 
concat_button = tk.Button(root, text="Concatenate Videos", command=concatenate_videos)
concat_button.pack()
 
# Create status label
status_label = tk.Label(root, text="")
status_label.pack()
 
root.mainloop()