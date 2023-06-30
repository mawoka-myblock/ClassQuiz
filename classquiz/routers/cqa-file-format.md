<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

# .cqa - ClassQuizArchive

A file-format for ClassQuiz-quizzes which stores images and the quiz in one compact file

## How the file format works

```
[QUIZ_DATA] {C7 C7 C7 00}
{C6 C6 C6 00} [UTF-8 encoded image-index] {C5 C5 00} [IMAGE as it is]
{C6 C6 C6 00} [UTF-8 encoded image-index] {C5 C5 00} [IMAGE as it is]
```
## Understanding the schema

### in {}
- `{C7 C7 C7 00}`: separates the quiz-data from the images
- `{C6 C6 C6 00}`: Indicates that a new image-block starts
- `{C5 C5 00}`: separates image-index and image

### in []
- `[QUIZ_DATA]`: The **gzipped JSON** of the quiz with some modifications:
  - Removed `id`-field and `user_id`-field
  - Dates (`created_at` and `updated_at`) formatted as ISO-Dates
  - Images replaced with their question-index
  - Cover-image with index `-1`
- `[UTF-8 encoded image-index]`: The index of the question which the image belongs to.
- `[IMAGE as it is]`: The unmodified uploaded image (jpg, png, webp, etc.)
