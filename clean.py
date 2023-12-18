
import sys
import os
import shutil
from pathlib import Path
import re

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}



for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()
    
    
    
images = []
video = []
documents = []
audio = []
archives =[]


list_of_known_formats = set()
list_of_unknown_formats = set()

    



## Функція для перейменування файлів
def normalize_item(item):      

    translated_name = ''
            
    for i in item.stem:  # Перейменування файлу без суфіксу
        if i.isalpha():
            translated_name += i.translate(TRANS)
        elif i.isdigit():
            translated_name += i 
        else:
            translated_name += '_'
                    
    folder_path = item.parent
    new_path = folder_path / f"{translated_name}{item.suffix}"   # Створення шляху з новим ім'ям файлу
    item.rename(new_path)    # Перейменування файлу


##  Функція ждя перейменування всіх файлів в папці, в інших папках функція перезапрускає себе            
def normalize_folder(path):
    
    for object in path.iterdir():  
        
        if object.is_file():
            normalize_item(object)
        else:
            normalize_folder(object)
            normalize_item(object)


## Створення папки

def create_folder(path, name): 
    
    new_folder_path = os.path.join(path, name)
    os.makedirs(new_folder_path, exist_ok=True)
    return new_folder_path


## Створення папок для сортування в кореній папці за допомогою функції create_folder
def create_folders_for_sorting(path):   
    
    global images_folder, video_folder, documents_folder, audio_folder, archives_folder   # Визначаємо глобальні змінні(шляхи до нових папок)
    images_folder = create_folder(path, 'images')                                         # щоб вертатися до них при переміщенні
    video_folder = create_folder(path, 'video')
    documents_folder = create_folder(path, 'documents')
    audio_folder = create_folder(path, 'audio')
    archives_folder = create_folder(path, 'archives')
    
    

# Функція на перевірку, чи існує файл з таким ім'ям -
def remove_file(file, new_folder_path):
    
    try:

        destination_path = Path(new_folder_path) / file.name

        if os.path.exists(destination_path):                     #Перевіряє, чи є файл з таким ім'ям
                
                base, extension = os.path.splitext(file.name)
                new_name = f"{base}_copy{extension}"
                destination_path = Path(new_folder_path) / new_name

                file.rename(destination_path)
                shutil.move(destination_path, new_folder_path)
        else:                                                      # Якщо нема, просто переміщує файл
            shutil.move(file, new_folder_path)
            
    except Exception as e:
        print(f"Помилка: {e}")  
    
            

## Функція перевіряє кожен файл за допомогою re.search, за збігом по формату
## Якщо зустрічає папку, перезапускає себе 
## Окремо додає формат (suffix) до списку відомих чи не відомих форматів 
    
def check_file_formats_version_one(path):

    try:
        for i in path.iterdir():
            
            if i.is_file() == True:

                # Використовуємо fnmatch для фільтрації файлів за форматами зображень
                if re.search(r'.jpeg|.png|.jpg|.svg|.bmp', i.suffix, flags=re.IGNORECASE):
                    remove_file(i, images_folder)
                    images.append(i.name)
                    list_of_known_formats.add(i.suffix)
                # Використовуємо fnmatch для фільтрації файлів за форматами відео
                if re.search(r'.avi|.mp4|.mov|.mkv', i.suffix, flags=re.IGNORECASE):
                    remove_file(i, video_folder)
                    video.append(i.name)
                    list_of_known_formats.add(i.suffix)
                # Використовуємо fnmatch для фільтрації файлів за форматами документів
                if re.search(r'.doc|.docx|.txt|.pdf|.xlsx|.pptx|.xls', i.suffix, flags=re.IGNORECASE):
                    remove_file(i, documents_folder)
                    documents.append(i.name)
                    list_of_known_formats.add(i.suffix)
                # Використовуємо fnmatch для фільтрації файлів за форматами музики
                if re.search(r'.mp3|.ogg|.wav|.amr', i.suffix, flags=re.IGNORECASE):
                    remove_file(i, audio_folder)
                    audio.append(i.name)
                    list_of_known_formats.add(i.suffix)
                # Використовуємо fnmatch для фільтрації файлів за форматами архівів
                if re.search(r'.zip|.gz|.tar', i.suffix, flags=re.IGNORECASE):
                    remove_file(i, archives_folder)
                    archives.append(i.name)
                    list_of_known_formats.add(i.suffix)
                # Варіант для невідомих форматів
                if i.suffix not in list_of_known_formats:
                    list_of_unknown_formats.add(i.suffix)
                # варіант для папок - функція запускає себе знову
            if i.is_dir() == True:
                check_file_formats_version_one(i)                

    except Exception as e:
        print(f"Помилка: {e}")
        
     
## Функція для разорхіваціі архівів 
def extracting_archives(archives_folder):
    
    archives_folder = Path(archives_folder)
    try:
        
        for archive in archives_folder.iterdir():
                
            archive_name = os.path.splitext(os.path.basename(archive))[0] ## Розділяє ім'я від розширення в кінці

            new_folder_path = os.path.join(archives_folder, archive_name)  ## Створення підпапки з назвою архіва
            os.makedirs(new_folder_path, exist_ok=True)
                
            shutil.unpack_archive(archive, new_folder_path)   # Розпакування в нову папку
                
    except Exception as e:
        print(f"Помилка: {e}")  
        
        
## Функція для видалення пустих папок        
def deleting_empty_folders(path):
    
    for folder in path.iterdir(): 
        
        if folder.is_dir():        # Перевіряє, чи предмет ітерації - папка
            files = os.listdir(folder)    # Перевіряє, чи є файли в папці

            if not files:       # Якщо файлів нема, папка видаляється
                shutil.rmtree(folder)     



## Функція для обработки папки
def sort_of_folder(path):
    
    normalize_folder(path)
    
    create_folders_for_sorting(path)
    
    check_file_formats_version_one(path)
    
    extracting_archives(archives_folder)
    
    deleting_empty_folders(path)
    
    print(f"Список зображень: {images}\n" 
          f"Список відео: {video}\n" 
          f"Список документів: {documents}\n" 
          f"Список аудіо: {audio}\n" 
          f"Список архівів: {archives}\n" 
          f"Список форматів відсортованих файлів: {list_of_known_formats}\n" 
          f"Список форматів невідомих файлів: {list_of_unknown_formats}")

## Запуск фунціі з вводу з командного рядка
def run():

     
    arguments = sys.argv[1:]   # аргумент [0] - назва скрипта, тому початок з першого

    if arguments:        #Перевірка на аргументи
            
        if len(arguments) > 1:   # якщо більше одного, то може бути, що назва папки розділена пробілом (прикл. Рабочитй Стіл)
            final_arg = ''       # і ці аргументи треба зібрати в один
            for i in arguments:
                final_arg += i
                if i is not arguments[-1]:
                    final_arg += " "   # додає пробіл, якщо це не останній аргумент
            path = Path(final_arg)
            sort_of_folder(path)
                    
        else:
            folder_path = arguments[0]
            path = Path(folder_path)
            sort_of_folder(path)
    else:
        print("Введіть шлях до папки як аргумент командного рядка.")

