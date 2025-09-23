"""
Ollama Service
Free local AI model service as alternative to OpenAI/Anthropic APIs
"""

import json
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OllamaMessage(BaseModel):
	"""Message for Ollama chat completion"""

	role: str
	content: str


class OllamaResponse(BaseModel):
	"""Response from Ollama API"""

	model: str
	created_at: str
	message: OllamaMessage
	done: bool
	total_duration: int
	load_duration: int
	prompt_eval_count: int
	prompt_eval_duration: int
	eval_count: int
	eval_duration: int


class OllamaService:
	"""Free local AI model service using Ollama"""

	def __init__(self):
		self.settings = get_settings()
		self.base_url = getattr(self.settings, "ollama_base_url", "http://localhost:11434")
		self.model = getattr(self.settings, "ollama_model", "llama2")
		self.temperature = getattr(self.settings, "ollama_temperature", 0.1)
		self.max_tokens = getattr(self.settings, "ollama_max_tokens", 4000)
		self.enabled = getattr(self.settings, "ollama_enabled", False)

		logger.info(f"Ollama service initialized: {self.base_url}, model: {self.model}")

	async def is_available(self) -> bool:
		"""Check if Ollama service is available"""
		if not self.enabled:
			return False

		try:
			async with httpx.AsyncClient(timeout=5.0) as client:
				response = await client.get(f"{self.base_url}/api/tags")
				return response.status_code == 200
		except Exception as e:
			logger.warning(f"Ollama service not available: {e}")
			return False

	async def get_available_models(self) -> List[str]:
		"""Get list of available models"""
		try:
			async with httpx.AsyncClient(timeout=10.0) as client:
				response = await client.get(f"{self.base_url}/api/tags")
				if response.status_code == 200:
					data = response.json()
					return [model["name"] for model in data.get("models", [])]
				return []
		except Exception as e:
			logger.error(f"Failed to get available models: {e}")
			return []

	async def chat_completion(
		self,
		messages: List[Dict[str, str]],
		model: Optional[str] = None,
		temperature: Optional[float] = None,
		max_tokens: Optional[int] = None,
		stream: bool = False,
	) -> Optional[OllamaResponse]:
		"""Generate chat completion using Ollama"""
		try:
			if not await self.is_available():
				logger.warning("Ollama service not available")
				return None

			model = model or self.model
			temperature = temperature or self.temperature
			max_tokens = max_tokens or self.max_tokens

			payload = {"model": model, "messages": messages, "stream": stream, "options": {"temperature": temperature, "num_predict": max_tokens}}

			async with httpx.AsyncClient(timeout=60.0) as client:
				response = await client.post(f"{self.base_url}/api/chat", json=payload)

				if response.status_code == 200:
					data = response.json()
					return OllamaResponse(**data)
				else:
					logger.error(f"Ollama API error: {response.status_code} - {response.text}")
					return None

		except Exception as e:
			logger.error(f"Failed to get chat completion: {e}")
			return None

	async def analyze_contract(self, contract_text: str, analysis_type: str = "comprehensive") -> Optional[Dict[str, Any]]:
		"""Analyze contract using Ollama"""
		try:
			system_prompt = self._get_analysis_system_prompt(analysis_type)
			user_prompt = f"Analyze this contract for risks and provide recommendations:\n\n{contract_text[:4000]}"  # Limit text length

			messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

			response = await self.chat_completion(messages)
			if not response:
				return None

			# Parse the response into structured format
			return self._parse_analysis_response(response.message.content)

		except Exception as e:
			logger.error(f"Failed to analyze contract with Ollama: {e}")
			return None

	async def generate_contract_clause(self, clause_type: str, requirements: str, context: str = "") -> Optional[str]:
		"""Generate contract clause using Ollama"""
		try:
			system_prompt = """You are a legal expert specializing in contract drafting. 
            Generate clear, professional contract clauses that are legally sound and protect the client's interests."""

			user_prompt = f"""Generate a {clause_type} clause with the following requirements:
            
            Requirements: {requirements}
            
            Context: {context}
            
            Please provide a well-drafted clause that is:
            - Legally sound
            - Clear and unambiguous
            - Protective of the client's interests
            - Professional in tone"""

			messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

			response = await self.chat_completion(messages)
			if not response:
				return None

			return response.message.content

		except Exception as e:
			logger.error(f"Failed to generate contract clause with Ollama: {e}")
			return None

	async def summarize_document(self, document_text: str, summary_type: str = "executive") -> Optional[str]:
		"""Summarize document using Ollama"""
		try:
			system_prompt = f"""You are a legal document analyst. 
            Create a {summary_type} summary that highlights key points, risks, and recommendations."""

			user_prompt = f"Summarize this document:\n\n{document_text[:3000]}"  # Limit text length

			messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

			response = await self.chat_completion(messages)
			if not response:
				return None

			return response.message.content

		except Exception as e:
			logger.error(f"Failed to summarize document with Ollama: {e}")
			return None

	def _get_analysis_system_prompt(self, analysis_type: str) -> str:
		"""Get system prompt for contract analysis"""
		base_prompt = """You are an expert contract analyst. Analyze contracts for:
        1. Financial risks (payment terms, penalties, costs)
        2. Legal risks (liability, indemnification, termination)
        3. Operational risks (deliverables, timelines, dependencies)
        4. Compliance risks (regulations, standards, requirements)
        
        Provide specific recommendations for each identified risk."""

		if analysis_type == "comprehensive":
			return base_prompt + "\n\nProvide a detailed analysis with risk levels (High/Medium/Low) and specific recommendations."
		elif analysis_type == "quick":
			return base_prompt + "\n\nProvide a brief analysis focusing only on high-risk items."
		else:
			return base_prompt

	def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
		"""Parse Ollama response into structured format"""
		try:
			# Try to extract JSON if present
			if "```json" in content:
				json_start = content.find("```json") + 7
				json_end = content.find("```", json_start)
				if json_end > json_start:
					json_str = content[json_start:json_end].strip()
					return json.loads(json_str)

			# Fallback: create structured response from text
			return {
				"analysis": content,
				"risks": self._extract_risks_from_text(content),
				"recommendations": self._extract_recommendations_from_text(content),
				"summary": content[:200] + "..." if len(content) > 200 else content,
			}

		except Exception as e:
			logger.warning(f"Failed to parse analysis response: {e}")
			return {"analysis": content, "risks": [], "recommendations": [], "summary": content[:200] + "..." if len(content) > 200 else content}

	def _extract_risks_from_text(self, text: str) -> List[Dict[str, str]]:
		"""Extract risks from text analysis"""
		risks = []
		lines = text.split("\n")

		for line in lines:
			line = line.strip()
			if any(keyword in line.lower() for keyword in ["risk", "concern", "issue", "problem", "danger"]):
				# Determine risk level
				risk_level = "Medium"
				if any(keyword in line.lower() for keyword in ["high", "critical", "severe", "major"]):
					risk_level = "High"
				elif any(keyword in line.lower() for keyword in ["low", "minor", "slight"]):
					risk_level = "Low"

				risks.append({"description": line, "level": risk_level, "category": "General"})

		return risks

	def _extract_recommendations_from_text(self, text: str) -> List[str]:
		"""Extract recommendations from text analysis"""
		recommendations = []
		lines = text.split("\n")

		for line in lines:
			line = line.strip()
			if any(keyword in line.lower() for keyword in ["recommend", "suggest", "should", "consider", "advise"]):
				recommendations.append(line)

		return recommendations

	async def get_models(self) -> List[str]:
		"""Get available Ollama models"""
		try:
			if not await self._check_ollama_connection():
				return []

			async with httpx.AsyncClient() as client:
				response = await client.get(f"{self.base_url}/api/tags")
				if response.status_code == 200:
					data = response.json()
					models = [model["name"] for model in data.get("models", [])]
					logger.info(f"Retrieved {len(models)} Ollama models")
					return models
				else:
					logger.warning(f"Failed to get models: {response.status_code}")
					return []
		except Exception as e:
			logger.error(f"Failed to get Ollama models: {e}")
			return []

	async def chat(self, message: str, model: Optional[str] = None) -> str:
		"""Chat with Ollama model"""
		try:
			if not await self._check_ollama_connection():
				return "Ollama service is not available"

			# Use specified model or default
			chat_model = model or self.model

			# Check if model is available
			available_models = await self.get_models()
			if chat_model not in available_models:
				return f"Model '{chat_model}' is not available. Available models: {', '.join(available_models)}"

			# Create chat completion
			messages = [{"role": "user", "content": message}]
			response = await self.chat_completion(messages, model=chat_model)

			if response and response.message:
				return response.message.content
			else:
				return "No response from Ollama model"

		except Exception as e:
			logger.error(f"Failed to chat with Ollama: {e}")
			return f"Error: {e!s}"
