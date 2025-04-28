from reportlab.lib.pagesizes import landscape, letter, portrait
from reportlab.pdfgen import canvas
import re


class GeneradorPDF:


    def __init__(self, archivo_txt, salida_pdf):
        self.archivo_txt = archivo_txt #Nombre del archivo txt que vamos a procesar
        self.salida_pdf = salida_pdf #Nombre del archivo del PDF convertido
        self.form = 'DLFT00' #asignamos un formulario tipo default
        self.config = self.estilo_paguina(self.form)
        self.c = canvas.Canvas(self.salida_pdf)
        self.textobject = None #Se establecera en configurar_paguina()
        self.cont = 0 #contador de líneas en la página

    def procesar(self):

        '''
        Procesa el archivo y genera el pdf
        '''
        
        with open(self.archivo_txt, 'r', encoding='utf-8') as f:

            #instanciamos el objeto texto
            self.textobject = self.c.beginText()

            for linea in f:
                
                primer_caracter = linea[0] #leemos el primer caracter
                cadena = linea[1:] #resto de la cadena

                if primer_caracter == '1': #el codigo uno representa novedades que se deben clasificar

                    if ('FIRST DATA' in cadena) or ('PROG.' in cadena) or ('NRO.' in cadena): #la linea comienza con alguno de estos string
                        self.textobject.textLine(cadena) #guardo la linea
                        cont += 1 #queremos contar cuantas lineas hay en una hoja para saber cuando tenemos que saltar de paguina

                    elif not cadena.strip(): #un codigo 1 con un string vacio representa una hoja nueva
                        self.config = self.estilo_paguina(self.form)
                        self.escribe_pdf(self.c, self.config, self.textobject)
                        self.c.showPage() #creamos una hoja nueva
                        self.cont = 0 #inicializamos nuevamente el contador
                        self.textobject = self.c.beginText() #inicializamos nuevamete el objeto texto


                    elif 'DJDE' in cadena: #un 1 con un DJDE es por que tiene la configuracion de la hoja
                        self.form = self.extraer_form(cadena) #extraemos el tipo de formulario
        
                    elif primer_caracter == '2': #si el primer caracter es igual a 2 es por que hay un codigo de para hacer la barra
                         #TODO: completar
                         #if '<' in linea and '>' in linea: #Si detectamos estos signos es por que estamos en presencia de un codigo de barras
                         #llamamos al decoder y guardamos el numero
                         #
                         #incrustar el codigo de barras
                        pass #borrar el pass

                    else:
                        try:
                            next_line = next(f) #lectura de la proxima linea
                        except StopIteration:
                            next_line = ''

                        if 'FIRST DATA' in next_line:
                            self.config = self.estilo_paguina(self.form)
                            self.escribe_pdf(self.c, self.config, self.textobject)
                            self.c.showPage() #creamos una hoja nueva
                            self.cont = 0 #inicializamos nuevamente el contador
                            self.textobject = self.c.beginText() 
                            
                        #grabamos la hoja y abrimos una nueva
                
                elif primer_caracter == '+':
                        continue #si encontramos un signo + saltamos la iteracion para no guardar nada

                elif primer_caracter == ' ' or primer_caracter == '0': 
                    if 'DJDE' in cadena: #si vemos DJDE en la linea no guardamos nada
                        continue
                    self.textobject.textLine(cadena) #guardamos la linea
                    cont += 1 #queremos contar cuantas lineas hay en una hoja para saber cuando tenemos que saltar de paguina

                if cont == self.config['limite']: #controla so llegamos a la cantidada de lineas permitidas por paguina
                    self.config = self.estilo_paguina(self.form)
                    self.escribe_pdf(self.c, self.config, self.textobject)
                    self.c.showPage() #creamos una hoja nueva
                    self.cont = 0 #inicializamos nuevamente el contador
                    self.textobject = self.c.beginText()
                    continue
                
            self.config = self.estilo_paguina(self.form)
            self.escribe_pdf(self.c, self.config, self.textobject)
            self.c.showPage() #creamos una hoja nueva
            self.cont = 0 #inicializamos nuevamente el contador
            self.textobject = self.c.beginText()
            
        self.c.save()
    
    def escribe_pdf (self, c, config, texto):
        """
        Configura y escribe el texto  a un pdf

        parametros:
            c: objeto canvas
            config: lista con los valores de configuración
            texto: el texto que de decea escribir en el pdf
        """
        #setear el tamaño de la paguina
        c.setPageSize(config['orientacion'])

        #set font
        c.setFont(config['font_name'], config['tamaño_letra'])

        #grabamos en texto en el pdf
        c.drawText(config['x_offset'], config['y'], texto)




    def extraer_form(self, linea):

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
        
def estilo_paguina(form ='DLFT00'):
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