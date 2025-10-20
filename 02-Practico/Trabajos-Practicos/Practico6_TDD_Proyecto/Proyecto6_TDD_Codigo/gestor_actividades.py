from inscripcion import Inscripcion
from actividad import Actividad
from visitante import Visitante
from inscripcion import Inscripcion
"""
def inscribirse_a_actividad(visitante, nombre_actividad, horario, cantidad_personas, acepta_terminos, actividades):
    actividad = next((act for act in actividades if act.nombre == nombre_actividad), None)                  # Buscamos la actividad por su nombre de la lista de actividades
    if not actividad:
        return "No se encontró la actividad solicitada"

    inscripcion = Inscripcion(visitante, actividad, horario, cantidad_personas, acepta_terminos)            # Creamos una instancia de Inscripcion

    error = inscripcion.validar()                                                      # Validamos la inscripción, si no hay errores confirmamos la misma
    if error:
        return error

    return inscripcion.confirmar()
"""

class GestorActividades:
    def __init__(self):
        self.actividades = []


    def agregar_actividad(self, nombre, cupos_por_horarios_por_dia, requiere_talle=False):
        try:
            actividad = Actividad(nombre, cupos_por_horarios_por_dia, requiere_talle)
            self.actividades.append(actividad)
            print(f"Actividad '{nombre}' agregada correctamente.")
        except ValueError as e:
            raise ValueError(f"No se pudo agregar la actividad: {e}")


    def obtener_cupos_disponibles(self, nombre_actividad, dia, horario):
        actividad = next((act for act in self.actividades if act.nombre == nombre_actividad), None)
        if not actividad:
            raise ValueError("No se encontró la actividad solicitada")
        return actividad.obtener_cupos_disponibles(dia, horario)


    # crea el visitante dependiendo de si tiene o no talle
    def crear_visitante(self, v):
        if len(v) == 4:
            return Visitante(v[0], v[1], v[2], v[3])
        else:
            return Visitante(v[0], v[1], v[2])
        
    
    def crear_inscripcion(self, visitante, nombre_actividad, dia, horario, acepta_terminos_condiciones):    
        return Inscripcion(visitante, nombre_actividad, dia, horario, acepta_terminos_condiciones)
            


    def inscribir(self, visitantes, nombre_actividad, dia, horario, acepta_terminos_condiciones):
        if not visitantes or len(visitantes) == 0:
            raise ValueError("Debe haber al menos un visitante para inscribirse")
        if not isinstance(acepta_terminos_condiciones, bool) or not acepta_terminos_condiciones:
            raise ValueError("Debe aceptar los términos y condiciones para inscribirse")
        if not isinstance(nombre_actividad, str) or not nombre_actividad:
            raise ValueError("El nombre de la actividad debe ser una cadena no vacía")
        if not isinstance(dia, str) or not dia:
            raise ValueError("El día debe ser una cadena no vacía")
        if not isinstance(horario, str) or not horario: 
            raise ValueError("El horario debe ser una cadena no vacía")

        actividad = next((act for act in self.actividades if act.nombre == nombre_actividad), None)
        
        if not actividad:
            raise ValueError("No se encontró la actividad solicitada")
        if dia not in actividad.cupos_por_horario or horario not in actividad.cupos_por_horario[dia]:
            raise ValueError("El día o el horario no son válidos para esta actividad")
        if not actividad.tiene_cupo(dia, horario, len(visitantes)):
            raise ValueError("No hay cupos suficientes para la cantidad de visitantes")
        
        inscripciones = []

        for v in visitantes:
            if actividad.requiere_talle and (len(v) < 4 or v[3] is None):
                raise ValueError("Esta actividad requiere que se indique la talla de ropa para todos los visitantes")
            try: 
                visitante = self.crear_visitante(v)
                actividad.agregar_inscripto(visitante, dia, horario)
                
                actividad.descontar_cupo(dia, horario, 1)
                
                inscripcion = self.crear_inscripcion(visitante, nombre_actividad, dia, horario, acepta_terminos_condiciones)
                
                inscripciones.append(inscripcion)
                
            except Exception as e:
                raise ValueError(f"No se pudo inscribir al visitante {v[0]}: {e}")
        
        return inscripciones