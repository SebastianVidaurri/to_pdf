import re
import os
import sys
import treepoem
import tkinter as tk
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib.utils import ImageReader
from io import BytesIO

def extraer_form(linea):
    """
    Esta función devuelve el tipo de formulario en la línea dada.
    Busca coincidencias con la expresión regular 'FORMS=XXXX' o 
    el texto 'ETQIBM' y devuelve el valor correspondiente.
    
    Parámetros:
    linea (str): Una línea de texto en la que buscar el tipo de formulario.
    
    Retorna:
    str: El tipo de formulario encontrado o 'ETQIBM' si se encuentra en la línea.
    None: Si no se encuentra ningún tipo de formulario.
    """

    # Buscar coincidencia de 'FORMS=XXXX'
    match = re.search(r"FORMS=([\w\d]+)", linea)
    # Buscar si la línea contiene 'ETQIBM'
    match_dos = re.search(r"ETQIBM", linea)
    
    if match:
        return match.group(1)  # Devuelve el formulario encontrado
    elif match_dos:
        return 'ETQIBM'  # Devuelve 'ETQIBM' si no hay coincidencia con FORMS pero sí con 'ETQIBM'
    else:
        return None  # Ninguna coincidencia

def formularios(tipo='default'):
    '''
    Devuelve los tipo de formulario que existen, según la orientacion del pdf
    '''
    # Definimos los formularios directamente como conjuntos
    formularios_vertical = {'FM0006', 'FL0006', 'FL2007', 'FM0007', 'FM0004', 'FL0005', 'FM0308', 'FM0005', 'SIME18', 'FL002E', 'FM0308', 'FRBLAN'}
    formularios_horizontal = {'FL1000', 'FM0007'}
    formularios_etiqueta = {'ETQIBM'}
    formulario_default = {'DLFT00'}
    formulario_codbarra = {'CODBAR'}    
   # Dependiendo del argumento 'tipo', devolvemos el conjunto correspondiente
    if tipo == 'vertical':
        return formularios_vertical
    elif tipo == 'horizontal':
        return formularios_horizontal
    elif tipo == 'etiqueta':
        return formularios_etiqueta
    elif tipo == 'default':
        return formulario_default
    elif tipo == 'codbarra':
        return formulario_codbarra
    else:
        # Si no se pasa argumento, devolvemos la unión de todos los conjuntos
        #¿para que quiero la union de los conjuntos?
        return formularios_vertical | formularios_horizontal | formularios_etiqueta | formulario_default

