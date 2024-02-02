import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import datetime
from dotenv import load_dotenv
import os
import psycopg2

import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Obtener la ruta al directorio 'main' (un nivel arriba de donde se encuentra este archivo) (solo si esta en un directorio anterior) 

#basedir = os.path.abspath(os.path.dirname(__file__))
#main_dir = os.path.join(basedir, '..')
#sys.path.append(main_dir)

# Cargar las variables de entorno desde .env (dentro del directorio 'main')

#load_dotenv(os.path.join(main_dir, 'main', '.env'))

from models.pokedex import create_table_if_not_exists

from jwt_config import validar_token

main = FastAPI()
main.title = "Pokedex de Samuel"
main.version = "1.0.1"


load_dotenv()
DATABASE_URL = os.environ['DATABASE_URL']

create_table_if_not_exists()

class Usuario(BaseModel):
    email: str
    clave: str



class Portador(HTTPBearer):
    async def __call__(self, request: Request):
        autorizacion = await super().__call__(request)
        dato = validar_token(autorizacion.credentials)

        if dato["email"] != "1234":
            raise HTTPException(status_code=403, detail="No autorizado")


@main.get("/pokemon/{name}", tags=["Pokemon"])
def fetch_pokemon(name: str):

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM my_pokedex WHERE name = %s", (name,))
    pokemon = cur.fetchone()
    conn.close()

    if pokemon:
        return {'message': f"Pokemon {name} is already in the database",
                "data": pokemon}
    else:
        try:

            api_url = f"https://pokeapi.co/api/v2/pokemon/{name}"
            response = requests.get(api_url)
            if response.status_code == 200:
                data: dict = response.json()

                new_pokemon = {
                    "name": data.get("name", "Sin Nombre"),
                    "height": str(data.get("height", 0)),
                    "weight": str(data.get("weight", 0)),
                    "created_date": datetime.datetime.now()
                }


                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                cur.execute("INSERT INTO my_pokedex (name, height, weight, created_date) VALUES (%s, %s, %s, %s)", 
                    (new_pokemon['name'], new_pokemon['height'], new_pokemon['weight'], new_pokemon['created_date']))
                conn.commit()
                cur.close()
                conn.close()
                return {'message': "Requesting...",
                        "data": new_pokemon}
            else:
                    return JSONResponse(
                        content={
                            "mensaje": f"Error al hacer la solicitud. Código de estado: {response.status_code}"
                        }
                    )
        except Exception as e:
            return JSONResponse(
                content={"mensaje": f"Error en el servidor: {str(e)}"}
            )





@main.delete("/pokemon/{name}", tags=["Pokemon"])
def delete_pokemon(name: str):
    #with sesion() as db:
        #resultado = db.query(pokedexmodelo).filter(pokedexmodelo.name == name).first()
        #if not resultado:
            raise HTTPException(
                status_code=404, detail="No se ha encontrado el pokemon"
            )

        #db.delete(resultado)
        #db.commit()
        #return {"mensaje": f"El pokemon {name} se ha eliminado correctamente"}


# @main.post('/login',tags=['Autenticacion'])
# def login(usuario:Usuario):
#     if usuario.email == '1234' and usuario.clave == '1234':
#         token:str=dame_token(usuario.dict())
#         return JSONResponse(status_code=200,content=token)
#     return JSONResponse(content={'message':'Error de autenticacion'},status_code=401)
