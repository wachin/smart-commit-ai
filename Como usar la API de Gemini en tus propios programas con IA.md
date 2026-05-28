# Como usar la API de Gemini en tus propios programas con IA

Este tutorial explica como usar la API de Gemini en programas propios, para que
puedas aprovechar la capa gratuita de Google AI Studio en herramientas pequeñas:
generadores de commits, asistentes de texto, clasificadores, extractores de
datos, traductores, resumidores, validadores, bots locales, etc.

La idea importante: Gemini no es solo un chat. Es una API HTTP que tu programa
puede llamar para convertir una entrada en texto, JSON, clasificaciones o
decisiones estructuradas.

## Para que puede servir

Algunas ideas practicas:

- Convertir resumenes de desarrollo en commits, como Smart Commit AI.
- Resumir textos largos, notas, PDFs convertidos a texto o logs.
- Clasificar mensajes: bug, feature, documentacion, soporte, urgente.
- Extraer datos estructurados desde texto libre: nombres, fechas, montos,
  tareas pendientes, comandos, tablas.
- Crear asistentes para aplicaciones de escritorio.
- Generar borradores de documentacion, changelogs o mensajes de release.
- Traducir texto y adaptar tono.
- Validar si una respuesta cumple reglas antes de guardarla.

## Crear una API key

1. Entra a Google AI Studio:
   <https://aistudio.google.com/api-keys>
2. Crea una API key.
3. Guardala fuera del repositorio.

En Linux, una forma simple es usar una variable de entorno:

```bash
export GEMINI_API_KEY="tu-api-key"
```

Para una app de escritorio, es mejor guardarla en una carpeta local del usuario,
por ejemplo:

```text
~/.config/mi-programa/secrets.env
```

No guardes la key dentro del codigo fuente ni la subas a GitHub.

## Modelo recomendado

Para empezar, usa:

```text
gemini-2.5-flash
```

Es una buena opcion para programas pequenos porque responde rapido, sirve para
muchos casos generales y tiene capa gratuita segun la pagina oficial de precios.

Puedes cambiar de modelo despues:

- `gemini-2.5-flash`: buena opcion general.
- `gemini-2.5-flash-lite`: mas liviano y barato.
- `gemini-2.5-pro`: mejor para razonamiento complejo, pero puede ser mas caro.
- modelos `preview`: utiles para probar, pero pueden cambiar.

## Opcion 1: usar el SDK oficial de Python

Instala el SDK:

```bash
pip install -U google-genai
```

Ejemplo minimo:

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explica que es una API en una frase.",
)

print(response.text)
```

El SDK lee automaticamente `GEMINI_API_KEY` si esta definida en el entorno.

## Opcion 2: usar REST sin dependencias externas

Esta opcion sirve si quieres evitar instalar paquetes adicionales.

```python
import json
import os
from urllib import request


api_key = os.environ["GEMINI_API_KEY"]
model = "gemini-2.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Resume este texto en 3 bullets: Gemini permite crear apps con IA."}
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.2,
        "maxOutputTokens": 300,
    },
}

req = request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    },
    method="POST",
)

with request.urlopen(req, timeout=30) as response:
    data = json.loads(response.read().decode("utf-8"))

text = data["candidates"][0]["content"]["parts"][0]["text"]
print(text)
```

## Comprobar si la API key funciona

Antes de generar texto, puedes listar modelos disponibles:

```python
import json
import os
from urllib import parse, request


api_key = os.environ["GEMINI_API_KEY"]
url = "https://generativelanguage.googleapis.com/v1beta/models"
url = f"{url}?{parse.urlencode({'key': api_key})}"

req = request.Request(url, headers={"Accept": "application/json"}, method="GET")

with request.urlopen(req, timeout=20) as response:
    data = json.loads(response.read().decode("utf-8"))

for model in data.get("models", []):
    methods = model.get("supportedGenerationMethods", [])
    if "generateContent" in methods:
        print(model["name"])
