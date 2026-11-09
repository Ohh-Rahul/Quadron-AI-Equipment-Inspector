
from pathlib import Path
import mimetypes

from src.inspector import inspect_equipment


# Locate the test photograph
image_path = Path("data/test_images/test_equipment.jpg")

if not image_path.exists():
    raise FileNotFoundError(
        f"Test image not found: {image_path}"
    )

# Read the photograph
image_data = image_path.read_bytes()

# Detect MIME type
content_type, _ = mimetypes.guess_type(str(image_path))

if content_type is None:
    raise ValueError("Could not identify image type.")

print("Sending photograph to Azure AI Foundry...")
print(f"Image size: {len(image_data) / 1024:.2f} KB")

# Run inspection
result = inspect_equipment(image_data, content_type)

# Display structured result
print("\n========== INSPECTION RESULT ==========")
print(result.model_dump_json(indent=4))
print("\n========== TEST COMPLETED ==========")
