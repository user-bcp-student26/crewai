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
    description = (
        f"{INSTRUCTIONS}\n\n"
        "Actúa como arquitecto de software de ReqFlow y analiza el impacto técnico "
        "del cambio aprobado. Usa la información de la feature y el contexto "
        "aprobado disponible; no inventes detalles del diseño actual ni de Discovery. "
        "Si falta evidencia, indícalo como pregunta abierta o supuesto pendiente.\n\n"
        "Entrega el análisis con estas tareas y secciones:\n"
        "1. Alcance: resume el objetivo, los criterios de aceptación y lo que queda "
        "fuera del cambio.\n"
        "2. Impacto técnico: identifica componentes y dependencias afectados, "
        "contratos HTTP que deben preservarse y evidencia que sustenta el análisis.\n"
        "3. Límites de implementación: propone pasos pequeños, reversibles e "
        "incrementales; no recomiendes una reescritura completa por defecto.\n"
        "4. Riesgos y decisiones: registra riesgos y preguntas abiertas, separa "
        "recomendaciones de decisiones aprobadas y propone un ADR solo si es necesario.\n"
        "5. Estrategia de pruebas: indica qué comportamiento existente proteger y qué "
        "pruebas deben ejecutarse antes de implementar.\n"
        "6. Aprobación: deja explícitos alcance, impacto, contratos, riesgos y pruebas "
        "que requieren aprobación humana antes de iniciar la implementación.\n\n"
        "No escribas ni modifiques código, no resuelvas hallazgos fuera del issue y "
        "no hagas handoff directo a Developer.\n\n"
        "## Feature\n"
        f"Título: {feature.get('title', '')}\n"
        f"Descripción: {feature.get('description', '')}\n"
        f"Criterios de aceptación: {feature.get('acceptance_criteria', [])}"
    )
    return Task(
        description=description,
        expected_output=(
            "Un informe Markdown de análisis de impacto arquitectónico con alcance, "
            "componentes y contratos afectados, propuesta incremental, riesgos, "
            "preguntas abiertas, estrategia de pruebas y aprobaciones pendientes. "
            "No debe incluir código."
        ),
        agent=agent,
    )
