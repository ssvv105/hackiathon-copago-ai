from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── DATOS DE SEGUROS ──
PLANES = {
    "IESS": {
        "nombre": "IESS - Seguro General",
        "coberturas": {
            "Medicina General": {"porcentaje": 100, "copago_fijo": 0},
            "Cardiología": {"porcentaje": 90, "copago_fijo": 5},
            "Dermatología": {"porcentaje": 80, "copago_fijo": 8},
            "Traumatología": {"porcentaje": 90, "copago_fijo": 5},
            "Neurología": {"porcentaje": 85, "copago_fijo": 6},
            "Ginecología": {"porcentaje": 95, "copago_fijo": 3},
            "Pediatría": {"porcentaje": 100, "copago_fijo": 0},
            "Oftalmología": {"porcentaje": 75, "copago_fijo": 10},
            "Psiquiatría": {"porcentaje": 70, "copago_fijo": 12},
            "Gastroenterología": {"porcentaje": 80, "copago_fijo": 8},
            "Urgencias": {"porcentaje": 100, "copago_fijo": 0},
        }
    },
    "SALUD_SA": {
        "nombre": "Salud S.A. - Plan Básico",
        "coberturas": {
            "Medicina General": {"porcentaje": 80, "copago_fijo": 15},
            "Cardiología": {"porcentaje": 70, "copago_fijo": 25},
            "Dermatología": {"porcentaje": 60, "copago_fijo": 30},
            "Traumatología": {"porcentaje": 70, "copago_fijo": 25},
            "Neurología": {"porcentaje": 65, "copago_fijo": 28},
            "Ginecología": {"porcentaje": 75, "copago_fijo": 20},
            "Pediatría": {"porcentaje": 85, "copago_fijo": 12},
            "Oftalmología": {"porcentaje": 55, "copago_fijo": 35},
            "Psiquiatría": {"porcentaje": 50, "copago_fijo": 40},
            "Gastroenterología": {"porcentaje": 60, "copago_fijo": 30},
            "Urgencias": {"porcentaje": 85, "copago_fijo": 15},
        }
    },
    "BUPA": {
        "nombre": "BUPA Ecuador - Premium",
        "coberturas": {
            "Medicina General": {"porcentaje": 95, "copago_fijo": 5},
            "Cardiología": {"porcentaje": 90, "copago_fijo": 10},
            "Dermatología": {"porcentaje": 85, "copago_fijo": 15},
            "Traumatología": {"porcentaje": 90, "copago_fijo": 10},
            "Neurología": {"porcentaje": 88, "copago_fijo": 12},
            "Ginecología": {"porcentaje": 95, "copago_fijo": 5},
            "Pediatría": {"porcentaje": 100, "copago_fijo": 0},
            "Oftalmología": {"porcentaje": 80, "copago_fijo": 20},
            "Psiquiatría": {"porcentaje": 75, "copago_fijo": 25},
            "Gastroenterología": {"porcentaje": 85, "copago_fijo": 15},
            "Urgencias": {"porcentaje": 100, "copago_fijo": 0},
        }
    }
}

# ── HOSPITALES ──
HOSPITALES = [
    {"nombre": "Hospital Metropolitano", "en_red": ["SALUD_SA", "BUPA"],
     "tarifas": {"Medicina General": 45, "Cardiología": 120, "Dermatología": 90, "Traumatología": 110, "Neurología": 130, "Ginecología": 95, "Pediatría": 80, "Oftalmología": 100, "Psiquiatría": 110, "Gastroenterología": 115, "Urgencias": 200}},
    {"nombre": "Hospital Eugenio Espejo", "en_red": ["IESS"],
     "tarifas": {"Medicina General": 0, "Cardiología": 10, "Dermatología": 10, "Traumatología": 10, "Neurología": 12, "Ginecología": 8, "Pediatría": 0, "Oftalmología": 10, "Psiquiatría": 10, "Gastroenterología": 12, "Urgencias": 0}},
    {"nombre": "Clínica Pichincha", "en_red": ["BUPA", "SALUD_SA"],
     "tarifas": {"Medicina General": 55, "Cardiología": 140, "Dermatología": 100, "Traumatología": 130, "Neurología": 150, "Ginecología": 110, "Pediatría": 90, "Oftalmología": 120, "Psiquiatría": 130, "Gastroenterología": 135, "Urgencias": 250}},
    {"nombre": "Hospital de los Valles", "en_red": ["BUPA", "SALUD_SA"],
     "tarifas": {"Medicina General": 50, "Cardiología": 130, "Dermatología": 95, "Traumatología": 120, "Neurología": 140, "Ginecología": 100, "Pediatría": 85, "Oftalmología": 110, "Psiquiatría": 120, "Gastroenterología": 125, "Urgencias": 220}},
    {"nombre": "Centro de Salud Chilibulo", "en_red": ["IESS"],
     "tarifas": {"Medicina General": 0, "Cardiología": 5, "Dermatología": 5, "Traumatología": 5, "Neurología": 8, "Ginecología": 5, "Pediatría": 0, "Oftalmología": 5, "Psiquiatría": 8, "Gastroenterología": 8, "Urgencias": 0}},
]

# ── MODELOS ──
class SintomaRequest(BaseModel):
    sintoma: str

class CopagoRequest(BaseModel):
    especialidad: str
    plan_id: str

# ── ENDPOINTS ──
@app.post("/detectar-especialidad")
def detectar_especialidad(request: SintomaRequest):
    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """Eres un asistente médico. 
El paciente describe un síntoma y tú respondes SOLO con un JSON:
{
  "especialidad": "Cardiología",
  "urgencia": "alta",
  "explicacion": "Los síntomas sugieren un problema cardíaco"
}
Especialidades posibles: Medicina General, Cardiología, Dermatología, 
Traumatología, Neurología, Ginecología, Pediatría, Oftalmología, Psiquiatría, 
Gastroenterología, Urgencias."""
            },
            {"role": "user", "content": request.sintoma}
        ]
    )
    texto = respuesta.choices[0].message.content
    return json.loads(texto)

@app.post("/calcular-copago")
def calcular_copago(request: CopagoRequest):
    plan = PLANES.get(request.plan_id)
    if not plan:
        return {"error": "Plan no encontrado"}
    
    cobertura = plan["coberturas"].get(request.especialidad, {"porcentaje": 60, "copago_fijo": 20})
    porcentaje = cobertura["porcentaje"]
    copago_fijo = cobertura["copago_fijo"]

    hospitales_resultado = []
    for h in HOSPITALES:
        if request.plan_id in h["en_red"]:
            tarifa = h["tarifas"].get(request.especialidad, 80)
            descuento = tarifa * (porcentaje / 100)
            copago_final = max(tarifa - descuento, copago_fijo)
            hospitales_resultado.append({
                "nombre": h["nombre"],
                "tarifa": tarifa,
                "copago_final": round(copago_final, 2)
            })

    hospitales_resultado.sort(key=lambda x: x["copago_final"])

    return {
        "plan": plan["nombre"],
        "especialidad": request.especialidad,
        "cobertura_porcentaje": porcentaje,
        "copago_fijo": copago_fijo,
        "hospitales": hospitales_resultado
    }