from itertools import tee
from tkinter import *
from tkinter import messagebox
import tkinter
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import os.path as path
from mutagen.easyid3 import *
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TT2, TPE1, TRCK, TALB, USLT, error
import requests
import eyed3
from eyed3.id3.frames import ImageFrame
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import os
import webbrowser




#Función para abrir enlaces
def callback(url):
    webbrowser.open_new(url)

#SE crea la app tkinter
app = tkinter.Tk()
app.geometry("600x500")
app.title("MyTag")
app.configure(bg='#FFFFFF')
app.resizable(0,0)

#En este array se guardan los archivos de audio de la carpeta
thefiles = []


MinOneFile = False

#Funcion para añadir texto a la consola
def create_label_console(w ,texts, color, size):
    count = len(app.winfo_children())
    label = tkinter.Label(w, text=f"-" + texts)
    label.configure(foreground=color, font = ("Terminal", size), bg="#000000")
    label.grid()

#Funcion del boton de busquda de carpeta
def browse_button():
    global thefiles
    global filename
    
    thefiles = []
    MinOneFile = False
    
    # El directorio se almacena en folder_path
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    content = os.listdir(filename)

    for fichero in content:
        if os.path.isfile(os.path.join(filename, fichero)):
            if fichero.endswith('.mp3') or fichero.endswith('.wav'):
                thefiles.append(fichero)
    print(thefiles)

#Descarga el album cover
def download_cover(url):
    f = open('cover.jpg','wb')
    print(url)
    response = requests.get(url)
    f.write(response.content)
    f.close()

#Buscar
def search():
    global MinOneFile
    songsWithoutFile = []
    #Se obtiene el nombre del album y el artista (se obtiene de los inputs de que rellenaron los usuarios)
    album0 = searchAlbumEntry.get()
    artist0 = searchArtistEntry.get()

    #Se remplazan los caracteres especiales y se convierten a URL Encoder
    album1 = album0.replace(' ','%20')
    artist1 = artist0.replace(' ','%20')
    album1 = album1.replace('ü','%C3%BC')
    artist1 = artist1.replace('ü','%C3%BC')
    
    #Se abre la url donde esta la info del album y del artista
    var_url = urlopen('http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=9431a6366225e88f9a1d9d0ce988e893&artist='+ artist1 +'&album='+ album1 +'&format=xml')
    xmldoc = parse(var_url)
    root = xmldoc.getroot()

    #Se obtiene el album, el artista, el link de la imagen
    album = root[0][0].text
    artist = root[0][1].text
    imagelink = root[0][8].text

    #Se crea la pantalla console
    console = Toplevel()
    console.geometry("640x310")
    console.title(album + " - " + artist + " - Consola")
    console.configure(bg='#000000')
    
    #Se ejecuta la funcion de descarga de imagen
    download_cover(imagelink)

    #Por cada track del album
    for track in root.iter('track'):
        #Se obtiene el nombre del track
        nametrack = track.find('name').text
        #Se obtiene el numero de track
        numbertrack = track.get('rank')

        #Por cada archivo de audio en la carpeta seleccionada
        for file in thefiles:
            songaaa = nametrack
            fileaaa = file.lower()
            songaaa = songaaa.lower()
            #songaaa se convierte en un array que separa cada palabra
            songaaa = songaaa.split(" ")
            nw = 0

            for w1 in songaaa: #Por cada palabra in songaaa
                w2 = w1.replace("'", "")
                w2 = w2.replace(",", "")
                print(w2)
                if w1 in fileaaa or w2 in fileaaa:
                    nw = nw + 1
                    if nw == len(songaaa): #Cuando todas las palabras han sido acertadas asignar las etiquetas
                        MinOneFile = True
                        tags = EasyID3(filename + "/" + file)
                        id3 = ID3(filename + "/" + file)
                        tags["title"] = nametrack
                        tags["artist"] = artist
                        tags["album"] = album
                        tags['tracknumber'] = numbertrack
                        tags.save()
                
                        #Se aplica el album cover
                        imagedata = open("cover.jpg", 'rb').read()
                        id3.add(APIC(3, 'image/jpeg', 3, 'Front cover', imagedata))
                        
                        #Se aplica el album cover
                        audiofile = eyed3.load(filename + "/" + file)
                        if (audiofile.tag == None):
                            audiofile.initTag()
                        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open('cover.jpg','rb').read(), 'image/jpeg')
                        audiofile.tag.save()

                        #Se inserta texto en la consola mostrando que se encontró un archivo
                        create_label_console(console, "Se encontró un archivo para " + nametrack, "green", 10)
        
                else:
                    break

        


    #Si todo salió bien
    if folder_path and MinOneFile:
        create_label_console(console, "Se le han aplicado las etiquetas a los archivos que encontramos", "green", 15)
    #Si 
    if not folder_path != "PY_VAR0" and not MinOneFile:
        create_label_console(console, "No se encontraron canciones", "red", 15)
        
    

            
            


