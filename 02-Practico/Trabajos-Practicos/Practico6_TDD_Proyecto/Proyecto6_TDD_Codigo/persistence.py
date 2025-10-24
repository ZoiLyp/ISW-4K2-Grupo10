import sqlite3
import os
from typing import Dict, Any, List
import datetime


class Persistencia:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self):
        cur = self.conn.cursor()
        
        # Tabla de actividades
        cur.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            requiere_talle INTEGER NOT NULL
        )
        ''')
        
        # Tabla de horarios (cupos por actividad, dia y hora)
        cur.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            actividad_id INTEGER NOT NULL,
            dia TEXT NOT NULL,
            horario TEXT NOT NULL,
            cupos INTEGER NOT NULL,
            PRIMARY KEY(actividad_id, dia, horario),
            FOREIGN KEY(actividad_id) REFERENCES activities(id) ON DELETE CASCADE
        )
        ''')
        
        # Tabla de visitantes (cada visitante es único por DNI)
        cur.execute('''
        CREATE TABLE IF NOT EXISTS visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dni TEXT UNIQUE NOT NULL,
            edad INTEGER,
            talle TEXT
        )
        ''')
        
        # Tabla de inscripciones (una inscripción agrupa visitantes para una actividad/día/hora específicos)
        cur.execute('''
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actividad_nombre TEXT NOT NULL,
            dia TEXT NOT NULL,
            horario TEXT NOT NULL,
            acepta_terminos INTEGER NOT NULL,
            fecha TIMESTAMP NOT NULL
        )
        ''')
        
        # Tabla intermedia inscripcion_visitantes (M:N entre inscripciones y visitantes)
        cur.execute('''
        CREATE TABLE IF NOT EXISTS inscripcion_visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inscripcion_id INTEGER NOT NULL,
            visitante_id INTEGER NOT NULL,
            UNIQUE(inscripcion_id, visitante_id),
            FOREIGN KEY(inscripcion_id) REFERENCES inscripciones(id) ON DELETE CASCADE,
            FOREIGN KEY(visitante_id) REFERENCES visitantes(id) ON DELETE CASCADE
        )
        ''')
        
        # Vista para verificar que un visitante no se inscriba al mismo día/hora
        cur.execute('''
        CREATE VIEW IF NOT EXISTS visitante_horarios AS
        SELECT 
            iv.visitante_id,
            i.dia,
            i.horario,
            i.actividad_nombre
        FROM inscripcion_visitantes iv
        JOIN inscripciones i ON iv.inscripcion_id = i.id
        ''')
        
        
        cur.execute('''
        INSERT OR IGNORE INTO activities (id, nombre, requiere_talle) 
        VALUES (1, 'Tirolesa', 1), (2, 'Safari', 0), (3, 'Palestra', 1), (4, 'Jardinería', 0)
        ''')
        
        cur.executescript('''
        -- Tirolesa (id 1)
        INSERT OR IGNORE INTO horarios (actividad_id, dia, horario, cupos) VALUES
        (1, '20251109', '10:00', 2),
        (1, '20251109', '14:00', 1),
        (1, '20251110', '10:00', 5),
        (1, '20251110', '14:00', 7);
        
        -- Safari (id 2)
        INSERT OR IGNORE INTO horarios (actividad_id, dia, horario, cupos) VALUES
        (2, '20251109', '09:00', 3);
        
        -- Palestra (id 3)
        INSERT OR IGNORE INTO horarios (actividad_id, dia, horario, cupos) VALUES
        (3, '20251109', '15:00', 0),
        (3, '20251110', '15:00', 3);
        
        -- Jardinería (id 4)
        INSERT OR IGNORE INTO horarios (actividad_id, dia, horario, cupos) VALUES
        (4, '20251109', '11:00', 2);
        ''')
        
        self.conn.commit()

    def save_activity(self, actividad) -> None:
        """Guarda o actualiza una actividad y sus horarios (cupos)."""
        cur = self.conn.cursor()
        requiere = 1 if getattr(actividad, 'requiere_talle', False) else 0
        cur.execute('INSERT OR IGNORE INTO activities(nombre, requiere_talle) VALUES(?, ?)', (actividad.nombre, requiere))
        cur.execute('UPDATE activities SET requiere_talle=? WHERE nombre=?', (requiere, actividad.nombre))
        cur.execute('SELECT id FROM activities WHERE nombre=?', (actividad.nombre,))
        row = cur.fetchone()
        if not row:
            self.conn.commit()
            return
        actividad_id = row['id']
        
        # Actualizar los cupos de los horarios
        cupos = getattr(actividad, 'cupos_por_horario', None) or getattr(actividad, 'cupos_por_horarios_por_dia', {})
        for dia, horarios in cupos.items():
            for horario, cupo in horarios.items():
                # Actualizar si existe, insertar si no existe
                cur.execute('''
                    UPDATE horarios SET cupos = ?
                    WHERE actividad_id = ? AND dia = ? AND horario = ?
                ''', (cupo, actividad_id, dia, horario))
                
                if cur.rowcount == 0:  # Si no se actualizó ningún registro, insertar uno nuevo
                    cur.execute('''
                        INSERT INTO horarios(actividad_id, dia, horario, cupos) 
                        VALUES(?, ?, ?, ?)
                    ''', (actividad_id, dia, horario, cupo))
        
        # Eliminar horarios que ya no existen en la actividad
        dias_horarios = [(dia, horario) for dia, horarios in cupos.items() for horario in horarios.keys()]
        if dias_horarios:
            placeholders = ','.join(['(?,?)'] * len(dias_horarios))
            params = [x for pair in dias_horarios for x in pair]
            cur.execute(f'''
                DELETE FROM horarios 
                WHERE actividad_id = ? 
                AND (dia, horario) NOT IN ({placeholders})
            ''', [actividad_id] + params)
        
        self.conn.commit()

    def load_activities(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute('SELECT id, nombre, requiere_talle FROM activities')
        activities = []
        for row in cur.fetchall():
            actividad_id = row['id']
            nombre = row['nombre']
            requiere = bool(row['requiere_talle'])
            cur.execute('SELECT dia, horario, cupos FROM horarios WHERE actividad_id=?', (actividad_id,))
            cupos_por_dia = {}
            for h in cur.fetchall():
                dia = h['dia']
                horario = h['horario']
                cupo = h['cupos']
                cupos_por_dia.setdefault(dia, {})[horario] = cupo
            activities.append({'nombre': nombre, 'requiere_talle': requiere, 'cupos_por_horario': cupos_por_dia})
        return activities

    def _ensure_visitante(self, visitante) -> int:
        """Guarda un visitante si no existe (por DNI) y retorna su ID."""
        cur = self.conn.cursor()
        dni = getattr(visitante, 'dni', None)
        
        # Buscar por DNI existente
        cur.execute('SELECT id FROM visitantes WHERE dni=? and nombre=? and edad=?', (dni, getattr(visitante, 'nombre', None), getattr(visitante, 'edad', None)))
        row = cur.fetchone()
        if row:
            # Actualizar datos del visitante existente
            cur.execute('''UPDATE visitantes 
                           SET nombre=?, edad=?, talle=? 
                           WHERE id=?''', (
                getattr(visitante, 'nombre', None),
                getattr(visitante, 'edad', None),
                getattr(visitante, 'talle', None),
                row['id']
            ))
            self.conn.commit()
            return row['id']
        
        # Crear nuevo visitante
        cur.execute('INSERT INTO visitantes(nombre, dni, edad, talle) VALUES(?, ?, ?, ?)', (
            getattr(visitante, 'nombre', None),
            dni,
            getattr(visitante, 'edad', None),
            getattr(visitante, 'talle', None)
        ))
        self.conn.commit()
        return cur.lastrowid

    def _verificar_conflicto_horario(self, visitante_id: int, dia: str, horario: str) -> bool:
        """Verifica si un visitante ya está inscripto en el mismo día/horario."""
        cur = self.conn.cursor()
        cur.execute('''
        SELECT COUNT(*) as conflictos
        FROM visitante_horarios 
        WHERE visitante_id=? AND dia=? AND horario=?
        ''', (visitante_id, dia, horario))
        return cur.fetchone()['conflictos'] > 0

    def validar_dni_unico(self, visitante):
        """
        Valida que el DNI del visitante no esté registrado para otra persona.
        
        Retorna True si es válido, False si el DNI ya existe con otro nombre.
        """
        cur = self.conn.cursor()
        dni = getattr(visitante, 'dni', None)
        nombre = getattr(visitante, 'nombre', '').strip()
        
        cur.execute('SELECT nombre FROM visitantes WHERE dni = ?', (dni,))
        row = cur.fetchone()
        
        if row:
            nombre_existente = row['nombre'].strip()
            # Si el DNI existe pero con diferente nombre, es inválido
            if nombre_existente.lower() != nombre.lower():
                return False, f"El DNI {dni} ya está registrado para otra persona ({nombre_existente})"
        
        return True, "DNI válido"

    def save_inscripcion(self, inscripcion, visitantes=None) -> None:
        """
        Guarda una inscripción con sus visitantes asociados.
        
        Args:
            inscripcion: Objeto inscripción con datos de actividad/día/horario
            visitantes: Lista de objetos visitante para esta inscripción
        """
        cur = self.conn.cursor()
        
        # Si no se pasan visitantes, usar el visitante de la inscripción (compatibilidad)
        if visitantes is None:
            visitantes = [getattr(inscripcion, 'visitante', None)] if hasattr(inscripcion, 'visitante') else []
        
        if not visitantes:
            return
        
        # VALIDACIÓN: Verificar DNIs únicos ANTES de hacer cualquier cambio
        for visitante in visitantes:
            if visitante is None:
                continue
            valido, mensaje = self.validar_dni_unico(visitante)
            if not valido:
                raise ValueError(mensaje)
        
        # Crear la inscripción
        acepta = 1 if getattr(inscripcion, 'acepta_terminos', False) else 0
        cur.execute('''INSERT INTO inscripciones(actividad_nombre, dia, horario, acepta_terminos, fecha) 
                       VALUES(?, ?, ?, ?, ?)''', (
            getattr(inscripcion, 'nombre_actividad', None),
            getattr(inscripcion, 'dia', None),
            getattr(inscripcion, 'horario', None),
            acepta,
            datetime.datetime.utcnow()
        ))
        inscripcion_id = cur.lastrowid
        
        # Asociar visitantes a la inscripción
        dia = getattr(inscripcion, 'dia', None)
        horario = getattr(inscripcion, 'horario', None)
        
        for visitante in visitantes:
            if visitante is None:
                continue
                
            visitante_id = self._ensure_visitante(visitante)
            
            # Verificar conflicto de horario
            if self._verificar_conflicto_horario(visitante_id, dia, horario):
                raise ValueError(f"El visitante {getattr(visitante, 'nombre', 'Unknown')} ya está inscripto en el mismo día/horario")
            
            # Asociar visitante a inscripción
            cur.execute('INSERT INTO inscripcion_visitantes(inscripcion_id, visitante_id) VALUES(?, ?)', 
                       (inscripcion_id, visitante_id))
        
        self.conn.commit()

    def update_activity_cupos(self, actividad) -> None:
        """Reescribe los cupos de la actividad en la DB"""
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM activities WHERE nombre=?', (actividad.nombre,))
        row = cur.fetchone()
        if not row:
            self.save_activity(actividad)
            return
        actividad_id = row['id']
        cur.execute('DELETE FROM horarios WHERE actividad_id=?', (actividad_id,))
        cupos = getattr(actividad, 'cupos_por_horario', None) or getattr(actividad, 'cupos_por_horarios_por_dia', {})
        for dia, horarios in cupos.items():
            for horario, cupo in horarios.items():
                cur.execute('INSERT INTO horarios(actividad_id, dia, horario, cupos) VALUES(?, ?, ?, ?)', 
                           (actividad_id, dia, horario, cupo))
        self.conn.commit()

    def get_inscripciones_por_actividad(self, actividad_nombre: str) -> List[Dict]:
        """Retorna las inscripciones de una actividad con sus visitantes."""
        cur = self.conn.cursor()
        cur.execute('''
        SELECT 
            i.id, i.dia, i.horario, i.acepta_terminos, i.fecha,
            v.id as visitante_id, v.nombre, v.dni, v.edad, v.talle
        FROM inscripciones i
        JOIN inscripcion_visitantes iv ON i.id = iv.inscripcion_id  
        JOIN visitantes v ON iv.visitante_id = v.id
        WHERE i.actividad_nombre = ?
        ORDER BY i.id, v.id
        ''', (actividad_nombre,))
        
        inscripciones = {}
        for row in cur.fetchall():
            insc_id = row['id']
            if insc_id not in inscripciones:
                inscripciones[insc_id] = {
                    'id': insc_id,
                    'dia': row['dia'],
                    'horario': row['horario'],
                    'acepta_terminos': bool(row['acepta_terminos']),
                    'fecha': row['fecha'],
                    'visitantes': []
                }
            
            inscripciones[insc_id]['visitantes'].append({
                'id': row['visitante_id'],
                'nombre': row['nombre'],
                'dni': row['dni'],
                'edad': row['edad'],
                'talle': row['talle']
            })
        
        return list(inscripciones.values())

    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas básicas de la DB."""
        cur = self.conn.cursor()
        stats = {}
        
        # Contar tablas principales
        for tabla in ['activities', 'horarios', 'visitantes', 'inscripciones', 'inscripcion_visitantes']:
            cur.execute(f'SELECT COUNT(*) as count FROM {tabla}')
            stats[tabla] = cur.fetchone()['count']
        
        return stats