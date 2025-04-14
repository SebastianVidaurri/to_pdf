import re
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.pdfgen import canvas

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

def crea_pdf (name_arch, ):

    form_default = 'DLFT00' #este es un formulario default
    c = canvas.Canvas(name_arch) #instanciamos el objeto c omo canvas
    
    with open(name_arch, "r", encoding="utf-8", errors="ignore") as file_IN:
        
        #recorremos el archivo linea por linea
        for linea in file_IN:
            primer_caracter = linea[0]
            cadena = linea[1:]
            form = extraer_form (cadena) #extraemos el formulario, si no hay un formulario asigna none

            #if not linea.strip(): #si la linea esta vacia agrega un \n para que posteriormente sea identificado como un salto de linea
            #    lista_pdf.append('\n')
            #    continue

        if primer_caracter == '1':
        
            if form or cont == limite_lineas: #si tenemos un formulario o llegamos al limite de lineas por hoja
                
                c.showPage() #cerramos la paguina y abrimos una nueva
                #asignamos el estilo de paguina #TODO ¿se puede agregar el estilo de la paguina luego u antes de dibujar el pdf

                config_pag = asigna_estilo_paguina(form)
                c.setPageSize( config_pag['orientacion']) #configura las dimensiones de la hoja pdf
                c.setFont(config_pag ['font_name'], config_pag ['tamaño_letra']) #Seteamos en tipo de letra y el tamaño según la configuración
                cont = 0 #Inicializamos el contador de lineas
                limite_lineas = config_pag['limite'] #Configuramos ely limite de lineas que vamos a escribir según la configuracion que seleccionamos




                # if tenemos un codigo de barras
                # 
                # 
                # 

                # si el formulario no es un codigo de barras
            
            if ('FIRST DATA' in cadena) or ('PROG.' in cadena) or ('NRO.' in cadena): #si es un uno y la linea comienza con alguno de estos 
            # escribimos la linea 
                pass #eliminar este pass luego de rellenar el if

            elif not cadena.strip(): #si el primer caracter es un uno y el resto de la cadena tenemos que saber que tipo de formulario tenemos que configurar
                pass #borrar este pass
            
            elif 'DJDE' in cadena: #SI encontramos DJDE sin el formulario es por que termino la linea
                pass #borrar este pass

            else:
                next_line = next(file_IN) #leemos la sigiente linea
                #si la linea que sigue contiene la palara firsdata entonces que guarde en la variable formato la configuracion horizontal
                if 'FIRST DATA' in next_line:
                    pass #borrar este pass 
        
        elif primer_caracter == '+':
            pass #si encontramos un signo + saltamos la iteracion para no guardar nada
        
        elif primer_caracter == '2': #si el primer caracter es igual a 2 es por que hay un codigo de para hacer la barra
            #acá iria la funcion decoder y luego incrustar el codigo de barras
            pass #borrar el pass

        elif primer_caracter == ' ' or primer_caracter == '0': #si el primer caracter esta vacio o es un cero es probable que se tenga que guardar la linea, salvo que exista un DJDE
                if 'DJDE' in cadena: #si vemos DJDE en la linea no guardamos nada
                    pass

                #TODO GUARDAR LA LINEA ------------------------

        
