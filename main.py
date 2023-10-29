import os
from PIL import Image
from shutil import copy2
import concurrent.futures
import warnings

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
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            with Image.open(file_path) as image:
                exif_info = image._getexif()
        return image, exif_info
    except Exception as e:
        if "Truncated File Read" in str(e):
            print(f"Errore durante la lettura dell'immagine {file_path}: Truncated File Read. Spostando nella cartella di errore.")
            error_file_path = os.path.join(error_folder, os.path.basename(file_path))
            copy2(file_path, error_file_path)
        else:
            print(f"Errore durante la lettura dell'immagine {file_path}: {str(e)}")
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
            date_parts = date.split(" ")[0].split(":")
            if len(date_parts) == 3:
                year = date_parts[0]
                month = date_parts[1]
                if month in mesi_italiani:
                    month = mesi_italiani[month]  # Usa il mese italiano
                    year_folder = os.path.join(output_folder, year)
                    month_folder = os.path.join(year_folder, month)
                    try:
                        os.makedirs(month_folder, exist_ok=True)
                        if os.path.exists(file_path):
                            copy2(file_path, os.path.join(month_folder, os.path.basename(file_path)))
                            processed_counter[0] += 1  # Incrementa il contatore di file processati con successo
                        else:
                            print(f"Il file non esiste: {file_path}")
                            copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
                    except (IOError, OSError) as e:
                        print(f"Errore nella copia del file: {e}")
                        copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
                else:
                    print(f"Mese non valido nel formato EXIF: {month}")
                    copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
            else:
                print(f"Formato data non valido nel formato EXIF: {date}")
                copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
        else:
            os.makedirs(unidentified_folder, exist_ok=True)
            try:
                if os.path.exists(file_path):
                    copy2(file_path, os.path.join(unidentified_folder, os.path.basename(file_path)))
                    processed_counter[0] += 1  # Incrementa il contatore di file processati con successo
                else:
                    print(f"Il file non esiste: {file_path}")
                    copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
            except (IOError, OSError) as e:
                print(f"Errore nella copia del file in 'unidentified': {e}")
                copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
    else:
        os.makedirs(error_folder, exist_ok=True)
        try:
            if os.path.exists(file_path):
                copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
                processed_counter[0] += 1  # Incrementa il contatore di file processati con successo
            else:
                print(f"Il file non esiste: {file_path}")
                copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))
        except (IOError, OSError) as e:
            print(f"Errore nella copia del file in 'error': {e}")
            copy2(file_path, os.path.join(error_folder, os.path.basename(file_path)))


def process_folder(input_folder, output_folder):
    # Crea le cartelle 'unidentified' e 'error' nella cartella di output
    unidentified_folder = os.path.join(output_folder, "unidentified")
    error_folder = os.path.join(output_folder, "error")
    os.makedirs(unidentified_folder, exist_ok=True)
    os.makedirs(error_folder, exist_ok=True)

    # Ottieni una lista di tutti i file presenti nella cartella di input
    input_files = []
    for root, _, files in os.walk(input_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            input_files.append(file_path)

    # Calcola il numero totale di file da elaborare
    total_files = len(input_files)

    # Inizializza un contatore per i file processati con successo
    processed_counter = [0]

    # Utilizza un ThreadPoolExecutor per elaborare i file in parallelo con un massimo di 4 thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for file_path in input_files:
            # Avvia l'esecuzione della funzione 'organize_image' per ogni file
            futures.append(executor.submit(organize_image, file_path, output_folder, unidentified_folder, error_folder, processed_counter))

        processed_files = 0
        for future in concurrent.futures.as_completed(futures):
            processed_files += 1
            if processed_files % 100 == 0:
                # Calcola e stampa il progresso percentuale
                completion_percentage = (processed_files / total_files) * 100
                print(f"Progresso: {processed_files}/{total_files} ({completion_percentage:.2f}%)")

            if future.exception() is not None:
                # Gestisce eventuali eccezioni durante l'elaborazione di un file
                print(f"Errore nell'elaborazione di {future.result()}")

    # Stampa un messaggio di completamento con il numero di file elaborati con successo
    print(f"Organizzazione completata! {processed_counter[0]} file processati con successo su {total_files}.")



if __name__ == "__main__":
    input_folder = r"C:\progetto\organizzate"
    output_folder = r"C:\progetto\ordinate"
    process_folder(input_folder, output_folder)
