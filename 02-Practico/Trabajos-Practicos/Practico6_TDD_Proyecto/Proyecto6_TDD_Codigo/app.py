# # from flask import Flask, render_template, request
# # from gestor_actividades import GestorActividades
# # from visitante import Visitante 
# # # Asumo que Actividad y GestorActividades están bien definidas.

# # app = Flask(__name__)

# # # --- Lógica de Inicialización de Datos (Usando GestorActividades) ---
# # def cargar_gestor():
# #     """Inicializa y configura el GestorActividades con los datos del fixture."""
# #     gestor = GestorActividades()
# #     # Usamos la nueva estructura: cupos_por_horarios_por_dia
# #     gestor.agregar_actividad("Tirolesa", cupos_por_horarios_por_dia={"20251109":{"10:00": 2, "14:00": 1}, "20251110":{"10:00":5, "14:00":7}}, requiere_talle=True)
# #     gestor.agregar_actividad("Safari", cupos_por_horarios_por_dia={"20251109":{"09:00": 3}}, requiere_talle=False)
# #     gestor.agregar_actividad("Palestra", cupos_por_horarios_por_dia={"20251109":{"15:00": 0}, "20251110":{"15:00": 3}}, requiere_talle=True)
# #     gestor.agregar_actividad("Jardinería", cupos_por_horarios_por_dia={"20251109":{"11:00": 2}}, requiere_talle=False)
# #     return gestor

# # gestor_actividades = cargar_gestor()
# # # --- Fin de Lógica de Inicialización de Datos ---


# # @app.route('/', methods=['GET'])
# # def index():
# #     """Muestra el formulario de inscripción."""
# #     # Pasar la lista de actividades del gestor al template
# #     return render_template('inscripcion.html', actividades=gestor_actividades.actividades)


# # @app.route('/inscribir', methods=['POST'])
# # def inscribir():
# #     """Procesa los datos del formulario de inscripción."""
    
# #     # 1. Obtener datos de la Actividad
# #     nombre_actividad = request.form.get('actividad')
# #     dia = request.form.get('dia')              # <-- Nuevo campo
# #     horario = request.form.get('horario')      # <-- Nuevo campo
# #     cantidad_personas = int(request.form.get('cantidad_personas', 1)) # Default 1
# #     acepta_terminos = 'acepta_terminos' in request.form
    
# #     # 2. Obtener datos del Visitante principal (simplificado a un solo visitante)
# #     # NOTA: En tus tests estás usando una lista de objetos Visitante. 
# #     # Aquí creamos UN solo visitante y usamos 'cantidad_personas' para el cupo.
# #     nombre = request.form.get('nombre')
# #     dni = request.form.get('dni')
# #     edad = int(request.form.get('edad', 0))
# #     talle_vestimenta = request.form.get('talle')
    
# #     # Crea el visitante principal
# #     visitante_principal = Visitante(nombre, dni, edad, talle=talle_vestimenta)
    
# #     # Crea la lista de visitantes para la función inscribir. 
# #     # Asumimos que todos los visitantes son iguales para efectos de simplicidad del formulario.
# #     # Si 'cantidad_personas' es 3, creamos una lista con 3 objetos Visitante.
# #     visitantes = [visitante_principal] * cantidad_personas 
    
# #     resultado_mensaje = ""
    
# #     try:
# #         # 3. Llamar a tu lógica de negocio
# #         gestor_actividades.inscribir(
# #             visitantes, 
# #             nombre_actividad, 
# #             dia, 
# #             horario, 
# #             acepta_terminos_condiciones=acepta_terminos
# #         )
# #         resultado_mensaje = "Inscripción exitosa."
        
# #     except ValueError as e:
# #         # Captura las excepciones de validación (como falta de cupo o talle)
# #         resultado_mensaje = f"Error en la inscripción: {e}"
# #     except Exception:
# #         # Captura cualquier otro error inesperado
# #         resultado_mensaje = "Error inesperado al procesar la inscripción."


# #     # 4. Redirigir o mostrar el resultado
# #     return render_template('inscripcion.html', 
# #                            actividades=gestor_actividades.actividades, 
# #                            mensaje=resultado_mensaje)


# # if __name__ == '__main__':
# #     # Esto asegura que la aplicación se ejecute en modo debug, que es útil para desarrollo
# #     app.run(debug=True)
# # Archivo: app.py (Modificado)

# from flask import Flask, render_template, request
# from gestor_actividades import GestorActividades
# from visitante import Visitante 
# # Asumo que Actividad y GestorActividades están bien definidas.

# app = Flask(__name__)