def procesar_archivo_txt(nombre_archivo_txt, ruta):
    '''
    esta funcion toma los archivos TXT y los combierte en una lista

    arg:

        nombre_archivo_txt : es el nombre del archivo que queremos procesar
        config : el la configuracion para que podamos extrar

    '''

    name_arch = ruta + '\\' + nombre_archivo_txt + '.TXT'
    lista_pdf = []
    form_remanente = 'DLFT00' #ACÁ asígnamos el formulario por default
    
    #consultamos si es un archivo de codigo de barras
    if "SOC" in name_arch:
        cod_barra = True
    else:
        cod_barra = False

    with open(name_arch, "r", encoding="utf-8", errors="ignore") as file_IN:
        for linea in file_IN: #recorremos el file
            primer_caracter = linea[0] #separamos el primer caracter por que contiene el tipo de codificacion
            resto_cadena = linea[1:]
            form = extraer_form(resto_cadena) #extraemos el tipo de formulario


            if not linea.strip(): #si la linea esta vacia agrega un \n para que posteriormente sea identificado como un salto de linea
                lista_pdf.append('\n')
                continue

            if primer_caracter == '1':

                if form:
                    
                    if cod_barra:
                        form_remanente = 'CODBAR'
                        lista_pdf.append(form_remanente) #si detectamos un formulario y además estamos en un archivo de acuses, guardamos en la lista la configuracion de codigodebarras
                        continue

                    #lista_pdf.append(linea) #esto guarda \f\n en la lista que posteriormente se utilizara en la creacion del pdf de manera que si se detecta este codigo en la lista agrega un salto de paguina
                    lista_pdf.append(form) #si detectamos que hay un tipo de formulario lo guardamos en la lista para luego utilizalo como configuración
                    form_remanente = form #guardamos el formulario para utilizarlo en proximas iteraciones (si es necesario)
                    continue #seguimos con la siguiente iteracion por que ya hicimos la tarea que necesitamos para esta linea
                
                if ('FIRST DATA' in resto_cadena) or ('PROG.' in resto_cadena) or ('NRO.' in resto_cadena):
                    lista_pdf.append(form_remanente) #guardo el TIPO de Formulario
                    lista_pdf.append(resto_cadena) #Guardo la linea 'FIRST DATA' o 'PROG.', esto por que generalmente despues de un 1 ya debemos comenzar a escribir el pdf  
                                
                elif not resto_cadena.strip(): #si el primer caracter es un uno y el resto de la cadena esta vacia agregamos el tipo de formulario remanente para generar una nueva paguina
                    #lista_pdf.append(linea) #agregamos el salto de paguina
                    lista_pdf.append(form_remanente)
                    continue

                elif 'DJDE' in resto_cadena: #SI encontramos DJDE sin el formulario es por que termino la linea
                    form_remanente = 'DLFT00' #Si es el final del formulario guardamos 
                    continue #es más que nada para evitar el NEXT que se encuentra en el ELSE

                else:
                    next_line = next(file_IN) #lectura de la proxima linea 
                    #si la linea que sigue contiene la palara firsdata entonces que guarde en la variable formato la configuracion horizontal
                    if 'FIRST DATA' in next_line:
                        #lista_pdf.append(linea) #agregamos el salto de pagina
                        lista_pdf.append(form_remanente)

                    else:                   
                        lista_pdf.append('???????????????????????????????????????????????????????????????') #TODO: es solo una prueba por lo cual hay que quitar esta linea

            elif primer_caracter == '+':
                continue #si encontramos un signo + saltamos la iteracion para no guardar nada

            elif primer_caracter == '2': #si el primer caracter es igual a 2 es por que hay un codigo de para hacer la barra
                lista_pdf.append(resto_cadena.rstrip())

            elif primer_caracter == ' ' or primer_caracter == '0': #si el primer caracter esta vacio o es un cero es probable que se tenga que guardar la linea, salvo que exista un DJDE
                if 'DJDE' in resto_cadena: #si vemos DJDE en la linea no guardamos nada
                    continue
                lista_pdf.append(resto_cadena) #GUARDAMOS LA LINEA

    return lista_pdf

