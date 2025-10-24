from inscripcion import Inscripcion
from actividad import Actividad
from visitante import Visitante
try:
    from persistence import Persistencia
except Exception:
    Persistencia = None


class GestorActividades:
    def __init__(self):
        self.actividades = []
        self.persistencia = None

    def set_persistencia(self, persistencia):
        """
        Configura el objeto de persistencia (por ejemplo, PersistenciaSQLite).
        """
        self.persistencia = persistencia





    def agregar_actividad(self, nombre, cupos_por_horarios_por_dia, requiere_talle=False):
        try:
            actividad = Actividad(nombre, cupos_por_horarios_por_dia, requiere_talle)
            self.actividades.append(actividad)
            if self.persistencia:
                self.persistencia.save_activity(actividad)
            print(f"Actividad '{nombre}' agregada correctamente.")
        except ValueError as e:
            raise ValueError(f"No se pudo agregar la actividad: {e}")


    def obtener_cupos_disponibles(self, nombre_actividad, dia, horario):
        # Usar siempre la persistencia si está disponible
        if self.persistencia:
            actividades_db = self.persistencia.load_activities()
            actividad = next((act for act in actividades_db if act['nombre'] == nombre_actividad), None)
            if not actividad:
                raise ValueError("No se encontró la actividad solicitada")
            try:
                return actividad['cupos_por_horario'][dia][horario]
            except KeyError:
                raise ValueError("El día o el horario no son válidos para esta actividad")
        
        # Fallback a memoria solo si no hay persistencia (para tests)
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
    
    def _descontar_cupos_bd(self, nombre_actividad, dia, horario, cantidad):
        """Descuenta cupos directamente en la base de datos."""
        if not self.persistencia:
            return
            
        # Obtener cupos actuales
        actividades_db = self.persistencia.load_activities()
        actividad_data = next((act for act in actividades_db if act['nombre'] == nombre_actividad), None)
        if not actividad_data:
            raise ValueError("No se encontró la actividad para descontar cupos")
            
        # Descontar cupos
        cupos_actuales = actividad_data['cupos_por_horario'][dia][horario]
        nuevos_cupos = cupos_actuales - cantidad
        
        if nuevos_cupos < 0:
            raise ValueError("No se pueden descontar más cupos de los disponibles")
            
        # Crear objeto temporal para actualizar en BD
        from actividad import Actividad
        actividad_temp = Actividad(
            nombre=actividad_data['nombre'],
            cupos_por_horario=actividad_data['cupos_por_horario'],
            requiere_talle=actividad_data.get('requiere_talle', False)
        )
        actividad_temp.cupos_por_horario[dia][horario] = nuevos_cupos
        
        # Actualizar en BD
        self.persistencia.update_activity_cupos(actividad_temp)
            


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

        # Usar persistencia si está disponible
        if self.persistencia:
            actividades_db = self.persistencia.load_activities()
            actividad_data = next((act for act in actividades_db if act['nombre'] == nombre_actividad), None)
            if not actividad_data:
                raise ValueError("No se encontró la actividad solicitada")
            
            # Verificar día y horario válidos
            if dia not in actividad_data['cupos_por_horario'] or horario not in actividad_data['cupos_por_horario'][dia]:
                raise ValueError("El día o el horario no son válidos para esta actividad")
            
            # Verificar cupos disponibles
            cupos_disponibles = actividad_data['cupos_por_horario'][dia][horario]
            if cupos_disponibles < len(visitantes):
                raise ValueError("No hay cupos suficientes para la cantidad de visitantes")
                
            requiere_talle = actividad_data.get('requiere_talle', False)
        else:
            # Fallback a memoria para tests
            actividad = next((act for act in self.actividades if act.nombre == nombre_actividad), None)
            if not actividad:
                raise ValueError("No se encontró la actividad solicitada")
            
            if dia not in actividad.cupos_por_horario or horario not in actividad.cupos_por_horario[dia]:
                raise ValueError("El día o el horario no son válidos para esta actividad")
            if not actividad.tiene_cupo(dia, horario, len(visitantes)):
                raise ValueError("No hay cupos suficientes para la cantidad de visitantes")
            
            requiere_talle = actividad.requiere_talle
        
        # Crear objetos visitante y validar tallas
        objetos_visitantes = []
        for v in visitantes:          
            # Si ya es un objeto Visitante, usarlo directamente
            if hasattr(v, 'nombre') and hasattr(v, 'dni'):
                visitante = v
                # Validar talle si es requerido
                if requiere_talle and (not hasattr(visitante, 'talle') or visitante.talle is None):
                    raise ValueError("Esta actividad requiere que se indique la talle de ropa para todos los visitantes")
                objetos_visitantes.append(visitante)
            else:
                # Es una tupla/lista, usar el método original
                if v[2] is None or (isinstance(v[2], str) and not v[2].isdigit()) or (isinstance(v[2], int) and v[2] < 0):
                    raise ValueError("La edad del visitante debe ser un número entero válido")  
                if requiere_talle and (len(v) < 4 or v[3] is None):
                    raise ValueError("Esta actividad requiere que se indique la talla de ropa para todos los visitantes")
                try: 
                    visitante = self.crear_visitante(v)
                    objetos_visitantes.append(visitante)
                except Exception as e:
                    raise ValueError(f"No se pudo crear el visitante {v[0] if len(v) > 0 else 'desconocido'}: {e}")
        
        # Crear inscripciones
        inscripciones = []
        
        # PRIMERO: Validar persistencia si está configurada (ANTES de modificar memoria)
        if self.persistencia:
            try:
                # Crear una inscripción representativa para validar
                inscripcion_grupal = self.crear_inscripcion(objetos_visitantes[0], nombre_actividad, dia, horario, acepta_terminos_condiciones)
                # Intentar guardar - esto validará DNIs duplicados
                self.persistencia.save_inscripcion(inscripcion_grupal, objetos_visitantes)
                # Si llegamos aquí, la persistencia fue exitosa
            except Exception as e:
                # Si la persistencia falla, lanzar error SIN modificar memoria
                raise ValueError(str(e))
        
        # SEGUNDO: Si la persistencia fue exitosa (o no hay persistencia), crear inscripciones y actualizar cupos
        try:
            # Crear inscripciones
            for visitante in objetos_visitantes:
                inscripcion = self.crear_inscripcion(visitante, nombre_actividad, dia, horario, acepta_terminos_condiciones)
                inscripciones.append(inscripcion)
            
            # Descontar cupos
            if self.persistencia:
                # Descontar directamente en la BD
                self._descontar_cupos_bd(nombre_actividad, dia, horario, len(visitantes))
            else:
                # Fallback a memoria para tests
                actividad = next((act for act in self.actividades if act.nombre == nombre_actividad), None)
                if actividad:
                    actividad.descontar_cupo(dia, horario, len(visitantes))
                
        except Exception as e:
            raise ValueError(f"Error en el proceso de inscripción: {e}")
        
        return inscripciones