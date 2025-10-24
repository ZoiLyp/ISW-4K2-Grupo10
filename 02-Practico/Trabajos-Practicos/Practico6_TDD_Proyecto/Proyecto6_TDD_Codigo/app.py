from flask import Flask, render_template, request, jsonify
from gestor_actividades import GestorActividades
from visitante import Visitante 
from boundary import Boundary
import os
try:
    from persistence import Persistencia
except Exception:
    Persistencia = None

app = Flask(__name__)

# --- Lógica de Inicialización de Datos (Usando GestorActividades) ---
def cargar_gestor():
    """Inicializa y configura el GestorActividades con los datos del fixture."""
    return GestorActividades()

gestor_actividades = cargar_gestor()

# Configurar persistencia opcional: crea ./data/inscripciones.db
db_path = os.path.join(os.path.dirname(__file__), 'data', 'inscripciones.db')
print(f"🔧 Configurando persistencia en: {db_path}")
if Persistencia is not None:
    try:
        persist = Persistencia(db_path)
        gestor_actividades.set_persistencia(persist)
        print("✅ Persistencia configurada correctamente")
    except Exception as e:
        print(f"❌ Error configurando persistencia: {e}")
        # si falla la persistencia, continuamos sin ella
        pass
else:
    print("❌ Módulo Persistencia no disponible")


# Crea la capa boundary
boundary = Boundary(gestor_actividades)

# --- Fin de Lógica de Inicialización de Datos ---


def obtener_dias_unicos(actividades):
    """Extrae y devuelve una lista ordenada de días únicos disponibles en todas las actividades."""
    dias = set()
    for act in actividades:
        dias.update(act.cupos_por_horarios_por_dia.keys()) 
        
    return sorted(list(dias))


@app.route('/', methods=['GET'])
def index():
    """Muestra el formulario de inscripción."""
    dias_disponibles = boundary.obtener_dias_unicos()
    return render_template('inscripcion.html', 
                           actividades=boundary.get_actividades(),
                           dias_unicos=dias_disponibles)



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
    
    print(f"📝 Inscripción recibida: {len(visitantes)} visitantes para {nombre_actividad} el {dia} a las {horario}")
    print(f"🔍 Persistencia activa: {hasattr(gestor_actividades, 'persistencia') and gestor_actividades.persistencia is not None}")
    
    try:
        inscripciones = boundary.inscribir(visitantes, nombre_actividad, dia, horario, acepta)
        print(f"✅ Inscripción exitosa: {len(inscripciones)} inscripciones creadas")
        return jsonify({'status': 'ok', 'inscripciones': len(inscripciones), 'actividad': nombre_actividad})
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
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
        # 3. Convertir visitantes al formato esperado por boundary
        visitantes_data = []
        for v in visitantes:
            visitante_dict = {
                'nombre': v.nombre,
                'dni': v.dni,
                'edad': v.edad,
                'talle': getattr(v, 'talle', None)
            }
            visitantes_data.append(visitante_dict)
        
        # Llamar a boundary en lugar de gestor directamente
        boundary.inscribir(visitantes_data, nombre_actividad, dia, horario, acepta_terminos)
        resultado_mensaje = "Inscripción exitosa."
        
    except ValueError as e:
        resultado_mensaje = f"Error en la inscripción: {e}"
    except Exception as e: # Mejor manejo de errores generales
        resultado_mensaje = f"Error inesperado al procesar la inscripción: {e}"

    # 4. Redirigir o mostrar el resultado, asegurando que se pasen los días únicos de nuevo
    dias_disponibles = boundary.obtener_dias_unicos()
    return render_template('inscripcion.html', 
                           actividades=boundary.get_actividades(), 
                           dias_unicos=dias_disponibles, 
                           mensaje=resultado_mensaje)


if __name__ == '__main__':
    app.run(debug=True)