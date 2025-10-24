import pytest
from gestor_actividades import GestorActividades


@pytest.fixture
def gestor():
    gestor = GestorActividades()
    gestor.agregar_actividad("Tirolesa", cupos_por_horarios_por_dia={"20251109":{"10:00": 2, "14:00": 1}, "20251110":{"10:00":5, "14:00":7}}, requiere_talle=True)
    gestor.agregar_actividad("Safari", cupos_por_horarios_por_dia={"20251109":{"09:00": 3}}, requiere_talle=False)
    gestor.agregar_actividad("Palestra", cupos_por_horarios_por_dia={"20251109":{"15:00": 0}, "20251110":{"15:00": 3}}, requiere_talle=True)
    gestor.agregar_actividad("Jardinería", cupos_por_horarios_por_dia={"20251109":{"11:00": 2}}, requiere_talle=False)
    return gestor


def test_inscripcion_exitosa_con_talle_con_cupo_ok(gestor):
    # Precondiciones + parametros(gestor)
    visitantes = [("Juan", "12345678", 25, "M")]
    
    # Llamadas a funciones
    cupos_disponibles_previos = gestor.obtener_cupos_disponibles("Tirolesa", "20251109", "10:00")
    inscripciones = gestor.inscribir(visitantes, "Tirolesa", "20251109", "10:00", acepta_terminos_condiciones = True)
    
    # Resultados
    assert cupos_disponibles_previos > 0, "No hay cupos disponibles"
    assert cupos_disponibles_previos > len(visitantes), "No hay cupos suficientes para la cantidad de visitantes"
    assert inscripciones != None, "La inscripcion es None"
    assert inscripciones != [], "La inscripción falló al crearse"
    for inscripcion in inscripciones:
        assert inscripcion.nombre_actividad == "Tirolesa", "El nombre de la actividad en la inscripcion es incorrecto"
        assert inscripcion.dia == "20251109", "El dia de inscripcion a actividad no es el mismo que el de la asctividad seleccionada"
    assert gestor.obtener_cupos_disponibles("Tirolesa", "20251109", "10:00") == cupos_disponibles_previos - len(visitantes), "Los cupos no se descontaron correctamente"
    
    print("Test de inscripcion exitosa con talle y cupo OK pasó correctamente.")
    

def test_inscripcion_exitosa_sin_talle_con_cupo_ok(gestor):
    # Precondiciones + parametros(gestor)
    visitantes = [("Juan", "12345678", 25), ("Maria", "87654321", 23)]
    
    # Llamadas a funciones
    cupos_disponibles_previos = gestor.obtener_cupos_disponibles("Safari", "20251109", "09:00")
    inscripciones = gestor.inscribir(visitantes, "Safari", "20251109", "09:00", acepta_terminos_condiciones = True)
    
    # Resultados
    assert cupos_disponibles_previos > 0, "No hay cupos disponibles"
    assert cupos_disponibles_previos > len(visitantes), "No hay cupos suficientes para la cantidad de visitantes"
    assert inscripciones != None, "La inscripcion es None"
    assert inscripciones != [], "La inscripción falló al crearse"
    assert len(inscripciones) == 2, ""
    for inscripcion in inscripciones:
        assert inscripcion.nombre_actividad == "Safari", "El nombre de la actividad en la inscripcion es incorrecto"
        assert inscripcion.dia == "20251109", "El dia de inscripcion a actividad no es el mismo que el de la asctividad seleccionada"
        assert inscripcion.horario == "09:00", "El horario de la inscripcion no coincide con el horario de la actividad seleccionada"
    assert gestor.obtener_cupos_disponibles("Safari", "20251109", "09:00") == cupos_disponibles_previos - len(visitantes), "Los cupos no se descontaron correctamente"
    
    print("Test de inscripcion exitosa sin talle y cupo OK pasó correctamente.")