def asigna_estilo_paguina(form):
    '''
    Esta función recibe el tipo de formulario y devuelve la configuración correspondiente.
    '''
    # Definición de las distintas configuraciones de página.
    # Cada configuración es un diccionario que contiene todos los parámetros.
    configuraciones = {
        'default': {
            'orientacion': landscape(letter) , 'marco': False, 'base': None, 'altura': None, 
            'grosor_linea': None, 'x_marco': None, 'y_marco': None, 'y': 590, 'font_name': 'Courier', 
            'tamaño_letra': 7, 'x_offset': -85, 'limite': 70, 'interlineado' : 8,'name_config' : 'default',
            'marca_agua' : False, 'cod_barra' : False
        },
        'etiqueta': {
            'orientacion': portrait(letter), 'marco': False, 'base': None, 'altura': None, 
            'grosor_linea': None, 'x_marco': None, 'y_marco': None, 'y': 785, 'font_name': 'Courier', 
            'tamaño_letra': 9, 'x_offset': -95, 'limite': 95, 'interlineado' : 9.3,'name_config' : 'etiqueta',
            'marca_agua' : False, 'cod_barra' : False
        },
        'vertical': {
            'orientacion': portrait(letter), 'marco': True, 'base': 584, 'altura': 749, 
            'grosor_linea': 1, 'x_marco': 13.0, 'y_marco': 26.0, 'y': 750, 'font_name': 'Courier-Bold', 
            'tamaño_letra': 7, 'x_offset': -75, 'limite': 90, 'interlineado' : 8,'name_config' : 'vertical',
            'marca_agua' : True, 'cod_barra' : False        
        },
        'horizontal': {
            'orientacion': landscape(letter), 'marco': True, 'base': 760, 'altura': 584, 
            'grosor_linea': 1, 'x_marco': 13.0, 'y_marco': 13.0, 'y': 590, 'font_name': 'Courier-Bold', 
            'tamaño_letra': 7, 'x_offset': -85, 'limite': 70, 'interlineado' : 8 ,'name_config' : 'horizontal',
            'marca_agua' : True, 'cod_barra' : False
        },
        'codbarra': {
            'orientacion': portrait(letter), 'marco': True, 'base': 584, 'altura': 749, 
            'grosor_linea': 1, 'x_marco': 13.0, 'y_marco': 26.0, 'y': 750, 'font_name': 'Courier-Bold', 
            'tamaño_letra': 8, 'x_offset': -85, 'limite': 70, 'interlineado' : 8 ,'name_config' : 'horizontal',
            'marca_agua' : False, 'cod_barra' : True, 
        }
    }
    
    # Listas de formularios que pertenecen a cada configuración.
    formularios_vertical = formularios('vertical')
    formularios_horizontal = formularios('horizontal')
    formularios_etiqueta = formularios('etiqueta')
    formulario_default =  formularios('default')
    formulario_codbarra = formularios('codbarra')

    # Verifica si el formulario pertenece a la lista de formularios horizontales, verticales o de etiquetas.
    # Devuelve la configuración correspondiente según el tipo de formulario.
    if form in formularios_horizontal:
        return configuraciones['horizontal']  # Configuración HORIZONTAL
    elif form in formularios_vertical:
        return configuraciones['vertical']    # Configuración VERTICAL
    elif form in formularios_etiqueta:
        return configuraciones['etiqueta']    # Configuración ETIQUETA
    elif form in formulario_default:
        return configuraciones['default']     # Configuración DEFAULT (por defecto)
    elif form in formulario_codbarra:
        return configuraciones['codbarra']     # Configuración para los codigos de barras
    else:
        return None     # si no existe la configuracíon

