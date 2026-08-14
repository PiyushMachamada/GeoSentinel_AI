import os
import time
import requests

from backend.models.prompt_builder import build_intelligence_prompt
from backend.config import OLLAMA_URL, QWEN_MODEL
print("Loaded qwen_reasoning.py")


MODEL_NAME = QWEN_MODEL

SYSTEM_PROMPT = """
You are GeoSentinel AI's Senior Geospatial Intelligence (GEOINT) Analyst.

Your responsibility is to produce professional intelligence assessments from validated Earth Observation evidence.

Rules:

- Use ONLY the supplied evidence.
- Never invent observations.
- Never invent objects.
- Never invent land-cover classes.
- Never invent transitions.
- Never contradict the supplied mission confidence.
- Explain evidence rather than listing model outputs.
- Write in the style of an intelligence analyst, not an AI assistant.
- If evidence is conflicting, explicitly describe the disagreement instead of resolving it yourself.
- Distinguish pixel difference, structural change, environmental variation, cloud, seasonality, water level, tide, and vegetation cycle.
- Only conclude construction, expansion, or infrastructure activity when multiple evidence sources support it.
"""


def _clean_response(text: str) -> str:
    """
    Clean and normalize Qwen output.
    """

    if not text:
        return "No response returned by Qwen."

    text = text.replace("\r\n", "\n")

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    unwanted = [
        "Sure!",
        "Certainly!",
        "Certainly.",
        "Okay!",
        "Okay.",
        "Here is the report:",
        "Here's the report:",
        "Below is the report:"
    ]

    for phrase in unwanted:

        if text.startswith(phrase):
            text = text[len(phrase):].strip()

    return text.strip()


def _save_prompt(prompt, prompt_path):

    os.makedirs(
        os.path.dirname(prompt_path),
        exist_ok=True
    )

    with open(
        prompt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(prompt)


def _save_report(report, report_path):

    os.makedirs(
        os.path.dirname(report_path),
        exist_ok=True
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    print(f"\nQwen report saved:\n{report_path}")


def _is_valid_report(report):

    required_sections = [

        "Executive Summary",

        "Key Findings",

        "Land Cover Assessment",

        "Change Assessment",

        "Confidence Assessment",

        "Recommendations"

    ]

    return all(
        section in report
        for section in required_sections
    )


def generate_qwen_report(
    prithvi_results,
    changestar_results,
    fusion_results,
    transition_results,
    geospatial_results,
    dynamic_world_results,
    dynamic_world_transition_results,
    osint_summary,
    mission_confidence,
    reliability_results,
    mission_assessment,
    historical_results,
    report_path,
    prompt_path,
    aoi_context=None,
):

    prompt = build_intelligence_prompt(
        prithvi_results,
        changestar_results,
        fusion_results,
        transition_results,
        geospatial_results,
        dynamic_world_results,
        dynamic_world_transition_results,
        osint_summary,
        mission_confidence,
        reliability_results,
        mission_assessment,
        historical_results,
        aoi_context=aoi_context,
    )

    _save_prompt(
        prompt,
        prompt_path
    )

    payload = {

        "model": MODEL_NAME,

        "system": SYSTEM_PROMPT,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": 0.1,

            "top_p": 0.8,

            "repeat_penalty": 1.20,

            "num_predict": 2048,

            "seed": 42

        }

    }

    for attempt in range(2):

        try:

            print(
                f"\nGenerating Intelligence Report (Attempt {attempt + 1})..."
            )

            start = time.time()

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=300
            )

            response.raise_for_status()

            result = response.json()

            if "response" not in result:
                raise RuntimeError(
                    "Ollama returned an unexpected response."
                )

            report = _clean_response(
                result["response"]
            )

            report = report.replace(
                "Prithvi EO 2.0 says",
                "Prithvi EO 2.0 indicates"
            )

            report = report.replace(
                "Dynamic World says",
                "Dynamic World indicates"
            )

            report = report.replace(
                "ChangeStar2 says",
                "ChangeStar2 indicates"
            )

            elapsed = time.time() - start

            print(
                f"Generation completed in {elapsed:.1f} seconds."
            )

            if not _is_valid_report(report):

                print(
                    "Generated report is incomplete. Retrying..."
                )

                continue

            _save_report(
                report,
                report_path
            )

            return report

        except requests.exceptions.ConnectionError:

            print("\nCould not connect to Ollama.")
            print("Make sure:")
            print("✓ Ollama is running")
            print(f"✓ Model '{MODEL_NAME}' is installed")
            print("✓ localhost:11434 is reachable")

        except requests.exceptions.Timeout:

            print("\nQwen request timed out.")

        except Exception as e:

            print(f"\nUnexpected Qwen Error:\n{e}")

    return (
        "Qwen Intelligence Report could not be generated."
    )