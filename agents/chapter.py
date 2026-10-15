"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'chapter'
LABEL = 'Chapter'
SPEC_FILE = 'chapter_review.md'
EXTRACT_CODE = False

INSTRUCTIONS = """Revisa todas las entregas anteriores que recibes en el contexto: la historia de usuario, las entregas de Backend y Frontend, el reporte de Testing y el reporte de Security. Contrástalas con la descripción y cada criterio de aceptación de la funcionalidad.

Evalúa si las entregas cubren los criterios, si son coherentes entre sí y con la historia de usuario, y si hay defectos o riesgos que impidan aprobar. Considera bloqueante cualquier criterio incumplido, contradicción relevante o riesgo de seguridad crítico/alto sin resolver. Documenta los hallazgos medios y bajos como observaciones, salvo que impidan cumplir un criterio.

Justifica cada conclusión con evidencia concreta de las entregas o criterios; no inventes resultados ni des por implementado o verificado algo que solo se propone. Testing puede incluir casos y comandos pendientes de ejecución: indícalos como pendientes, no afirmes que pasaron ni rechaces únicamente por no tener resultados ejecutados.

Emite un único veredicto final: APROBADO solo si se cubren todos los criterios, las entregas son coherentes y no hay bloqueantes; en caso contrario, RECHAZADO. Estructura el informe con el veredicto al inicio, revisión por entrega y criterio, hallazgos/bloqueantes con su evidencia, y pendientes de validación. Separa claramente los bloqueantes de las observaciones."""
agent = Agent(role='Revisor final de entregas',
              goal="Revisar todas las entregas y emitir el veredicto final con evidencia.",
              backstory=("Eres responsable de la revisión final del equipo. Recibes el brief "
                         "de la funcionalidad y las entregas aprobadas de los agentes anteriores. "
                         "Tu evaluación debe ser imparcial, trazable a los criterios de aceptación "
                         "y explícita sobre la evidencia que falta."),
              llm=llm,
              verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    tasks = (
        "Verificar cada criterio de aceptación contra la historia de usuario y las entregas.",
        "Revisar las entregas de Backend, Frontend, Testing y Security, incluyendo validaciones pendientes.",
        "Contrastar la coherencia entre entregas e identificar bloqueantes y observaciones con evidencia.",
        "Emitir el veredicto final y organizar el informe por entrega, criterio y pendientes de validación.",
    )
    task_description = (
        INSTRUCTIONS
        + "\nTareas del rol:\n"
        + "\n".join(f"{index}. {task}" for index, task in enumerate(tasks, start=1))
        + "\nFeature: " + str(feature.get("title", ""))
        + "\n" + str(feature.get("description", ""))
        + "\n" + str(feature.get("acceptance_criteria", []))
    )
    return Task(description=task_description,
                expected_output=('Un informe estructurado con el veredicto al inicio '
                                 '(VEREDICTO: APROBADO o VEREDICTO: RECHAZADO), revisión '
                                 'por entrega y criterio, hallazgos con evidencia y pendientes '
                                 'de validación.'),
                agent=agent)
