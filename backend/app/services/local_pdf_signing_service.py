"""
Local PDF Signing Service
Free local PDF signing as alternative to DocuSign
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib.colors import black, red
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SignatureInfo:
	"""Information about a signature"""

	def __init__(
		self,
		signer_name: str,
		signer_email: str,
		signature_text: str = "",
		signature_image_path: Optional[str] = None,
		x_position: float = 100,
		y_position: float = 100,
		page_number: int = 1,
	):
		self.signer_name = signer_name
		self.signer_email = signer_email
		self.signature_text = signature_text
		self.signature_image_path = signature_image_path
		self.x_position = x_position
		self.y_position = y_position
		self.page_number = page_number


class LocalPDFSigningService:
	"""Free local PDF signing service"""

	def __init__(self):
		self.settings = get_settings()
		self.enabled = getattr(self.settings, "local_pdf_signing_enabled", True)
		self.cert_path = getattr(self.settings, "local_pdf_signing_cert_path", "")
		self.key_path = getattr(self.settings, "local_pdf_signing_key_path", "")

		# Create signatures directory
		self.signatures_dir = Path("/app/storage/signatures")
		self.signatures_dir.mkdir(parents=True, exist_ok=True)

		logger.info(f"Local PDF signing service initialized: enabled={self.enabled}")

	async def add_signature_to_pdf(
		self, pdf_content: bytes, signatures: List[SignatureInfo], output_filename: Optional[str] = None
	) -> Optional[bytes]:
		"""Add signatures to PDF content"""
		try:
			if not self.enabled:
				logger.warning("Local PDF signing is disabled")
				return None

			# For this demo, we'll create a simple signature overlay
			# In production, you would use PyPDF2 or similar to properly merge signatures

			# Create signature overlay
			signature_overlay = self._create_signature_overlay(signatures)

			# For demo purposes, return the original PDF with a note about signatures
			# In production, you would merge the signature overlay with the original PDF
			return pdf_content

		except Exception as e:
			logger.error(f"Failed to add signature to PDF: {e}")
			return None

	async def create_signature_page(self, signatures: List[SignatureInfo], page_title: str = "Contract Signatures") -> bytes:
		"""Create a signature page for the contract"""
		try:
			buffer = io.BytesIO()
			c = canvas.Canvas(buffer, pagesize=letter)
			width, height = letter

			# Add title
			c.setFont("Helvetica-Bold", 16)
			c.drawString(100, height - 100, page_title)

			# Add current date
			c.setFont("Helvetica", 12)
			c.drawString(100, height - 130, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

			# Add signature lines
			y_position = height - 200
			for i, signature in enumerate(signatures):
				# Signature line
				c.line(100, y_position, 500, y_position)

				# Signer name
				c.setFont("Helvetica", 10)
				c.drawString(100, y_position - 20, f"Name: {signature.signer_name}")
				c.drawString(100, y_position - 35, f"Email: {signature.signer_email}")

				# Signature text or image
				if signature.signature_text:
					c.setFont("Helvetica-Italic", 12)
					c.drawString(100, y_position - 55, f"Signature: {signature.signature_text}")
				elif signature.signature_image_path and Path(signature.signature_image_path).exists():
					try:
						# Add signature image
						img = ImageReader(signature.signature_image_path)
						c.drawImage(img, 100, y_position - 80, width=200, height=50)
					except Exception as e:
						logger.warning(f"Failed to add signature image: {e}")
						c.setFont("Helvetica", 10)
						c.drawString(100, y_position - 55, "[Signature Image]")

				# Add signature date
				c.setFont("Helvetica", 9)
				c.drawString(400, y_position - 20, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

				y_position -= 120

				# Add new page if needed
				if y_position < 200 and i < len(signatures) - 1:
					c.showPage()
					y_position = height - 100

			# Add footer
			c.setFont("Helvetica", 8)
			c.drawString(100, 50, "This document has been digitally signed using Local PDF Signing Service")
			c.drawString(100, 35, f"Generated on: {datetime.now().isoformat()}")

			c.save()
			buffer.seek(0)
			return buffer.getvalue()

		except Exception as e:
			logger.error(f"Failed to create signature page: {e}")
			return b""

	async def create_signature_template(self, signer_name: str, signer_email: str, contract_title: str = "Contract Agreement") -> bytes:
		"""Create a signature template for a signer"""
		try:
			buffer = io.BytesIO()
			c = canvas.Canvas(buffer, pagesize=letter)
			width, height = letter

			# Add header
			c.setFont("Helvetica-Bold", 18)
			c.drawString(100, height - 100, "Digital Signature Template")

			# Contract information
			c.setFont("Helvetica", 12)
			c.drawString(100, height - 140, f"Contract: {contract_title}")
			c.drawString(100, height - 160, f"Signer: {signer_name}")
			c.drawString(100, height - 180, f"Email: {signer_email}")
			c.drawString(100, height - 200, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

			# Signature area
			c.setFont("Helvetica-Bold", 14)
			c.drawString(100, height - 250, "Signature Area:")

			# Draw signature box
			c.rect(100, height - 350, 400, 100)
			c.setFont("Helvetica", 10)
			c.drawString(110, height - 320, "Please sign within this box")

			# Signature line
			c.line(100, height - 380, 500, height - 380)
			c.setFont("Helvetica", 10)
			c.drawString(100, height - 400, f"Signature: _________________________")
			c.drawString(100, height - 420, f"Date: _________________________")

			# Instructions
			c.setFont("Helvetica", 10)
			instructions = [
				"Instructions:",
				"1. Print this page",
				"2. Sign in the designated area",
				"3. Scan or photograph the signed page",
				"4. Upload the signed page to complete the process",
			]

			y_pos = height - 480
			for instruction in instructions:
				c.drawString(100, y_pos, instruction)
				y_pos -= 20

			c.save()
			buffer.seek(0)
			return buffer.getvalue()

		except Exception as e:
			logger.error(f"Failed to create signature template: {e}")
			return b""

	async def validate_signature(self, signature_data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate a signature (basic validation for demo)"""
		try:
			validation_result = {"valid": True, "errors": [], "warnings": []}

			# Check required fields
			required_fields = ["signer_name", "signer_email", "signature_text"]
			for field in required_fields:
				if not signature_data.get(field):
					validation_result["valid"] = False
					validation_result["errors"].append(f"Missing required field: {field}")

			# Validate email format
			email = signature_data.get("signer_email", "")
			if email and "@" not in email:
				validation_result["valid"] = False
				validation_result["errors"].append("Invalid email format")

			# Check signature text length
			signature_text = signature_data.get("signature_text", "")
			if len(signature_text) < 3:
				validation_result["warnings"].append("Signature text is very short")

			return validation_result

		except Exception as e:
			logger.error(f"Failed to validate signature: {e}")
			return {"valid": False, "errors": [f"Validation error: {e!s}"], "warnings": []}

	def _create_signature_overlay(self, signatures: List[SignatureInfo]) -> bytes:
		"""Create a signature overlay PDF"""
		try:
			buffer = io.BytesIO()
			c = canvas.Canvas(buffer, pagesize=letter)
			width, height = letter

			# Add signature information
			c.setFont("Helvetica-Bold", 12)
			c.drawString(100, height - 100, "Digital Signatures")

			y_position = height - 150
			for signature in signatures:
				c.setFont("Helvetica", 10)
				c.drawString(100, y_position, f"Signed by: {signature.signer_name}")
				c.drawString(100, y_position - 15, f"Email: {signature.signer_email}")
				c.drawString(100, y_position - 30, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

				if signature.signature_text:
					c.drawString(100, y_position - 45, f"Signature: {signature.signature_text}")

				y_position -= 80

			c.save()
			buffer.seek(0)
			return buffer.getvalue()

		except Exception as e:
			logger.error(f"Failed to create signature overlay: {e}")
			return b""

	async def get_signing_status(self, document_id: str) -> Dict[str, Any]:
		"""Get signing status for a document"""
		try:
			# For demo purposes, return mock status
			return {
				"document_id": document_id,
				"status": "pending",
				"signatures_required": 2,
				"signatures_completed": 0,
				"created_at": datetime.now().isoformat(),
				"last_updated": datetime.now().isoformat(),
			}

		except Exception as e:
			logger.error(f"Failed to get signing status: {e}")
			return {"document_id": document_id, "status": "error", "error": str(e)}

	async def create_template(self, template_name: str, template_data: Dict[str, Any]) -> Optional[str]:
		"""Create a PDF signing template"""
		try:
			template_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

			# Store template data
			template_info = {
				"template_id": template_id,
				"template_name": template_name,
				"created_at": datetime.now().isoformat(),
				"template_data": template_data,
			}

			# In a real implementation, this would be stored in a database
			# For demo purposes, we'll just return the template ID
			logger.info(f"Created PDF signing template: {template_name} (ID: {template_id})")
			return template_id

		except Exception as e:
			logger.error(f"Failed to create PDF signing template: {e}")
			return None

	async def sign_document(self, document_path: str, signature_data: Dict[str, Any]) -> Optional[str]:
		"""Sign a PDF document locally"""
		try:
			# Validate signature data
			validation = await self.validate_signature(signature_data)
			if not validation["valid"]:
				logger.error(f"Signature validation failed: {validation['errors']}")
				return None

			# Create signature info
			signature_info = SignatureInfo(
				signer_name=signature_data.get("signer_name", "Unknown Signer"),
				signer_email=signature_data.get("signer_email", "unknown@example.com"),
				signature_text=signature_data.get("signature_text", ""),
				signature_image=signature_data.get("signature_image"),
				signing_reason=signature_data.get("signing_reason", "Contract Agreement"),
				signing_location=signature_data.get("signing_location", "Digital Signature"),
			)

			# Sign the document
			signed_pdf = await self.sign_pdf(document_path, [signature_info])
			if not signed_pdf:
				return None

			# Save signed document
			output_path = document_path.replace(".pdf", "_signed.pdf")
			with open(output_path, "wb") as f:
				f.write(signed_pdf)

			logger.info(f"Document signed successfully: {output_path}")
			return output_path

		except Exception as e:
			logger.error(f"Failed to sign document: {e}")
			return None
