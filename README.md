# Quadron – Lab Equipment Condition Inspector

**AI-103 Hackathon | Team 08 | Problem P06**

An AI-powered visual inspection application built using Python, Streamlit and Microsoft Azure AI Foundry. It analyzes photographs of IT equipment and laboratory instruments to identify visible damage and provide a structured condition assessment.

---

## 1. Problem Statement

Lab in-charges often record equipment conditions manually, which can lead to inconsistent inspection records and overlooked visible defects.

Quadron addresses this problem through an AI-powered application that:

- Accepts photographs of equipment.
- Automatically identifies the equipment category and type.
- Selects the appropriate five-item inspection checklist.
- Identifies visible issues and potential hazards.
- Provides a condition verdict and confidence score.
- Maintains an inspection history with image thumbnails.

**Disclaimer:** This application performs visual screening only. It is not a certified safety inspection and cannot verify hidden or internal equipment faults.

## 2. Supported Equipment

The application supports two categories:

| Category | Supported equipment |
|---|---|
| IT equipment | Desktop computer, Projector |
| Lab instruments | Microscope, Oscilloscope |

Each category has its own editable five-item inspection checklist.

## 3. Main Features

- Image upload supporting PNG and JPEG.
- Maximum image size: 2 MB.
- Automatic equipment category detection.
- Category-specific editable inspection checklists.
- AI-generated condition verdict:
  - Good
  - Needs repair
  - Unsafe
  - cannot_assess
- Identification of visible issues.
- Confidence score between 0 and 1.
- Structured JSON response validation using Pydantic.
- Inspection history with image thumbnails.
- Input validation and handling of unrelated or unsuitable images.
- Azure AI Foundry integration using Microsoft Entra ID authentication.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application backend |
| Streamlit | Web application interface |
| Microsoft Azure AI Foundry | AI model and agent hosting |
| GPT-5 mini | Multimodal equipment image analysis |
| Azure AI Projects SDK | Foundry project and agent connection |
| Azure Identity | Microsoft Entra ID authentication |
| Pillow | Image validation |
| Pydantic | Structured response validation |
| JSON | Checklist configuration and local inspection history |

## 5. Application Architecture

```text
                 USER
                   |
                   v
          STREAMLIT APPLICATION
                 app.py
                   |
          IMAGE VALIDATION
       (Type, readability, size)
                   |
                   v
          INSPECTION SERVICE
             inspector.py
                   |
          LOAD CHECKLISTS
          checklists.json
                   |
                   v
          MICROSOFT ENTRA ID
          DefaultAzureCredential
                   |
                   v
          AZURE AI FOUNDRY
          Project + Saved Agent
                   |
                   v
              GPT-5 MINI
          Text + Image Analysis
                   |
                   v
           STRUCTURED JSON
                   |
                   v
          PYDANTIC VALIDATION
                   |
                   v
          INSPECTION REPORT
                   |
                   v
          LOCAL HISTORY STORAGE
```

## 6. Project Structure

```text
T08_P06_Quadron/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── inspector.py
│   ├── checklist.py
│   ├── history.py
│   ├── image_validator.py
│   └── response_schema.py
│
├── data/
│   ├── checklists.json
│   ├── inspection_history.json
│   └── test_images/
│
├── tests/
│
├── docs/
│
└── assets/
```

## 7. Prerequisites

Before running the application, install:

1. Python 3.10 or later (use a version compatible with the installed Azure SDK dependencies).
2. Visual Studio Code or another Python IDE.
3. Microsoft Azure CLI.
4. An Azure subscription.
5. Access to the configured Azure AI Foundry project and agent.

The following resources must already exist in Azure:

- Resource group: `rg-hack-T08`
- Foundry project: `Lab-Equipment-Inspector-T08`
- Saved agent: `Lab-Equipment-Inspector-T08`
- GPT-5 mini model deployment.

## 8. Installation

### Step 1: Extract the project

Extract `2_Code.zip` into a local folder.

Open the extracted project folder in VS Code.

### Step 2: Create a virtual environment

Open PowerShell in the project directory:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 9. Azure Authentication and Configuration

The application uses Microsoft Entra ID authentication instead of storing an Azure API key.

### Step 1: Sign in to Azure

Install Azure CLI and sign in:

```powershell
az login
```

Verify your active subscription:

```powershell
az account show --output table
```

The signed-in identity must have the necessary permissions to access the Azure AI Foundry project.

### Step 2: Configure environment variables

Create a local file named `.env` in the project root.

Add:

```env
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
FOUNDRY_AGENT_NAME=Lab-Equipment-Inspector-T08
```

Replace the endpoint placeholder with the actual project endpoint from Azure AI Foundry.

**Security:** Never upload `.env` or credentials to GitHub or the hackathon submission ZIP.

### Step 3: Verify authentication

The application uses:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
```

`DefaultAzureCredential` obtains an authentication token using the available Azure identity mechanism. In the local development environment, it can use the credentials established through Azure CLI login.

## 10. Running the Application

After completing installation and Azure configuration, run:

```powershell
streamlit run app.py
```

Streamlit will start the application and provide a local URL, normally:

```text
http://localhost:8501
```

Open this address in your browser.

### Application Workflow

1. Open the application.
2. Upload a supported equipment photograph.
3. Review the uploaded image and file details.
4. Click **Inspect Equipment**.
5. Wait for Azure AI Foundry to analyze the image.
6. Review the detected equipment, condition verdict, confidence and visible issues.
7. Expand checklist items to inspect their findings.
8. Review previous inspections in the history section.

The checklist editor is available in the sidebar and allows users to modify and save the five inspection items for each category.

## 11. Inspection Response

The inspection service validates the AI response using a Pydantic model.

The response contains:

- `assessment_status`
- `category`
- `equipment_name`
- `verdict`
- `checklist_results`
- `visible_issues`
- `confidence`
- `reason`

Allowed verdicts are:

- `Good`
- `Needs repair`
- `Unsafe`
- `cannot_assess`

The application also checks that the assessment status and verdict agree.

## 12. Safety and Limitations

### Safety Measures

- Only PNG and JPEG images are accepted.
- Uploaded image size is restricted to 2 MB.
- Unreadable images are rejected.
- The AI is instructed to use visible evidence only.
- The AI is instructed not to invent defects or infer internal faults.
- Blurry, dark, unrelated or insufficiently visible images should return `cannot_assess`.
- Azure AI Foundry content filtering is configured using `Microsoft.DefaultV2`.

### Limitations

- Only four equipment types are supported.
- Assessment accuracy depends on image quality, lighting and viewing angle.
- Internal damage and functional performance cannot be verified.
- The AI may make incorrect observations.
- All results should be reviewed by a qualified human before equipment-related decisions are made.

## 13. Team Quadron

| Member | Role |
|---|---|
| RAHUL V | Application Lead |
| VIKAS CHANDRA | AI Lead |
| UMANG JAISWAL | Presenter |
| BALA SANDEEP | Testing |

**Hackathon:** AI-103  
**Team ID:** 08  
**Problem ID:** P06

---

*Built by Team Quadron using Python, Streamlit and Microsoft Azure AI Foundry.*