def crear_pdf(listapdf, nombre_archivo, ruta):

    
    name_arch = ruta + '\\' + nombre_archivo.rstrip('.TXT') + '.PDF' #Nobre del pdf que vamos a crear
    c = canvas.Canvas(name_arch) #instanciamos el objeto c omo canvas
    cont = 1 #se utilizara para controlar la cantidad de lineas que se deben escribir en una hoja, dependera de la limite_lineas que se configura según la orientacion de la hoja
    config_pag = asigna_estilo_paguina('DLFT00')
    limite_lineas = 70 #INICIALIZAMOS la variable a 70 para que puesa pasar el proximo if

    for linea in listapdf: #recorremos la lista, cada iteracion representa una linea del archivo
        
        valida_form = asigna_estilo_paguina(linea) #usaremos esta variable solamente para saber si encontramos un valor correspondiente a un formulario - ES UNA VARIABLE muy volatil

        if (valida_form or cont == limite_lineas): #Si en la lista hay un valor correspondiente a una configuracion de un formulario y además no sobrepasamos el limite de las lineas que se deben escribir en el PDF

            if valida_form: #con este if me aseguro de guardar la configuracion de paguina, es necesario por que al poner el un OR en el if anterior no tenemos la seguridad de que estemos guardando una condiguracion
                config_pag = valida_form #si efectivamente estamos ante el valor de un formulario vamos a guardar dicho valor para no perderlo
            
            if cont > 0: #para no agregar ninguna paguina pdf si no 
                c.showPage() #creamos la una paguina nueva en el pdf
                c.setPageSize( config_pag['orientacion']) #configura las dimensiones de la hoja pdf
                c.setFont(config_pag ['font_name'], config_pag ['tamaño_letra']) #Seteamos en tipo de letra y el tamaño según la configuración
                cont = 0 #Inicializamos el contador de lineas que controla el limite de lineas que devemos escribir en el PDF
                limite_lineas = config_pag['limite'] #Configuramos ely limite de lineas que vamos a escribir según la configuracion que seleccionamos
                y = config_pag['y'] #configuracíon de la coodenada 'y'

            if config_pag['marco']: #El marco solo si esta habilito
                c.rect(config_pag['x_marco'], config_pag['y_marco'], config_pag['base'], config_pag['altura'], stroke=1) #agregamos el marco

            if config_pag['marca_agua']: #agrega Marca de agua solo si esta habilitada
                agregar_marca_de_agua(c, config_pag['name_config']) #agregamos la marca de agua
        
        else:
            if config_pag is None:
                config_pag = asigna_estilo_paguina('DLFT00') #si no encontramos una configuracion asignamos por default
            
            if '<' in linea and '>' in linea: #Si detectamos estos signos es por que estamos en presencia de un codigo de barras
                num_tj =  decoder(linea.strip('<>')) #decodificamos el codigo WwnN y lo guardamos

                incrusta_barcode(c, num_tj, config_pag['x_offset'] + 450, y - 10) #incrustamos el codigo de barras
            else:
                c.drawString(100 + config_pag['x_offset'], y, linea.rstrip()) #ESCRIBE la linea en x e y, sin espacion vacios
                y -= config_pag['interlineado'] #ES lo cantidad que debemos bajar respecto el eje 'y' (sería el interlineado)
                cont += 1
    c.save()

def incrusta_barcode (c, codigo, coordx, coordy):
    '''
    Genera un codigo de barras y lo incruta en el pdf
    formato del cogido de barras: interleaved 2 to 5

    argumentos:
        c: objeto camvas
        codigo: numero que representara el codigo de barras
        coordx coordy: coordenadas x e y
    
    '''
    barcode = treepoem.generate_barcode(
        barcode_type="interleaved2of5",
        data=codigo
    )

    # Crear un flujo en memoria para almacenar la imagen
    image_stream = BytesIO()
    barcode.convert("L").save(image_stream, format="PNG")
    image_stream.seek(0)  # Volver al inicio del flujo

    # Usar ImageReader para leer la imagen desde el flujo
    barcode_image = ImageReader(image_stream)

    # Dibujar la imagen en el PDF
    c.drawImage(barcode_image, x=coordx, y=coordy, width=150, height=30)

    # Liberar manualmente el flujo en memoria
    image_stream.close()

