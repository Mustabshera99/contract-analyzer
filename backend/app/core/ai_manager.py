"""
Advanced AI/ML management system for the contract analyzer.
Supports multiple models, confidence scoring, and A/B testing.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import openai
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .caching import cache_result, get_document_cache
from .config import get_settings

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
	"""Supported AI model providers."""

	OPENAI = "openai"
	ANTHROPIC = "anthropic"
	LOCAL = "local"


class ModelType(str, Enum):
	"""Model types for different tasks."""

	CONTRACT_ANALYSIS = "contract_analysis"
	RISK_ASSESSMENT = "risk_assessment"
	REDLINE_GENERATION = "redline_generation"
	EMAIL_DRAFTING = "email_drafting"
	PRECEDENT_SEARCH = "precedent_search"


@dataclass
class ModelConfig:
	"""Configuration for an AI model."""

	name: str
	provider: ModelProvider
	model_type: ModelType
	model_id: str
	temperature: float = 0.1
	max_tokens: Optional[int] = None
	timeout: int = 30
	retry_attempts: int = 3
	cost_per_token: float = 0.0
	is_active: bool = True
	priority: int = 1  # Lower number = higher priority


@dataclass
class AnalysisResult:
	"""Result from AI analysis with confidence scoring."""

	content: Any
	confidence_score: float
	model_used: str
	processing_time: float
	token_usage: Dict[str, int]
	cost: float
	metadata: Dict[str, Any]


class AIModel(ABC):
	"""Abstract base class for AI models."""

	def __init__(self, config: ModelConfig):
		self.config = config
		self.settings = get_settings()

	@abstractmethod
	async def analyze(self, prompt: str, **kwargs) -> AnalysisResult:
		"""Analyze text using the model."""
		pass

	@abstractmethod
	def calculate_confidence(self, response: str, context: Dict[str, Any]) -> float:
		"""Calculate confidence score for the response."""
		pass

	def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
		"""Estimate cost for token usage."""
		return (input_tokens + output_tokens) * self.config.cost_per_token


class OpenAIModel(AIModel):
	"""OpenAI model implementation."""

	def __init__(self, config: ModelConfig):
		super().__init__(config)
		self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key.get_secret_value())

	async def analyze(self, prompt: str, **kwargs) -> AnalysisResult:
		"""Analyze text using OpenAI model."""
		start_time = time.time()

		try:
			response = await self.client.chat.completions.create(
				model=self.config.model_id,
				messages=[{"role": "user", "content": prompt}],
				temperature=self.config.temperature,
				max_tokens=self.config.max_tokens,
				timeout=self.config.timeout,
			)

			processing_time = time.time() - start_time
			content = response.choices[0].message.content

			# Calculate confidence based on response characteristics
			confidence = self.calculate_confidence(content, {"response": response})

			# Calculate token usage and cost
			token_usage = {
				"prompt_tokens": response.usage.prompt_tokens,
				"completion_tokens": response.usage.completion_tokens,
				"total_tokens": response.usage.total_tokens,
			}
			cost = self.estimate_cost(token_usage["prompt_tokens"], token_usage["completion_tokens"])

			return AnalysisResult(
				content=content,
				confidence_score=confidence,
				model_used=self.config.name,
				processing_time=processing_time,
				token_usage=token_usage,
				cost=cost,
				metadata={"response_id": response.id, "model": self.config.model_id},
			)

		except Exception as e:
			logger.error(f"OpenAI model {self.config.name} failed: {e}")
			raise

	def calculate_confidence(self, response: str, context: Dict[str, Any]) -> float:
		"""Calculate confidence score for OpenAI response."""
		if not response or len(response.strip()) < 10:
			return 0.0

		# Base confidence on response length and structure
		confidence = 0.5

		# Increase confidence for longer, more detailed responses
		if len(response) > 100:
			confidence += 0.2
		if len(response) > 500:
			confidence += 0.1

		# Check for structured content (JSON, lists, etc.)
		if "{" in response and "}" in response:
			confidence += 0.1
		if any(marker in response for marker in ["1.", "2.", "•", "-"]):
			confidence += 0.1

		# Check for legal terminology
		legal_terms = ["contract", "clause", "liability", "indemnification", "warranty", "termination"]
		if any(term in response.lower() for term in legal_terms):
			confidence += 0.1

		return min(confidence, 1.0)


class AnthropicModel(AIModel):
	"""Anthropic Claude model implementation."""

	def __init__(self, config: ModelConfig):
		super().__init__(config)
		# Note: This would require anthropic SDK
		# For now, we'll implement a placeholder
		pass

	async def analyze(self, prompt: str, **kwargs) -> AnalysisResult:
		"""Analyze text using Anthropic model."""
		# Placeholder implementation
		# In production, this would use the actual Anthropic API
		start_time = time.time()

		# Simulate processing
		await asyncio.sleep(0.1)

		processing_time = time.time() - start_time

		return AnalysisResult(
			content="Anthropic model response (placeholder)",
			confidence_score=0.8,
			model_used=self.config.name,
			processing_time=processing_time,
			token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
			cost=0.0,
			metadata={"provider": "anthropic"},
		)

	def calculate_confidence(self, response: str, context: Dict[str, Any]) -> float:
		"""Calculate confidence score for Anthropic response."""
		# Similar to OpenAI but with Anthropic-specific logic
		return 0.8


class LocalModel(AIModel):
	"""Local model implementation (e.g., Ollama, Hugging Face)."""

	def __init__(self, config: ModelConfig):
		super().__init__(config)
		# This would connect to a local model server
		pass

	async def analyze(self, prompt: str, **kwargs) -> AnalysisResult:
		"""Analyze text using local model."""
		# Placeholder implementation
		start_time = time.time()

		# Simulate processing
		await asyncio.sleep(0.5)

		processing_time = time.time() - start_time

		return AnalysisResult(
			content="Local model response (placeholder)",
			confidence_score=0.7,
			model_used=self.config.name,
			processing_time=processing_time,
			token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
			cost=0.0,
			metadata={"provider": "local"},
		)

	def calculate_confidence(self, response: str, context: Dict[str, Any]) -> float:
		"""Calculate confidence score for local model response."""
		return 0.7


class AIModelManager:
	"""Centralized AI model management with load balancing and A/B testing."""

	def __init__(self):
		self.models: Dict[str, AIModel] = {}
		self.model_configs: Dict[str, ModelConfig] = {}
		self.usage_stats: Dict[str, Dict[str, Any]] = {}
		self.ab_test_groups: Dict[str, List[str]] = {}

		# Initialize default models
		self._initialize_default_models()

	def _initialize_default_models(self):
		"""Initialize default model configurations."""
		default_models = [
			ModelConfig(
				name="gpt-4-analysis",
				provider=ModelProvider.OPENAI,
				model_type=ModelType.CONTRACT_ANALYSIS,
				model_id="gpt-4",
				temperature=0.1,
				max_tokens=4000,
				cost_per_token=0.00003,
			),
			ModelConfig(
				name="gpt-4-turbo-analysis",
				provider=ModelProvider.OPENAI,
				model_type=ModelType.CONTRACT_ANALYSIS,
				model_id="gpt-4-turbo-preview",
				temperature=0.1,
				max_tokens=4000,
				cost_per_token=0.00001,
				priority=2,
			),
			ModelConfig(
				name="gpt-3.5-analysis",
				provider=ModelProvider.OPENAI,
				model_type=ModelType.CONTRACT_ANALYSIS,
				model_id="gpt-3.5-turbo",
				temperature=0.1,
				max_tokens=2000,
				cost_per_token=0.000002,
				priority=3,
			),
		]

		for config in default_models:
			self.add_model(config)

	def add_model(self, config: ModelConfig):
		"""Add a new model to the manager."""
		try:
			if config.provider == ModelProvider.OPENAI:
				model = OpenAIModel(config)
			elif config.provider == ModelProvider.ANTHROPIC:
				model = AnthropicModel(config)
			elif config.provider == ModelProvider.LOCAL:
				model = LocalModel(config)
			else:
				raise ValueError(f"Unsupported provider: {config.provider}")

			self.models[config.name] = model
			self.model_configs[config.name] = config
			self.usage_stats[config.name] = {
				"total_requests": 0,
				"successful_requests": 0,
				"failed_requests": 0,
				"total_tokens": 0,
				"total_cost": 0.0,
				"average_confidence": 0.0,
				"average_processing_time": 0.0,
			}

			logger.info(f"Added model: {config.name} ({config.provider})")

		except Exception as e:
			logger.error(f"Failed to add model {config.name}: {e}")

	def get_model(self, model_name: str) -> Optional[AIModel]:
		"""Get a model by name."""
		return self.models.get(model_name)

	def get_models_by_type(self, model_type: ModelType) -> List[AIModel]:
		"""Get all models of a specific type."""
		return [
			model for name, model in self.models.items() if self.model_configs[name].model_type == model_type and self.model_configs[name].is_active
		]

	def select_best_model(self, model_type: ModelType, criteria: str = "confidence") -> Optional[AIModel]:
		"""Select the best model based on criteria."""
		available_models = self.get_models_by_type(model_type)

		if not available_models:
			return None

		if criteria == "confidence":
			# Select model with highest average confidence
			best_model = max(available_models, key=lambda m: self.usage_stats[m.config.name]["average_confidence"])
		elif criteria == "speed":
			# Select model with lowest average processing time
			best_model = min(available_models, key=lambda m: self.usage_stats[m.config.name]["average_processing_time"])
		elif criteria == "cost":
			# Select model with lowest cost per token
			best_model = min(available_models, key=lambda m: m.config.cost_per_token)
		else:
			# Default to priority-based selection
			best_model = min(available_models, key=lambda m: m.config.priority)

		return best_model

	async def analyze_with_model(self, model_name: str, prompt: str, **kwargs) -> AnalysisResult:
		"""Analyze text with a specific model."""
		model = self.get_model(model_name)
		if not model:
			raise ValueError(f"Model {model_name} not found")

		try:
			result = await model.analyze(prompt, **kwargs)

			# Update usage statistics
			self._update_usage_stats(model_name, result)

			return result

		except Exception as e:
			# Update failure statistics
			self.usage_stats[model_name]["failed_requests"] += 1
			logger.error(f"Model {model_name} analysis failed: {e}")
			raise

	async def analyze_with_best_model(self, model_type: ModelType, prompt: str, criteria: str = "confidence", **kwargs) -> AnalysisResult:
		"""Analyze text with the best available model."""
		model = self.select_best_model(model_type, criteria)
		if not model:
			raise ValueError(f"No active models available for type: {model_type}")

		return await self.analyze_with_model(model.config.name, prompt, **kwargs)

	async def analyze_with_fallback(self, model_type: ModelType, prompt: str, **kwargs) -> AnalysisResult:
		"""Analyze text with fallback to alternative models if primary fails."""
		models = self.get_models_by_type(model_type)

		if not models:
			raise ValueError(f"No models available for type: {model_type}")

		# Sort by priority
		models.sort(key=lambda m: m.config.priority)

		last_error = None
		for model in models:
			try:
				return await self.analyze_with_model(model.config.name, prompt, **kwargs)
			except Exception as e:
				last_error = e
				logger.warning(f"Model {model.config.name} failed, trying next: {e}")
				continue

		# If all models failed, raise the last error
		raise last_error or Exception("All models failed")

	def _update_usage_stats(self, model_name: str, result: AnalysisResult):
		"""Update usage statistics for a model."""
		stats = self.usage_stats[model_name]
		stats["total_requests"] += 1
		stats["successful_requests"] += 1
		stats["total_tokens"] += result.token_usage.get("total_tokens", 0)
		stats["total_cost"] += result.cost

		# Update running averages
		if stats["successful_requests"] > 0:
			stats["average_confidence"] = (stats["average_confidence"] * (stats["successful_requests"] - 1) + result.confidence_score) / stats[
				"successful_requests"
			]
			stats["average_processing_time"] = (
				stats["average_processing_time"] * (stats["successful_requests"] - 1) + result.processing_time
			) / stats["successful_requests"]

	def get_model_stats(self, model_name: Optional[str] = None) -> Dict[str, Any]:
		"""Get statistics for models."""
		if model_name:
			return self.usage_stats.get(model_name, {})

		return {
			"models": self.usage_stats,
			"total_models": len(self.models),
			"active_models": sum(1 for config in self.model_configs.values() if config.is_active),
		}

	def create_ab_test(self, test_name: str, model_names: List[str], traffic_split: List[float]):
		"""Create an A/B test configuration."""
		if len(model_names) != len(traffic_split):
			raise ValueError("Number of models must match traffic split")

		if abs(sum(traffic_split) - 1.0) > 0.01:
			raise ValueError("Traffic split must sum to 1.0")

		self.ab_test_groups[test_name] = {
			"models": model_names,
			"traffic_split": traffic_split,
			"results": {name: {"requests": 0, "successes": 0} for name in model_names},
		}

		logger.info(f"Created A/B test: {test_name} with models: {model_names}")

	async def analyze_with_ab_test(self, test_name: str, prompt: str, **kwargs) -> Tuple[AnalysisResult, str]:
		"""Analyze text using A/B test configuration."""
		if test_name not in self.ab_test_groups:
			raise ValueError(f"A/B test {test_name} not found")

		test_config = self.ab_test_groups[test_name]

		# Simple round-robin selection (in production, use proper traffic splitting)
		import random

		model_name = random.choices(test_config["models"], weights=test_config["traffic_split"])[0]

		try:
			result = await self.analyze_with_model(model_name, prompt, **kwargs)

			# Update A/B test results
			test_config["results"][model_name]["requests"] += 1
			test_config["results"][model_name]["successes"] += 1

			return result, model_name

		except Exception as e:
			# Update failure in A/B test results
			test_config["results"][model_name]["requests"] += 1
			raise


# Global AI model manager instance
ai_manager = AIModelManager()


def get_ai_manager() -> AIModelManager:
	"""Get the global AI model manager instance."""
	return ai_manager


# Cached analysis function
@cache_result("ai_analysis", ttl=3600)
async def cached_analyze_contract(contract_text: str, analysis_type: str = "risk_assessment") -> AnalysisResult:
	"""Cached contract analysis function."""
	model_type = ModelType(analysis_type)
	return await ai_manager.analyze_with_best_model(model_type, contract_text)
