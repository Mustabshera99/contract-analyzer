# Sample Contracts for Testing

This directory contains sample contract documents that you can use to test the Contract Analyzer application. Each contract has different risk levels and characteristics to help you evaluate the system's analysis capabilities.

## Available Sample Contracts

### 1. Simple NDA (Non-Disclosure Agreement)

**File**: `simple_nda.pdf`
**Risk Level**: Low
**Characteristics**:

- Short and straightforward
- Standard confidentiality terms
- Minimal legal complexity
- Good for basic testing

### 2. Software License Agreement

**File**: `sample_software_license_agreement.pdf`
**Risk Level**: Medium
**Characteristics**:

- Standard software licensing terms
- Payment obligations ($50,000)
- Intellectual property clauses
- Warranty disclaimers
- Liability limitations

### 3. Employment Agreement

**File**: `sample_employment_agreement.pdf`
**Risk Level**: Medium-High
**Characteristics**:

- Non-compete clause (2 years, 50-mile radius)
- Confidentiality obligations
- Intellectual property assignment
- Termination provisions
- Salary and benefits terms

### 4. Professional Services Agreement

**File**: `sample_service_agreement.pdf`
**Risk Level**: Medium
**Characteristics**:

- Service delivery obligations
- Payment schedule ($150,000 total)
- Timeline requirements (6 months)
- Warranty provisions
- Indemnification clauses

### 5. High-Risk Data Processing Agreement

**File**: `sample_high_risk_contract.pdf`
**Risk Level**: High
**Characteristics**:

- Sensitive personal data processing
- Financial and health information
- Biometric data handling
- High liability exposure
- Complex security requirements
- Foreign contractor
- Arbitration clause

## How to Use These Contracts

1. **Start the Application**:

   ```bash
   # Backend
   cd backend && python app/main_working.py &

   # Frontend
   cd frontend && streamlit run app.py --server.port 8501 --server.address 127.0.0.1 &
   ```

2. **Access the Web Interface**: http://localhost:8501

3. **Upload a Contract**: Use the file upload feature to upload any of these sample contracts

4. **Review Analysis**: The system will analyze the contract and provide:
   - Risk assessment
   - Key clauses identification
   - Compliance checks
   - Recommendations

## Expected Analysis Results

### Low Risk (Simple NDA)

- Standard confidentiality terms
- Minimal legal exposure
- Clear and simple language

### Medium Risk (Software License, Service Agreement)

- Payment obligations
- Intellectual property concerns
- Standard liability limitations
- Warranty disclaimers

### High Risk (Employment Agreement)

- Non-compete restrictions
- Confidentiality obligations
- Potential legal disputes
- Termination risks

### Very High Risk (Data Processing Agreement)

- Data privacy compliance issues
- High liability exposure
- Complex security requirements
- Regulatory compliance concerns
- Foreign jurisdiction issues

## Testing Scenarios

1. **Basic Upload Test**: Upload `simple_nda.pdf` to verify basic functionality
2. **Risk Assessment Test**: Upload `sample_high_risk_contract.pdf` to test risk detection
3. **Payment Analysis Test**: Upload `sample_software_license_agreement.pdf` to test payment clause detection
4. **Compliance Test**: Upload `sample_employment_agreement.pdf` to test compliance checking
5. **Complex Analysis Test**: Upload `sample_service_agreement.pdf` to test complex contract analysis

## Notes

- These are sample contracts created for testing purposes only
- They contain realistic but fictional company names and details
- Use them to evaluate the system's analysis capabilities
- Modify them as needed for specific testing scenarios
