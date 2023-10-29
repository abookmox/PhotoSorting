import os
from PIL import Image
from shutil import copy2
import imghdr
import concurrent.futures

def get_image_info(file_path):
    try:
        image = Image.open(file_path)
        exif_info = image._getexif()
        return image, exif_info
    except (IOError, OSError, AttributeError):
        return None, None

def clean_folder_name(name):
    # Rimuovi spazi e caratteri non validi
    return name.strip().translate(str.maketrans("\/:*?\"<>|", "_________"))

def organize_image(file_path, output_folder, unidentified_folder, error_folder):
    image, exif_info = get_image_info(file_path)
    if image is not None and exif_info:
        date = exif_info.get(36867)
        make = exif_info.get(271)
        model = exif_info.get(272)

        if model:
            model = clean_folder_name(model)

        if date:
            year = date.split(" ")[0].split(":")[0]
            destination_folder = os.path.join(output_folder, year)
        else:
            destination_folder = unidentified_folder
        try:
            os.makedirs(destination_folder, exist_ok=True)
        except OSError as e:
            print(f"Errore nella creazione della cartella: {e}")

        if make:
            make = clean_folder_name(make)
            make_folder = os.path.join(destination_folder, make)
            try:
                os.makedirs(make_folder, exist_ok=True)
            except OSError as e:
                print(f"Errore nella creazione della cartella: {e}")

            if model:
                model_folder = os.path.join(make_folder, model)
                try:
                    os.makedirs(model_folder, exist_ok=True)
                except OSError as e:
                    print(f"Errore nella creazione della cartella: {e}")

                try:
                    if os.path.exists(file_path):
                        copy2(file_path, os.path.join(model_folder, os.path.basename(file_path)))
                    else:
                        print(f"Il file non esiste: {file_path}")
                        # Copia il file mancante nella cartella degli errori
                        copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
                except (IOError, OSError) as e:
                    print(f"Errore nella copia del file: {e}")
            else:
                try:
                    if os.path.exists(file_path):
                        copy2(file_path, os.path.join(make_folder, os.path.basename(file_path)))
                    else:
                        print(f"Il file non esiste: {file_path}")
                        # Copia il file mancante nella cartella degli errori
                        copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
                except (IOError, OSError) as e:
                    print(f"Errore nella copia del file: {e}")
        else:
            try:
                if os.path.exists(file_path):
                    copy2(file_path, os.path.join(destination_folder, os.path.basename(file_path)))
                else:
                    print(f"Il file non esiste: {file_path}")
                    # Copia il file mancante nella cartella degli errori
                    copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
            except (IOError, OSError) as e:
                print(f"Errore nella copia del file: {e}")
    else:
        os.makedirs(error_folder, exist_ok=True)
        try:
            if os.path.exists(file_path):
                copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
            else:
                print(f"Il file non esiste: {file_path}")
        except (IOError, OSError) as e:
            print(f"Errore nella copia del file in 'error': {e}")

def process_folder(input_folder, output_folder):
    unidentified_folder = os.path.join(output_folder, "unidentified")
    error_folder = os.path.join(output_folder, "error")
    os.makedirs(unidentified_folder, exist_ok=True)
    os.makedirs(error_folder, exist_ok=True)

    total_files = sum(len(files) for _, _, files in os.walk(input_folder))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for root, _, files in os.walk(input_folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                futures.append(executor.submit(organize_image, file_path, output_folder, unidentified_folder, error_folder))

        processed_files = 0
        for future in concurrent.futures.as_completed(futures):
            processed_files += 1
            if processed_files % 100 == 0:
                completion_percentage = (processed_files / total_files) * 100
                print(f"Progresso: {processed_files}/{total_files} ({completion_percentage:.2f}%)")

    print("Organizzazione completata!")

if __name__ == "__main__":
    input_folder = r"C:\foto recuperate"
    output_folder = r"C:\Users\ermox\OneDrive\Desktop\progetto\organizzate"
    process_folder(input_folder, output_folder)