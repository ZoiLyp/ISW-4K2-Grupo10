from visitante import Visitante


class Actividad:
    def __init__(self, nombre, cupos_por_horario, requiere_talle=False):
        if not isinstance(cupos_por_horario, dict):
            raise ValueError("cupos_por_horario debe ser un diccionario")
        if not all(isinstance(dia, str) and isinstance(horarios, dict) for dia, horarios in cupos_por_horario.items()):
            raise ValueError("cupos_por_horario debe tener dias como claves y diccionarios de horarios como valores")
        if not all(isinstance(horario, str) and isinstance(cupo, int) and cupo >= 0 for horarios in cupos_por_horario.values() for horario, cupo in horarios.items()):
            raise ValueError("Los horarios deben ser cadenas y los cupos enteros no negativos")
        if not isinstance(nombre, str):
            raise ValueError("El nombre de la actividad debe ser una cadena")
        if not isinstance(requiere_talle, bool):
            raise ValueError("requiere_talle debe ser un valor booleano")
        self.nombre = nombre
        self.cupos_por_horario = cupos_por_horario
        self.requiere_talle = requiere_talle
        self.inscriptos_por_horario = {
                dia: {hora: [] for hora in horarios}
                for dia, horarios in cupos_por_horario.items()
            }

    # Verificamos que haya cupo disponible en el horario del dia elegido para la cantidad solicitada
    def tiene_cupo(self, dia, horario, cantidad):
        if dia not in self.cupos_por_horario:
            raise ValueError("El día no es válido para esta actividad")
        if horario not in self.cupos_por_horario[dia]:
            raise ValueError("El horario no es válido para este dia de esta actividad")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        return self.cupos_por_horario[dia][horario] > 0 and self.cupos_por_horario[dia][horario] >= cantidad
    
    
    # Restamos de los cupos disponibles la cantidad de personas inscritas
    def descontar_cupo(self, dia, horario, cantidad):
        if dia not in self.cupos_por_horario:
            raise ValueError("El día no es válido para esta actividad")
        if horario not in self.cupos_por_horario[dia]:
            raise ValueError("El horario no es válido para este dia de esta actividad")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        
        if self.tiene_cupo(dia, horario, cantidad):
            self.cupos_por_horario[dia][horario] -= cantidad
        else:
            raise ValueError("No hay cupos suficientes para descontar")
    
    
    def obtener_cupos_disponibles(self, dia, horario):
        if dia not in self.cupos_por_horario:
            raise ValueError("El día no es válido para esta actividad")
        if horario not in self.cupos_por_horario[dia]:
            raise ValueError("El horario no es válido para este dia de esta actividad")
        return self.cupos_por_horario[dia][horario]
    
    
    def agregar_inscripto(self, visitante, dia, horario):
        if not isinstance(visitante, Visitante):
            raise ValueError("El visitante debe ser una instancia de la clase Visitante")
        self.inscriptos_por_horario[dia][horario].append(visitante)