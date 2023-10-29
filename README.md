# PhotoSorting
# Image Organizer Script

The Image Organizer Script is a Python program designed to organize a collection of image files based on their EXIF metadata, such as date and time, and store them in a structured folder hierarchy. It also handles errors, including files with missing or corrupted EXIF data.

## Features

- Organizes images into folders based on their capture date, using the Italian month names.
- Handles images with missing or corrupted EXIF data.
- Creates folders for unidentified images and errors.
- Multi-threaded processing for faster execution.

## Prerequisites

Before using the script, ensure you have the following installed:

- Python 3.x
- The Python Imaging Library (PIL)
- A directory containing the images you want to organize.

## Usage

1. Clone or download this repository to your local machine.

2. Open a terminal or command prompt and navigate to the script's directory.

3. Edit the `input_folder` and `output_folder` variables in the script to specify the paths to your input and output folders.

4. Run the script using the following command:

   ```shell
   python image_organizer.py

1. The script will process the images in the input folder, organize them into the output folder, and create 'unidentified' and 'error' folders as needed.

2. The progress of the organization process will be displayed in the terminal, and any errors will be logged.

3. Once the process is complete, the script will provide a summary of the number of files successfully processed and any files that couldn't be processed.

Customization
You can customize the script by editing the following:

mesi_italiani: This dictionary allows you to map month numbers to Italian month names. You can modify it to support other languages or date formats.
Error Handling
The script handles the following types of errors:

Truncated File Read: Files with corrupted or missing EXIF data are moved to the 'error' folder.
Invalid EXIF Data: Files with invalid or missing date information are moved to the 'error' folder.
Nonexistent Files: Files that no longer exist are logged and moved to the 'error' folder.

Contributors
- Gabriele Mossino  
- kinglyudk@gmail.com
- https://github.com/abookmox

License
This project is licensed under the MIT License - see the LICENSE file for details.