def decoder(codigo):
    '''
    Decodifica el codigo WwNnn en un numero entero
    
    '''
    # Tabla de mapeo de 5 caracteres a dígitos
    cod = {
    'nnWWn': '00', 'NnwwN': '01', 'nNwwN': '02', 'NNwwn': '03', 'nnWwN': '04',
    'NnWwn': '05', 'nNWwn': '06', 'nnwWN': '07', 'NnwWn': '08', 'nNwWn': '09',
    'wnNNw': '10', 'WnnnW': '11', 'wNnnW': '12', 'WNnnw': '13', 'wnNnW': '14',
    'WnNnw': '15', 'wNNnw': '16', 'wnnNW': '17', 'WnnNw': '18', 'wNnNw': '19',
    'nwNNw': '20', 'NwnnW': '21', 'nWnnW': '22', 'NWnnw': '23', 'nwNnW': '24',
    'NwNnw': '25', 'nWNnw': '26', 'nwnNW': '27', 'NwnNw': '28', 'nWnNw': '29',
    'wwNNn': '30', 'WwnnN': '31', 'wWnnN': '32', 'WWnnn': '33', 'wwNnN': '34',
    'WwNnn': '35', 'wWNnn': '36', 'wwnNN': '37', 'WwnNn': '38', 'wWnNn': '39',
    'nnWNw': '40', 'NnwnW': '41', 'nNwnW': '42', 'NNwnw': '43', 'nnWnW': '44',
    'NnWnw': '45', 'nNWnw': '46', 'nnwNW': '47', 'NnwNw': '48', 'nNwNw': '49',
    'wnWNn': '50', 'WnwnN': '51', 'wNwnN': '52', 'WNwnn': '53', 'wnWnN': '54',
    'WnWnn': '55', 'wNWnn': '56', 'wnwNN': '57', 'WnwNn': '58', 'wNwNn': '59',
    'nwWNn': '60', 'NwwnN': '61', 'nWwnN': '62', 'NWwnn': '63', 'nwWnN': '64',
    'NwWnn': '65', 'nWWnn': '66', 'nwwNN': '67', 'NwwNn': '68', 'nWwNn': '69',
    'nnNWw': '70', 'NnnwW': '71', 'nNnwW': '72', 'NNnww': '73', 'nnNwW': '74',
    'NnNww': '75', 'nNNww': '76', 'nnnWW': '77', 'NnnWw': '78', 'nNnWw': '79',
    'wnNWn': '80', 'WnnwN': '81', 'wNnwN': '82', 'WNnwn': '83', 'wnNwN': '84',
    'WnNwn': '85', 'wNNwn': '86', 'wnnWN': '87', 'WnnWn': '88', 'wNnWn': '89',
    'nwNWn': '90', 'NwnwN': '91', 'nWnwN': '92', 'NWnwn': '93', 'nwNwN': '94',
    'NwNwn': '95', 'nWNwn': '96', 'nwnWN': '97', 'NwnWn': '98', 'nWnWn': '99'
}


    tarjeta_numero = ""

    for i in range(0, len(codigo), 5):
        key = codigo[i: i + 5]
        tarjeta_numero += cod[key]

    return tarjeta_numero

def agregar_marca_de_agua(c, orientacion): #c es el objeto camvas, es el pdf
    '''
        Agrega el logo de la compania y lo acomoda según la orientacion del pdf

        parametros:
            c - objeto Canvas
            orientacion:
                horizontal
                vertical
    '''

    logo_path = 'agua.png'

    if orientacion == 'vertical':
        c.drawImage(logo_path, 200, 400)
        
    elif orientacion == 'horizontal':
        c.drawImage(logo_path, 300, 350)

def leer_config(ruta_archivo):
    '''
    Lee la configuracion del programa
    El txt debe contener todos los campos utilizados
 
    config['IN']: ruta de entrada
    config['out']: ruta de salida
    '''
    config = {}
    try:
        with open(ruta_archivo, 'r') as archivo:
            lineas = archivo.readlines()
            #ruta IN
            config['IN'] = lineas[0].strip()
            config['OUT'] = lineas[1].strip()
    except FileNotFoundError:
        print(f"El archivo '{ruta_archivo}' no se encontró.")
    except IOError:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
    return config
 
def lista_nombres_archivos (ruta_carpeta):
    '''
    devuelve una lista con los nombres de los archivos existentes en una carpeta especifica
    '''
    try:
        # Lista para almacenar nombres de archivos
        lista_de_nombres = []
        # Iterar sobre los archivos en la carpeta
        for archivo in os.listdir(ruta_carpeta):
            # Verificar si es un archivo .txt
            if archivo.endswith('.TXT') or archivo.endswith('.PDF') or archivo.endswith('.txt'):
                lista_de_nombres.append(archivo[:-4])

            else:
                lista_de_nombres.append(archivo)
        # Devolver la lista de nombres de archivos
        return lista_de_nombres
    except FileNotFoundError:
        print(f"La carpeta '{ruta_carpeta}' no se encontró.")
        return []
    except IOError:
        print(f"No se pudo leer la carpeta '{ruta_carpeta}'.")
        return []
 