# # --- Lógica de Inicialización de Datos (Usando GestorActividades) ---
# def cargar_gestor():
#     """Inicializa y configura el GestorActividades con los datos del fixture."""
#     gestor = GestorActividades()
#     # Usamos la nueva estructura: cupos_por_horarios_por_dia
#     gestor.agregar_actividad("Tirolesa", cupos_por_horarios_por_dia={"20251109":{"10:00": 2, "14:00": 1}, "20251110":{"10:00":5, "14:00":7}}, requiere_talle=True)
#     gestor.agregar_actividad("Safari", cupos_por_horarios_por_dia={"20251109":{"09:00": 3}}, requiere_talle=False)
#     gestor.agregar_actividad("Palestra", cupos_por_horarios_por_dia={"20251109":{"15:00": 0}, "20251110":{"15:00": 3}}, requiere_talle=True)
#     gestor.agregar_actividad("Jardinería", cupos_por_horarios_por_dia={"20251109":{"11:00": 2}}, requiere_talle=False)
#     return gestor

# gestor_actividades = cargar_gestor()
# # --- Fin de Lógica de Inicialización de Datos ---


# def obtener_dias_unicos(actividades):
#     """Extrae y devuelve una lista ordenada de días únicos disponibles en todas las actividades."""
#     dias = set()
#     for act in actividades:
#         dias.update(act.cupos_por_horarios_por_dia.keys())
#     return sorted(list(dias))


# @app.route('/', methods=['GET'])
# def index():
#     """Muestra el formulario de inscripción."""
#     dias_disponibles = obtener_dias_unicos(gestor_actividades.actividades)
#     return render_template('inscripcion.html', 
#                            actividades=gestor_actividades.actividades,
#                            dias_unicos=dias_disponibles) # <-- Nuevo parámetro


# @app.route('/inscribir', methods=['POST'])
# def inscribir():
#     """Procesa los datos del formulario de inscripción."""
    
#     # 1. Obtener datos de la Actividad
#     nombre_actividad = request.form.get('actividad')
#     dia = request.form.get('dia')
#     horario = request.form.get('horario')
#     cantidad_personas = int(request.form.get('cantidad_personas', 1))
#     acepta_terminos = 'acepta_terminos' in request.form
    
#     # 2. Obtener datos del Visitante principal
#     nombre = request.form.get('nombre')
#     dni = request.form.get('dni')
#     edad = int(request.form.get('edad', 0))
#     talle_vestimenta = request.form.get('talle')
    
#     visitante_principal = Visitante(nombre, dni, edad, talle=talle_vestimenta)
#     visitantes = [visitante_principal] * cantidad_personas 
    
#     resultado_mensaje = ""
    
#     try:
#         # 3. Llamar a tu lógica de negocio
#         gestor_actividades.inscribir(
#             visitantes, 
#             nombre_actividad, 
#             dia, 
#             horario, 
#             acepta_terminos_condiciones=acepta_terminos
#         )
#         resultado_mensaje = "Inscripción exitosa."
        
#     except ValueError as e:
#         resultado_mensaje = f"Error en la inscripción: {e}"
#     except Exception:
#         resultado_mensaje = "Error inesperado al procesar la inscripción."

#     # 4. Redirigir o mostrar el resultado, asegurando que se pasen los días únicos de nuevo
#     dias_disponibles = obtener_dias_unicos(gestor_actividades.actividades)
#     return render_template('inscripcion.html', 
#                            actividades=gestor_actividades.actividades, 
#                            dias_unicos=dias_disponibles, # <-- Parámetro añadido
#                            mensaje=resultado_mensaje)


# if __name__ == '__main__':
#     app.run(debug=True)

# Archivo: app.py (CORREGIDO)

from flask import Flask, render_template, request, jsonify
from gestor_actividades import GestorActividades
from visitante import Visitante 
from boundary import Boundary

app = Flask(__name__)

# --- Lógica de Inicialización de Datos (Usando GestorActividades) ---
def cargar_gestor():
    """Inicializa y configura el GestorActividades con los datos del fixture."""
    gestor = GestorActividades()
    # Usamos la nueva estructura: cupos_por_horarios_por_dia
    gestor.agregar_actividad("Tirolesa", cupos_por_horarios_por_dia={"20251109":{"10:00": 2, "14:00": 1}, "20251110":{"10:00":5, "14:00":7}}, requiere_talle=True)
    gestor.agregar_actividad("Safari", cupos_por_horarios_por_dia={"20251109":{"09:00": 3}}, requiere_talle=False)
    gestor.agregar_actividad("Palestra", cupos_por_horarios_por_dia={"20251109":{"15:00": 0}, "20251110":{"15:00": 3}}, requiere_talle=True)
    gestor.agregar_actividad("Jardinería", cupos_por_horarios_por_dia={"20251109":{"11:00": 2}}, requiere_talle=False)
    return gestor

gestor_actividades = cargar_gestor()
boundary = Boundary(gestor_actividades)
# --- Fin de Lógica de Inicialización de Datos ---


