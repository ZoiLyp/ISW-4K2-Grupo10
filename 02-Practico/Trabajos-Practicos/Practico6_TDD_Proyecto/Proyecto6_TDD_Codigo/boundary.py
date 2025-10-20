from gestor_actividades import GestorActividades
from visitante import Visitante
import datetime


class Boundary:
    """Boundary que actúa como capa entre la UI y GestorActividades.

    Expone datos en estructuras serializables y convierte datos de la UI
    a objetos de dominio antes de delegar en GestorActividades.
    """
    def __init__(self, gestor: GestorActividades):
        self.gestor = gestor

    def get_actividades(self):
        """Devuelve lista de actividades serializables con sus días/horarios/cupos."""
        actividades = []
        for act in self.gestor.actividades:
            cupos = getattr(act, 'cupos_por_horarios_por_dia', None) or getattr(act, 'cupos_por_horario', {})
            actividades.append({
                'nombre': act.nombre,
                'requiere_talle': getattr(act, 'requiere_talle', False),
                'cupos_por_horario': cupos
            })
        return actividades

    def obtener_dias_unicos(self):
        dias = set()
        for act in self.gestor.actividades:
            cupos = getattr(act, 'cupos_por_horarios_por_dia', None) or getattr(act, 'cupos_por_horario', {})
            dias.update(cupos.keys())
        return sorted(list(dias))

    def obtener_horarios(self, nombre_actividad, dia):
        """Devuelve lista de horarios disponibles (con cupos) para una actividad y día."""
        actividad = next((a for a in self.gestor.actividades if a.nombre == nombre_actividad), None)
        if not actividad:
            return []
        cupos = getattr(actividad, 'cupos_por_horarios_por_dia', None) or getattr(actividad, 'cupos_por_horario', {})
        return cupos.get(dia, {})

    def obtener_cupos_disponibles(self, nombre_actividad, dia, horario):
        return self.gestor.obtener_cupos_disponibles(nombre_actividad, dia, horario)

    def inscribir(self, visitantes_data, nombre_actividad, dia, horario, acepta_terminos_condiciones):
        """Recibe una lista de dicts con datos de visitantes y realiza inscripción.

        visitantes_data: [{'nombre':..., 'dni':..., 'edad':..., 'talle':...}, ...]
        """
        visitantes = []
        print(visitantes_data)
        for v in visitantes_data:
            # Validaciones mínimas locales
            nombre = v.get('nombre')
            dni = v.get('dni')
            edad = int(v.get('edad', 0)) if v.get('edad') not in (None, '') else 0
            talle = v.get('talle', None)
            
            # Si la actividad requiere talle, agregamos 4 elementos, sino 3
            if talle is not None and talle != '':
                visitantes.append((nombre, dni, edad, talle))
            else:
                visitantes.append((nombre, dni, edad))

        # Delegar en el gestor (lanza ValueError en caso de error de validación)
        return self.gestor.inscribir(visitantes, nombre_actividad, dia, horario, acepta_terminos_condiciones)
