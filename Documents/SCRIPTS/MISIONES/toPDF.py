from reportlab.lib.pagesizes import landscape, letter, portrait
from reportlab.pdfgen import canvas
import re


class GeneradorPDF:


    def __init__(self, archivo_txt, salida_pdf):
        self.archivo_txt = archivo_txt
        self.salida_pdf = salida_pdf
        self.form = self.config_por_defecto()
        self.c = canvas.Canvas(salida_pdf, pagesize=self.config_actual['page_size'])
        self.buffer = []  # Acumula líneas hasta que se decide dibujar
        self.pos_y = self.config_actual['start_y']

    def procesar(self):

        '''
        Procesa el archivo y generar el pdf

        '''
        with open(self.archivo_txt, 'r', encoding='utf-8') as f:


            #instanciamos el objeto texto
            textobject = self.c.beginText()

            for linea in f:
                
                cont = 0 #Inicializamos el contador de lineas
                primer_caracter = linea[0] #leemos el primer caracter
                cadena = linea[1:] #resto de la cadena

                if primer_caracter == '1': #el codigo uno representa novedades que se deben clasificar

                    if ('FIRST DATA' in cadena) or ('PROG.' in cadena) or ('NRO.' in cadena): #la linea comienza con alguno de estos string
                        
                        textobject.textLine(cadena) #guardo la linea
                        cont += 1 #queremos contar cuantas lineas hay en una hoja para saber cuando tenemos que saltar de paguina

                    elif not cadena.strip(): #un codigo 1 con un string vacio representa una hoja nueva
                        '''quizas debamomos guardar el tipo de estilo de hoja'''
                        #TODO
                        #guardamos el texto acumulado con el formato acumulado
                        #creamos una hoja nueva
                        pass
                
                    elif 'DJDE' in cadena: #un 1 con un DJDE es por que tiene la configuracion de la 
                        self.form = self.extraer_form(cadena) #extraemos el tipo de formulario
                                        
                    elif primer_caracter == '+':
                        continue #si encontramos un signo + saltamos la iteracion para no guardar nada
        
                    elif primer_caracter == '2': #si el primer caracter es igual a 2 es por que hay un codigo de para hacer la barra
                         #acá iria la funcion decoder y luego incrustar el codigo de barras
                        pass #borrar el pass

                    else:
                        next_line = next(f) #lectura de la proxima linea
                        if 'FIRST DATA' in next_line:
                            pass
                            #grabamos la hoja y abrimos una nueva

                elif primer_caracter == ' ' or primer_caracter == '0': 
                    if 'DJDE' in cadena: #si vemos DJDE en la linea no guardamos nada
                        continue

                    textobject.textLine(cadena) #guardamos la linea
                    cont += 1 #queremos contar cuantas lineas hay en una hoja para saber cuando tenemos que saltar de paguina
                
                #TODO
                #guardamos el texto acumulado con el formato acumulado
                #creamos una hoja nueva               
                #si el contador llega a su limite hay que crear una hoja nueva

        self.c.save()
    
    def extraer_form(linea):

        """Esta función devuelve el tipo de formulario en la línea dada.
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
        formularios_vertical = {'FM0006', 'FL0006', 'FL2007', 'FM0007', 'FM0004', 'FL0005', 'FM0308', 'FM0005', 'SIME18', 'FL002E', 'FM0308', 'FRBLAN'}
        formularios_horizontal = {'FL1000', 'FM0007'}
        formularios_etiqueta = {'ETQIBM'}
        formulario_default =  {'DLFT00'}
        formulario_codbarra = {'CODBAR'}

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
