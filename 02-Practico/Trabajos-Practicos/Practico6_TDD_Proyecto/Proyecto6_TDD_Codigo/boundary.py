from gestor_actividades import GestorActividades
from visitante import Visitante
import datetime


class Boundary:
    def __init__(self, gestor: GestorActividades):
        self.gestor = gestor

    def get_actividades(self):
        """Devuelve lista de actividades serializables con sus días/horarios/cupos."""
        if not self.gestor.persistencia:
            return []
        return self.gestor.persistencia.load_activities()

    def obtener_dias_unicos(self):
        if not self.gestor.persistencia:
            return []
        actividades = self.gestor.persistencia.load_activities()
        dias = set()
        for act in actividades:
            cupos = act.get('cupos_por_horario', {})
            dias.update(cupos.keys())
        return sorted(list(dias))

    def obtener_horarios(self, nombre_actividad, dia):
        """Devuelve lista de horarios disponibles (con cupos) para una actividad y día."""
        if not self.gestor.persistencia:
            return {}
        actividades = self.gestor.persistencia.load_activities()
        actividad = next((act for act in actividades if act['nombre'] == nombre_actividad), None)
        if not actividad:
            return {}
        return actividad['cupos_por_horario'].get(dia, {})

    def obtener_cupos_disponibles(self, nombre_actividad, dia, horario):
        # Ahora el gestor maneja automáticamente persistencia vs memoria
        return self.gestor.obtener_cupos_disponibles(nombre_actividad, dia, horario)

    def inscribir(self, visitantes_data, nombre_actividad, dia, horario, acepta_terminos_condiciones):
        """Recibe una lista de dicts con datos de visitantes y realiza inscripción.

        visitantes_data: [{'nombre':..., 'dni':..., 'edad':..., 'talle':...}, ...]
        """
        visitantes = []
        print(f"🔍 Boundary recibió: {visitantes_data}")
        
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
        
        print(f"🔍 Visitantes convertidos a tuplas: {visitantes}")
        print(f"🔍 Gestor tiene persistencia: {hasattr(self.gestor, 'persistencia') and self.gestor.persistencia is not None}")
        
        # Delegar en el gestor (lanza ValueError en caso de error de validación)
        resultado = self.gestor.inscribir(visitantes, nombre_actividad, dia, horario, acepta_terminos_condiciones)
        print(f"✅ Boundary: inscripción completada, {len(resultado)} inscripciones")
        return resultado
