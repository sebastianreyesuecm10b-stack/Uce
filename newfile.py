import sqlite3 #nos permite usar variables como select, insert, delete paa nuestra tabla
from typing import List, Optional #Ayuda a definir qué tipo de datos esperamos recibir o devolver.
from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel #revisa que el tipo de texto sea correcto y no se confunda entre número y texto

app = FastAPI(
    title="Registro estudiantil",
    description="CRUD en archivo SQLite",
    version="1.0.0",
)
DB_NAME= "tabla_estudiantes.db"

#estructura donde recibiremos o modificaremos datos
class EstudiantesBase(BaseModel):
    usuario: str
    materia: str
    paralelo: str
class CrearNuevoEstudiante (EstudiantesBase):
    pass
class Estudiante(EstudiantesBase):
    id:int

def init_db(): #noos permite iniciar inmediatamente el programa 
    conn=sqlite3.connect(DB_NAME) #conexión al archivo 
    cursor=conn.cursor() #crea un cursor donde podemos escribir comando SQL a la base de datos 

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                materia TEXT NOT NULL,
                paralelo TEXT NOT NULL
            )
        """)
    #CREATE TABLE IF NOT EXISTS es una instrucción SQL para crear una tabla 
    #id :número entero para distinguir
    #autoincrement sirve para identificar cada estudiante 

    cursor.execute("SELECT COUNT(*) FROM estudiantes")
    count =cursor.fetchone()[0]

    if count ==0:
        registros_iniciales=[
            ("Sebastián Reyes", "Base de datos", "02"),
            ("José Cabascango", "Historia de la CDeIA", "01"),
            ("Santiago Chamba", "Analisis 2", "03"),
            ("Dilvany Cruz", "Algebra Lineal", "03"),
            ("Christian Flores", "Probabilidad y Estadistica", "02"),
            ("Danna Flores", "Programación 1", "01"),
            ("Sahid Galarrapa", "Programación 1", "02"),
            ("María Gancino", "Algebra Lineal", "03"),
            ("Jhordy Hídalgo", "Analisis 2", "02"),
            ("Luis Hídalgo", "Probabilidad y Estadistica", "03"),
            ("Luis Inlago", "Base de datos", "01"),
            ("Fernando López", "Analisis 2", "02"),
            ("Jeremy Maisincho", "Historia de la CDeIA", "02"),
            ("Segundo Montaluisa", "Programación 1", "03"),
            ("Jesusu Montenegro", "Base de datos", "02"),
            ("Daniela Ordoñez", "Analisis 2", "01"),
            ("Jennifer Palacios", "Historia de la CDeIA", "01"),
            ("Genesis Palma", "Base de datos", "01"),
            ("Jhonatan Pérez", "Algebra Lineal", "03"),
            ("Maicky Proaño", "Programación 1", "01"),
            ("Ronal Recalde", "Analisis 2", "02"),
        ]
        cursor.executemany( #sirve para que las lineas de la tabla se repitan y no escribir cada una a mano
            "INSERT INTO estudiantes (usuario, materia, paralelo) VALUES (?, ?, ?)",
            registros_iniciales
            #inser into dice a python que queremos guardar archivos en una tabla 
        )
        conn.commit() #commit es una orden para guardar cambios 
    conn.close()#libera memoria una vez se configura todo 

#usamos init_db para comenzar a correr el programa
init_db()

def get_db(): # mausco herramienta que nos ayudara más tarde. Sirve para consultar o borrar un dato
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row #para acceder a cada columna por su nombre
    return conn 

@app.get("/estudiantes/", response_model=List[Estudiante], summary="Obtener todos los registros")
def obtener_estudiantes():
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute("SELECT id, usuario, materia, paralelo FROM estudiantes")
    rows = cursor.fetchall()
    conn.close()
    return[dict(row) for row in rows]

@app.get("/estudiantes/{estudiante_id}", response_model = Estudiante, summary="Obtener un registro por ID")
def obtener_estudiante(estudiante_id: int):
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute("SELECT id, usuario, materia, paralelo FROM estudiantes WHERE id = ?", (estudiante_id,))
    row=cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    return dict(row)

@app.post("/estudiantes/",response_model=Estudiante, status_code=201, summary="Agregar un nuevo registro" )
def crear_estudiante(estudiante: CrearNuevoEstudiante):
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute(
        "INSERT INTO estudiantes (usuario, materia, paralelo) VALUES (?, ?, ?)",
        (estudiante.usuario, estudiante.materia, estudiante.paralelo)
    )
    conn.commit()
    nuevo_id=cursor.lastrowid
    conn.close()
    return{**estudiante.model_dump(), "id":nuevo_id}

@app.delete("/estudiantes/{estudiante_id}", summary="Eliminar un registro")
def eliminar_estudiante(estudiante_id: int):
    conn = get_db()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM estudiantes WHERE id=?", (estudiante_id,))
    conn.commit()
    filas_afectadas=cursor.rowcount
    conn.close()

    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="El ID especificado no existe")

    return{"mensaje": f"Registro con ID {estudiante_id} eliminado exitosamente"}