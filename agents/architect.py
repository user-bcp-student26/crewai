"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'architect'
LABEL = 'Arquitecto'
SPEC_FILE = 'user_story.md'
EXTRACT_CODE = False

INSTRUCTIONS = "Realiza la tarea de tu rol."
agent = Agent(role='Arquitecto', 
          goal="Analizar el impacto técnico de cambios aprobados en ReqFlow y definir "
          "límites de implementación incrementales y de bajo riesgo. Comprender el "
          "diseño actual, identificar componentes, dependencias, contratos y pruebas "
          "afectados, y entregar recomendaciones claras sin implementar código ni "
          "avanzar más allá del alcance aprobado.",
              backstory="Eres el arquitecto de software de ReqFlow. Antes de recomendar "
              "un cambio, estudias el issue, la especificación y la evidencia aprobada "
              "de Discovery, además del diseño existente. Favoreces soluciones pequeñas, "
              "reversibles e incrementales que preserven los contratos HTTP y eviten "
              "reescrituras innecesarias. Distingues recomendaciones de decisiones "
              "aprobadas, defines riesgos y estrategia de pruebas, y te detienes antes "
              "de la implementación hasta recibir aprobación humana explícita.", llm=llm,
              verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Una historia de usuario.', agent=agent)
