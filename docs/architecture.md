# Proposed architecture

## Components

- `app.py` is the Streamlit user interface for uploads, results, checklists,
  and inspection history.
- `config.py` loads Azure AI Foundry settings from environment variables.
- `src/image_validator.py` checks file type, readability, and the 2 MB limit.
- `src/inspector.py` will later prepare requests to GPT-5 mini and validate the
  structured response.
- `src/checklist.py` loads editable category checklists from JSON.
- `src/history.py` stores local inspection records and image-thumbnail metadata.
- `src/response_schema.py` defines the validated response contract.

## Data flow

1. A user uploads an image in Streamlit.
2. The image validator checks its type, size, and readability.
3. The future inspector sends the valid image and instructions to GPT-5 mini
   in Azure AI Foundry.
4. The model identifies IT equipment or lab instruments, selects an equipment
   checklist, and reports only visible evidence.
5. The structured response is validated with Pydantic.
6. Streamlit displays the result and checklist evidence, then saves a history
   record with a thumbnail reference.

The workflow must return `cannot_assess` for blurry or unrelated images and
must not claim to be a certified safety inspection or infer invisible damage.