def test_falla_por_sin_cupo(gestor):
    # Precondiciones + parametros(gestor)
    visitantes = [("Juan", "12345678", 25, "M")]
    
    # Llamada a funciones
    cupos_disponibles = gestor.obtener_cupos_disponibles("Palestra", "20251109", "15:00")
    # Utilizamos pytest.raises para esperar la excepción ValueError
    with pytest.raises(ValueError) as excinfo:
        gestor.inscribir(visitantes, "Palestra", "20251109", "15:00", acepta_terminos_condiciones=True)

    # Resultados
    assert cupos_disponibles == 0, "El fixture no está configurado para 0 cupos"
    assert "No hay cupos suficientes para la cantidad de visitantes" in str(excinfo.value), "No se generó la excepción esperada"
    
    print("Test de falla por sin cupo pasó correctamente.")


def test_falla_por_no_aceptar_terminos(gestor):
    # Precondiciones + parametros(gestor)
    visitantes = [("Pedro", "52345678", 22)]
    
    cupos_antes = gestor.obtener_cupos_disponibles("Jardinería", "20251109", "11:00")
    
    # Llamada a funciones
    with pytest.raises(ValueError) as excinfo:
        gestor.inscribir(visitantes, "Jardinería", "20251109", "11:00", acepta_terminos_condiciones=False)
    
    # Resultados
    cupos_despues = gestor.obtener_cupos_disponibles("Jardinería", "20251109", "11:00")
    assert cupos_antes == cupos_despues, "El sistema modificó cupos a pesar de fallo"
    assert "Debe aceptar los términos y condiciones para inscribirse" in str(excinfo.value), "No se generó la excepción esperada"
    
    print("Test de falla por sin cupo pasó correctamente.")


def test_falla_por_horario_invalido(gestor):
    #  Precondiciones + parametros (gestor)
    visitantes = [("María", "42345678", 28, "L")]
    
    # Llamadas a funciones
    with pytest.raises(ValueError) as excinfo:
        gestor.inscribir(visitantes, "Palestra", "20251109", "20:00", acepta_terminos_condiciones=True)
    
    # Resultados
    assert "El día o el horario no son válidos para esta actividad" in str(excinfo.value), "No se generó la excepción esperada"
    
    print("Test de falla por horario invalido pasó correctamente.")


def test_falla_por_falta_de_talle_en_actividad_que_lo_requiere(gestor):
    # Precondiciones + parametros(gestor)
    visitantes = [("Lucía", "62345678", 27)]
    cupos_antes = gestor.obtener_cupos_disponibles("Palestra", "20251110", "15:00")
    # Llamada a funciones
    with pytest.raises(ValueError) as excinfo:    
        gestor.inscribir(visitantes, "Palestra", "20251110", "15:00", acepta_terminos_condiciones=True)
    
    # Resultados
    cupos_despues = gestor.obtener_cupos_disponibles("Palestra", "20251110", "15:00")
    assert cupos_antes == cupos_despues, "El sistema modificó cupos a pesar de fallo"
    assert "Esta actividad requiere que se indique la talla de ropa para todos los visitantes" in str(excinfo.value), "No se generó la excepción esperada"
    
    print("Test de falla por falta de talle en actividad que lo requiere pasó correctamente.")


def test_falla_por_edad_de_visitante_es_numero_negativo(gestor):
    # Precondiciones + parametros(gestor)
    visitantes = [("Lucía", "62345678", -27)]
    cupos_antes = gestor.obtener_cupos_disponibles("Palestra", "20251110", "15:00")
    # Llamada a funciones
    with pytest.raises(ValueError) as excinfo:    
        gestor.inscribir(visitantes, "Palestra", "20251110", "15:00", acepta_terminos_condiciones=True)
    
    # Resultados
    cupos_despues = gestor.obtener_cupos_disponibles("Palestra", "20251110", "15:00")
    assert cupos_antes == cupos_despues, "El sistema modificó cupos a pesar de fallo"
    assert "La edad del visitante debe ser un número entero válido" in str(excinfo.value), "No se generó la excepción esperada"
    
    print("Test de falla al ingresar edad negativa para un visitante.")