```

Esto verifica que la key responde y que modelos puedes usar con
`generateContent`.

Una comprobacion mas fuerte es hacer una generacion minima:

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Responde exactamente: OK",
)
print(response.text)
```

## Pedir JSON en vez de texto libre

Para programas reales, muchas veces conviene pedir JSON estructurado. Asi tu app
puede parsear la respuesta con menos errores.

Ejemplo con SDK y Pydantic:

```python
from google import genai
from pydantic import BaseModel


class CommitInfo(BaseModel):
    type: str
    scope: str
    subject: str
    bullets: list[str]


client = genai.Client()

prompt = """
Convierte este resumen en datos de commit:
Se agrego un boton Check API para validar Gemini y se agregaron tests.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": CommitInfo.model_json_schema(),
    },
)

print(response.text)
```

Aunque pidas JSON, valida siempre el resultado en tu programa. Que sea JSON
valido no significa que sea semanticamente perfecto.

## Prompt recomendado para una app

Un prompt de aplicacion debe ser concreto:

```text
Eres un asistente tecnico.
Devuelve solo JSON valido.
No incluyas explicaciones.
Si falta informacion, usa null.

Tarea:
Extrae type, scope, subject y bullets desde este resumen.
```

Consejos:

- Di exactamente que formato quieres.
- Pon limites: longitud maxima, numero de bullets, tipos permitidos.
- Pide que no incluya explicaciones si tu app espera parsear la salida.
- Usa `temperature` baja, por ejemplo `0.1` o `0.2`, para resultados mas
  estables.
- Agrega validacion local despues de recibir la respuesta.

## Manejo de errores

Tu programa debe esperar fallos normales:

- `400` o `404`: modelo no disponible o nombre incorrecto.
- `401` o `403`: API key invalida, restringida o proyecto sin acceso.
- `429`: cuota o limite de frecuencia.
- Respuesta sin texto: puede haber bloqueo de seguridad o `finishReason`.
- JSON invalido: el modelo no siguio el formato esperado.

Patron recomendado:

```text
1. Intentar modelo preferido.
2. Si no esta disponible, probar modelo fallback.
3. Si Gemini falla, mostrar diagnostico copiables.
4. Si es posible, usar un generador local como respaldo.
5. Nunca guardar datos de entrenamiento si la respuesta fue mala.
```

## Seguridad y privacidad

La capa gratuita es util, pero no envies cosas sensibles sin pensarlo:

- No envies contrasenas, tokens, claves privadas ni secretos.
- No pegues codigo privado sensible si no quieres que salga de tu maquina.
- En la capa gratuita, revisa las condiciones actuales de uso y privacidad.
- Para produccion o datos sensibles, revisa el plan de pago o Vertex AI.

Tambien conviene:

- guardar la key fuera del repo;
- agregar `.env`, `.env.local` y archivos de config local al `.gitignore`;
- limitar el texto enviado al modelo;
- registrar solo diagnosticos necesarios, no la API key.

## Ejemplo de arquitectura pequena

```text
Entrada del usuario
        |
        v
limpieza local del texto
        |
        v
prompt controlado
        |
        v
Gemini generateContent
        |
        v
parseo/validacion local
        |
        v
resultado final en la app
```

Para una app como Smart Commit AI:

```text
Codex summary
    -> generador local crea borrador
    -> Gemini mejora el commit
    -> validador revisa Conventional Commits
    -> si Gemini falla, se usa local
    -> si Gemini responde bien, se puede guardar como ejemplo
```

## Fuentes oficiales

- Quickstart oficial de Gemini API:
  <https://ai.google.dev/gemini-api/docs/quickstart>
- Generacion de contenido y modelos:
  <https://ai.google.dev/api>
- Salida estructurada:
  <https://ai.google.dev/gemini-api/docs/structured-output>
- Precios y capa gratuita:
  <https://ai.google.dev/gemini-api/docs/pricing>
- Limites de frecuencia:
  <https://ai.google.dev/gemini-api/docs/rate-limits>