folder_path = StringVar()                                                                                                         


#De aqui en adelante es la interfaz

chooseFolderlabel = Label(text="Seleccione la carpeta donde se encuentran los archivos de audio:")
chooseFolderlabel.grid(row= 0, column= 0, padx=10, pady=10)
chooseFolderlabel.config(fg = "#1556A4", bg = "#FFFFFF", font = ("Roboto Light", 15))


button2 = Button(text="Abrir Carpeta", command=browse_button)
button2.grid(row= 1, column= 0, padx=10, pady=10)
button2.config(bg = "#1556A4", relief=SUNKEN, bd=0, fg="#FFFFFF", width="11", height="1", font = ("Roboto Light", 10))
lbl1 = Label(master=app,textvariable=folder_path)
lbl1.grid(row= 2, column= 0, padx=10, pady=10)
lbl1.config(fg = "#1556A4", bg = "#FFFFFF", font = ("Roboto Light", 9))


AlbumNameLabel = tkinter.Label(app, text="Nombre del album:")
AlbumNameLabel.grid(row= 3, column= 0, padx=10, pady=10)
AlbumNameLabel.config(fg = "#1556A4", bg = "#FFFFFF", font = ("Roboto Light", 15))

searchAlbumEntry = tkinter.Entry(app, width=50)
searchAlbumEntry.config(fg = "#000000", bg = "#FFFFFF", font = ("Roboto Light", 10))
searchAlbumEntry.grid(row= 4, column= 0, padx=10, pady=10)

ArtistNameLabel = tkinter.Label(app, text="Nombre del artista:")
ArtistNameLabel.grid(row= 5, column= 0, padx=10, pady=10)
ArtistNameLabel.config(fg = "#1556A4", bg = "#FFFFFF", font = ("Roboto Light", 15))

searchArtistEntry = tkinter.Entry(app, width=50)
searchArtistEntry.grid(row= 6, column= 0, padx=10, pady=10)
searchArtistEntry.config(fg = "#000000", bg = "#FFFFFF", font = ("Roboto Light", 10))

searchButton = Button(app, text= "Asignar datos", command= search)
searchButton.grid(row= 7, column= 0, padx=10, pady=10)
searchButton.config(bg = "#1556A4", relief=SUNKEN, bd=0, fg="#FFFFFF", width="12", height="1", font = ("Roboto Light", 15))


link1 = Label(app, text="Reportar un error", fg="#1556A4", bg="white", cursor="hand2")
link1.grid()
link1.bind("<Button-1>", lambda e: callback("https://pasteluengas.github.io/MyTag/index.html#Bug"))

Mark = Label(app, text='v1.0.0 Beta | PasteLuengas')
Mark.grid(row=10, column=0, pady=50)
Mark.config(fg = "#000000", bg = "#FFFFFF")

#Comprobacion de Internet
try:
    request = requests.get("http://www.google.com", timeout=5)
except (requests.ConnectionError, requests.Timeout):
    messagebox.showinfo(message="Parece que no estás conectado a Internet, sin el, esta aplicacion no funcionará", title="Error de red")


app.mainloop()