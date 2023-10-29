import os
from PIL import Image
from shutil import copy2
import concurrent.futures

mesi_italiani = {
    '01': 'gennaio',
    '02': 'febbraio',
    '03': 'marzo',
    '04': 'aprile',
    '05': 'maggio',
    '06': 'giugno',
    '07': 'luglio',
    '08': 'agosto',
    '09': 'settembre',
    '10': 'ottobre',
    '11': 'novembre',
    '12': 'dicembre'
}

def get_image_info(file_path, error_folder):
    try:
        with Image.open(file_path) as image:
            exif_info = image._getexif()
        return image, exif_info
    except Exception as e:
        print(f"Errore durante la lettura dell'immagine {file_path}: {str(e)}. Spostando nella cartella di errore.")
        error_file_path = os.path.join(error_folder, os.path.basename(file_path))
        copy2(file_path, error_file_path)
        return None, None


def clean_folder_name(name):
    return name.strip().translate(str.maketrans("\/:*?\"<>|", "_________"))

def organize_image(file_path, output_folder, unidentified_folder, error_folder, processed_counter):
    image, exif_info = get_image_info(file_path, error_folder)
    if image is not None and exif_info:
        date = exif_info.get(36867)  # Informazioni sulla data
        if date:
            year = date.split(" ")[0].split(":")[0]
            month = mesi_italiani[date.split(" ")[0].split(":")[1]]  # Usa il mese italiano
            year_folder = os.path.join(output_folder, year)
            month_folder = os.path.join(year_folder, month)
            try:
                os.makedirs(month_folder, exist_ok=True)
            except OSError as e:
                print(f"Errore nella creazione della cartella: {e}")

            try:
                if os.path.exists(file_path):
                    copy2(file_path, os.path.join(month_folder, os.path.basename(file_path)))
                    processed_counter[0] += 1  # Incrementa il contatore di file processati con successo
                else:
                    print(f"Il file non esiste: {file_path}")
                    copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
            except (IOError, OSError) as e:
                print(f"Errore nella copia del file: {e}")
        else:
            os.makedirs(unidentified_folder, exist_ok=True)
            try:
                if os.path.exists(file_path):
                    copy2(file_path, os.path.join(unidentified_folder, os.path.basename(file_path)))
                    processed_counter[0] += 1  # Incrementa il contatore di file processati con successo
                else:
                    print(f"Il file non esiste: {file_path}")
            except (IOError, OSError) as e:
                print(f"Errore nella copia del file in 'unidentified': {e}")
    else:
        os.makedirs(error_folder, exist_ok=True)
        try:
            if os.path.exists(file_path):
                copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
                processed_counter[0] += 1  # Incrementa il contatore di file processati con successo
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
    processed_counter = [0]  # Lista con un valore per tenere traccia dei file processati

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for root, _, files in os.walk(input_folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                futures.append(executor.submit(organize_image, file_path, output_folder, unidentified_folder, error_folder, processed_counter))

        processed_files = 0
        for future in concurrent.futures.as_completed(futures):
            processed_files += 1
            if processed_files % 100 == 0:
                completion_percentage = (processed_files / total_files) * 100
                print(f"Progresso: {processed_files}/{total_files} ({completion_percentage:.2f}%)")

    print(f"Organizzazione completata! {processed_counter[0]} file processati con successo su {total_files}.")

if __name__ == "__main__":
    input_folder = r"C:\progetto\organizzate"
    output_folder = r"C:\progetto\ordinate"
    process_folder(input_folder, output_folder)