def file_sin_procesar(ruta_in, ruta_out):
    '''
    devuelve los elementos de lista_in menos lista_out,
    se utilizara para obtener la lista de los elementos que aún no estan procesados
    '''
    try:
        #obtenemos las lista de los archivos que estan en las rutas de entrada y salida
 
        #TO_DO: seria mejor que la lista de salida las lea de un archivo que contenga el historial de los archivos procesados
        lista_in = lista_nombres_archivos(ruta_in)
        lista_out = lista_nombres_archivos(ruta_out)

        # Convertir ambas listas a conjuntos para realizar la diferencia
        set_in = set(lista_in)
        set_out = set(lista_out)
        # Obtener los archivos que están en lista_in pero no en lista_out
        archivos_faltantes = set_in - set_out
        # Devolver la lista de archivos faltantes
        return list(archivos_faltantes)

    except TypeError as e:
        print("Error:", e)
        return []

def crea_archivos (lista_sin_procesar, config): #lista de nombres de los archivos sin procesar
    '''
    Recibe la lista de los nombres de los archivos y la ruta donde entran y salen los archivos
    Llama a las funciones más importantes
    '''
    #funcion raiz que llama a las funciones más importantes
    
    sin_procesar = lista_sin_procesar
    nombre_acuses = ['SOCBLACK', 'SOCIOPRT']

    for nombre_archivo in sin_procesar: #recorro la lista de nombres

        lista_pdf = procesar_archivo_txt(nombre_archivo, config['IN']) #procesamos el txt para combertirlo en una lista    

        if any(nombre in nombre_archivo for nombre in nombre_acuses): #verifico si es un archivo de acuses
            break
        
        lista_pdf = procesar_archivo_txt(nombre_archivo, config['IN']) #procesamos el txt para combertirlo en una lista    
        crear_pdf(lista_pdf, nombre_archivo, config['OUT']) #le paso el archivo para procesar y el nombre del archivo de salida

    lista_pdf.clear()
    
def ajustar_tamano_fondo(ventana, fondo_label, imagen_fondo):
    nueva_ancho = ventana.winfo_width()
    nueva_alto = ventana.winfo_height()
    imagen_redimensionada = imagen_fondo.resize((nueva_ancho, nueva_alto))
    nuevo_fondo = ImageTk.PhotoImage(imagen_redimensionada)
    fondo_label.configure(image=nuevo_fondo)
    fondo_label.image = nuevo_fondo  # Actualiza la referencia del objeto de la imagen

def cerrar_ventana(ventana):
    ventana.destroy()
    sys.exit()  # Termina la ejecución del programa

def crear_interfaz_usuario(nombre_archivos, ruta):
    '''
    Crea la interfaz del usuario

    '''

    ventana = tk.Tk()
    ventana.title("Misiones 2.3")
    ventana.iconbitmap("fiserv_logo-1-368x184.ico")
    ventana.geometry("500x250")  # Tamaño de la ventana

    fondo_path = 'fondo_fiserv.png'   # Reemplaza con la ruta correcta
    if os.path.exists(fondo_path):
        imagen_fondo = Image.open(fondo_path)
        fondo = ImageTk.PhotoImage(imagen_fondo)
        
        fondo_label = tk.Label(ventana, image=fondo)
        fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Enlazar el evento de redimensionamiento al ajuste del fondo
        ventana.bind("<Configure>", lambda e: ajustar_tamano_fondo(ventana, fondo_label, imagen_fondo))

    # Agregar el botón para seleccionar el archivo
    boton_seleccionar = tk.Button(ventana, text= "Procesar archivos",command = lambda: crea_archivos(nombre_archivos, ruta))
    boton_seleccionar.pack(pady=20)       
    
    # Enlazar el evento de cerrar ventana
    ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana))

    # Iniciar el bucle principal de la interfaz de usuario
    ventana.mainloop()



if __name__ == "__main__":

    config = leer_config('config.txt') #busca la configuracion donde se encuentra el script
    sin_procesar = file_sin_procesar(config['IN'], config['OUT']) #obtenemos la lista de los archivos sin procesar
    crear_interfaz_usuario(sin_procesar, config)
