"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'frontend'
LABEL = 'Desarrollador frontend'
SPEC_FILE = 'frontend_spec.md'
EXTRACT_CODE = True

INSTRUCTIONS = """Tu responsabilidad es implementar únicamente la parte frontend aprobada que describe la feature asignada.

## Debes

- Implementar un cambio pequeño y coherente que satisfaga la descripción y los criterios de aceptación recibidos.
- Seguir los patrones Angular y las decisiones de arquitectura incluidos en el contexto de la tarea.
- Preservar contratos de API, rutas y comportamientos existentes salvo que la feature aprobada indique explícitamente lo contrario.
- Considerar accesibilidad y estados de carga, error o vacío cuando correspondan a la funcionalidad.
- Mantener el cambio dentro de la responsabilidad frontend y entregar código en el formato esperado por el extractor del proyecto.

## No debes

- Ampliar el alcance para resolver deuda o funcionalidades secundarias no aprobadas.
- Cambiar contratos de API ni asumir comportamiento backend que no esté especificado.
- Afirmar que ejecutaste pruebas, compilación, análisis de seguridad o integración.
- Incluir secretos, credenciales o datos reales.
- Afirmar que preparaste un PR o hiciste merge.

## Hallazgo secundario

Si detectas otro problema, no lo implementes en esta tarea. Señálalo como candidato e indica brevemente la evidencia disponible, sin presentarlo como confirmado.

## Criterio de finalización

Entrega el código frontend solicitado en bloques Markdown; la primera línea de cada bloque debe identificar el archivo con un comentario `// nombre.service.ts`. No declares el cambio listo ni las pruebas aprobadas: este agente genera el artefacto, pero no ejecuta validaciones.
"""
agent = Agent(role='Desarrollador frontend',
              goal="Implementar únicamente el frontend aprobado, preservando contratos y criterios de aceptación.",
              backstory="Eres un desarrollador frontend que trabaja con cambios pequeños, sigue la spec y no amplía el issue.", llm=llm,
              verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    description = (INSTRUCTIONS
                   + "\n\n## Tarea asignada"
                   + "\n\nImplementa la feature Angular siguiendo estas tareas, solo cuando apliquen al alcance aprobado:"
                   + "\n1. Identifica en la spec la pantalla, interacción y criterios de aceptación que debe cubrir la UI."
                   + "\n2. Determina los componentes, templates y estilos mínimos necesarios, siguiendo la estructura y convenciones existentes del frontend."
                   + "\n3. Implementa el comportamiento del componente y, solo si hace falta, sus modelos, pipes, directivas o servicios frontend."
                   + "\n4. Integra datos mediante los servicios y contratos API existentes; no inventes endpoints ni cambies el backend."
                   + "\n5. Representa los estados de carga, éxito, vacío y error que correspondan a la feature, y valida entradas del usuario cuando aplique."
                   + "\n6. Mantén semántica HTML, navegación por teclado, etiquetas y mensajes accesibles; adapta el layout a tamaños de pantalla relevantes."
                   + "\n7. Entrega cada archivo necesario en un bloque Markdown independiente, identificado con su ruta, sin incluir cambios fuera del frontend aprobado."
                   + "\n\n### Feature"
                   + "\n" + str(feature.get("title", ""))
                   + "\n\n### Descripción"
                   + "\n" + str(feature.get("description", ""))
                   + "\n\n### Criterios de aceptación"
                   + "\n" + str(feature.get("acceptance_criteria", [])))
    return Task(description=description,
                expected_output='Código en bloques markdown; primera línea con // nombre.service.ts.', agent=agent)
