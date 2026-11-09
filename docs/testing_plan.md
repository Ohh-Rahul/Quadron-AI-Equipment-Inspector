# Hackathon testing plan

The following acceptance tests guide the completed application:

## A1: Damaged equipment

Upload a clear image of damaged equipment. The application must identify the
correct category, describe visible defects and evidence, and return an
appropriate `Needs repair` or `Unsafe` result.

## A2: Undamaged equipment

Upload a clear image of undamaged equipment. The application must return
`Good` and must not invent defects that are not visible.

## A3: Unusable or unrelated image

Upload a blurry photograph or an unrelated photograph. The application must
return `cannot_assess` and explain that there is insufficient relevant visual
evidence.

Additional checks should cover the 2 MB upload limit, checklist selection,
history thumbnails, and response-schema validation.