def obtener_dias_unicos(actividades):
    """Extrae y devuelve una lista ordenada de días únicos disponibles en todas las actividades."""
    dias = set()
    for act in actividades:
        # Aquí se usa el nombre de propiedad correcto, que es `cupos_por_horarios_por_dia`
        # si lo definiste como atributo de Actividad, o asumo que es accesible.
        # En tu Gestor lo definiste como 'cupos_por_horarios_por_dia', 
        # pero si tu clase Actividad lo almacena como 'cupos_por_horario', usa ese.
        # Basándonos en tu fixture, usaremos el nombre del atributo interno: cupos_por_horarios_por_dia (o similar)
        # Asumiendo que el atributo en la clase Actividad se llama 'cupos_por_horario'
        # ¡IMPORTANTE!: Revisa el nombre del atributo real en tu clase Actividad.
        # Basado en tu Gestor, vamos a asumir que la Actividad tiene el atributo 'cupos_por_horario'
        # o que usa el nombre del argumento de entrada, que es cupos_por_horarios_por_dia.
        # Si la clase Actividad almacena con el nombre de cupos_por_horarios_por_dia:
        dias.update(act.cupos_por_horarios_por_dia.keys()) 
        
    return sorted(list(dias))


@app.route('/', methods=['GET'])
def index():
    """Muestra el formulario de inscripción."""
    dias_disponibles = boundary.obtener_dias_unicos()
    return render_template('inscripcion.html', 
                           actividades=boundary.get_actividades(),
                           dias_unicos=dias_disponibles) # <--- CORREGIDO: SE PASA dias_unicos AQUÍ



@app.route('/api/horarios', methods=['GET'])
def api_horarios():
    nombre = request.args.get('actividad')
    dia = request.args.get('dia')
    if not nombre or not dia:
        return jsonify({'error': 'actividad y dia son requeridos'}), 400
    horarios = boundary.obtener_horarios(nombre, dia)
    return jsonify({'horarios': horarios})


@app.route('/api/cupos', methods=['GET'])
def api_cupos():
    nombre = request.args.get('actividad')
    dia = request.args.get('dia')
    horario = request.args.get('horario')
    if not nombre or not dia or not horario:
        return jsonify({'error': 'actividad, dia y horario son requeridos'}), 400
    try:
        cupos = boundary.obtener_cupos_disponibles(nombre, dia, horario)
        return jsonify({'cupos': cupos})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/inscribir', methods=['POST'])
def api_inscribir():
    payload = request.json or {}
    nombre_actividad = payload.get('actividad')
    dia = payload.get('dia')
    horario = payload.get('horario')
    visitantes = payload.get('visitantes', [])
    acepta = payload.get('acepta_terminos', False)
    try:
        inscripciones = boundary.inscribir(visitantes, nombre_actividad, dia, horario, acepta)
        return jsonify({'status': 'ok', 'inscripciones': len(inscripciones), 'actividad': nombre_actividad})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error inesperado: {e}'}), 500


@app.route('/inscribir', methods=['POST'])
def inscribir():
    """Procesa los datos del formulario de inscripción."""
    
    # 1. Obtener datos de la Actividad
    nombre_actividad = request.form.get('actividad')
    dia = request.form.get('dia')
    horario = request.form.get('horario')
    cantidad_personas = int(request.form.get('cantidad_personas', 1))
    acepta_terminos = 'acepta_terminos' in request.form
    
    # 2. Obtener datos del Visitante principal
    nombre = request.form.get('nombre')
    dni = request.form.get('dni')
    edad = int(request.form.get('edad', 0))
    talle_vestimenta = request.form.get('talle')
    
    visitante_principal = Visitante(nombre, dni, edad, talle=talle_vestimenta)
    visitantes = [visitante_principal] * cantidad_personas 
    
    resultado_mensaje = ""
    
    try:
        # 3. Llamar a tu lógica de negocio
        gestor_actividades.inscribir(
            visitantes, 
            nombre_actividad, 
            dia, 
            horario, 
            acepta_terminos_condiciones=acepta_terminos
        )
        resultado_mensaje = "Inscripción exitosa."
        
    except ValueError as e:
        resultado_mensaje = f"Error en la inscripción: {e}"
    except Exception as e: # Mejor manejo de errores generales
        resultado_mensaje = f"Error inesperado al procesar la inscripción: {e}"

    # 4. Redirigir o mostrar el resultado, asegurando que se pasen los días únicos de nuevo
    dias_disponibles = obtener_dias_unicos(gestor_actividades.actividades)
    return render_template('inscripcion.html', 
                           actividades=gestor_actividades.actividades, 
                           dias_unicos=dias_disponibles, 
                           mensaje=resultado_mensaje)


if __name__ == '__main__':
    app.run(debug=True)