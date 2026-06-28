from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger("hrms.ai_service")


class AIService:
    """Interface for AI features used by HRMS.

    This abstraction keeps LLM logic outside the HRMS core. Implementations
    can call OpenAI/Azure OpenAI, a local model, or a hosted analytics pipeline.
    """

    def detect_anomalies(self, attendance_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze attendance events and return detected anomalies.

        Each anomaly is a dict with keys like `employee_id`, `type`, `score`, `details`, and `metadata`.
        """
        raise NotImplementedError()

    def predict_leave_risk(self, employee_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Return leave/resignation risk scores for an employee."""
        raise NotImplementedError()


class LoggingAIService(AIService):
    def detect_anomalies(self, attendance_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info("AI analyze %d attendance events", len(attendance_events))
        # naive placeholder: no anomalies
        return []

    def predict_leave_risk(self, employee_profile: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("AI predict leave risk for %s", employee_profile.get("employee_id"))
        return {
            "employee_id": employee_profile.get("employee_id"),
            "resignation_risk": 0.01,
            "long_leave_risk": 0.02,
            "rationale": "Default log-based fallback risk estimate."
        }


class OpenAIAdapter(AIService):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        try:
            import openai
        except Exception as e:
            raise RuntimeError("openai library is required for OpenAIAdapter") from e
        self._openai = openai
        self._openai.api_key = api_key
        self._model = model

    def _run_chat(self, system: str, user: str) -> str:
        resp = self._openai.ChatCompletion.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            max_tokens=512,
        )
        return resp.choices[0].message.content

    def _extract_json(self, text: str, fallback):
        text = text.strip()
        if not text:
            return fallback

        candidates = [text]
        if "```json" in text:
            candidates = [segment.split("```", 1)[0].strip() for segment in text.split("```json")[1:]]
        elif "```" in text:
            candidates = [segment.strip() for segment in text.split("```") if segment.strip()]

        for candidate in candidates:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    start = candidate.index("{")
                    end = candidate.rindex("}") + 1
                    return json.loads(candidate[start:end])
                except Exception:
                    continue

        logger.warning("OpenAIAdapter failed to parse JSON response. Returning fallback.")
        return fallback

    def detect_anomalies(self, attendance_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an HR analytics assistant that inspects attendance records and identifies anomalies. "
            "You must return only valid JSON and nothing else. "
            "If there are no anomalies, return an empty JSON array."
        )
        user_prompt = (
            "Analyze the attendance event list below and identify suspicious attendance patterns such as buddy "
            "punching, impossible travel between timestamps, repeated late arrivals, frequent same-day leave, shift mismatch, "
            "or unexplained absence. Provide the output as a JSON array of objects. "
            "Each object should include the following keys: employee_id, type, score, details, and metadata. "
            "Do not add any fields that are not supported by the event data.\n\n"
            "Attendance events:\n"
            f"{json.dumps(attendance_events, default=str, indent=2)}\n"
            "Output format example:\n"
            "[\n"
            "  {\n"
            "    \"employee_id\": \"E123\",\n"
            "    \"type\": \"late_arrival\",\n"
            "    \"score\": 0.7,\n"
            "    \"details\": \"Employee checked in 25 minutes after shift start.\",\n"
            "    \"metadata\": {\"event_count\": 1}\n"
            "  }\n"
            "]"
        )
        response = self._run_chat(system_prompt, user_prompt)
        return self._extract_json(response, [])

    def predict_leave_risk(self, employee_profile: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are an HR risk analyst. Assess the employee profile to estimate resignation and long-leave risk. "
            "Return only valid JSON and include a concise rationale field." 
        )
        user_prompt = (
            "Review the employee profile below and produce a JSON object with keys: employee_id, resignation_risk, "
            "long_leave_risk, and rationale. Use values between 0.0 and 1.0 for the risk scores. "
            "Parse the profile fields carefully and do not invent extra facts.\n\n"
            "Employee profile:\n"
            f"{json.dumps(employee_profile, default=str, indent=2)}\n"
            "Output format example:\n"
            "{\n"
            "  \"employee_id\": \"E123\",\n"
            "  \"resignation_risk\": 0.22,\n"
            "  \"long_leave_risk\": 0.14,\n"
            "  \"rationale\": \"Multiple consecutive absent days and low engagement metrics indicate elevated risk.\"\n"
            "}"
        )
        response = self._run_chat(system_prompt, user_prompt)
        default_output = {
            "employee_id": employee_profile.get("employee_id"),
            "resignation_risk": 0.0,
            "long_leave_risk": 0.0,
            "rationale": "Unable to parse AI response.",
        }
        data = self._extract_json(response, default_output)
        if not isinstance(data, dict):
            return default_output
        if "employee_id" not in data:
            data["employee_id"] = employee_profile.get("employee_id")
        if "resignation_risk" not in data:
            data["resignation_risk"] = 0.0
        if "long_leave_risk" not in data:
            data["long_leave_risk"] = 0.0
        if "rationale" not in data:
            data["rationale"] = "No rationale provided."
        return data


# module-level default
_default_ai_service: AIService = LoggingAIService()


def get_ai_service() -> AIService:
    return _default_ai_service


def set_ai_service(svc: AIService) -> None:
    global _default_ai_service
    _default_ai_service = svc
