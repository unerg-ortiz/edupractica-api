# Interactive Challenge Builder (Documentation)

## Overview
This feature allows professors to build "Drag and Drop" interactive challenges for educational stages. The configurations are stored as structured JSON in the `interactive_config` field of each stage.

## Supported Challenge Types

### 1. Matching Pairs (`matching`)
Students must pair elements from two different groups.
- **Library**: Contains all cards (images, text, or audio).
- **Logic**: Defines which element ID pairs with which other element ID.

### 2. Classification (`classification`)
Students must drag items into predefined categories.
- **Library**: Contains the draggable items.
- **Categories**: Defines bucket IDs and which item IDs belong to each bucket.

### 3. Ordering (`ordering`)
Students must arrange items in the correct sequence.
- **Library**: Contains the draggable items.
- **Correct Order**: A list of element IDs in the expected sequence.

---

## Schema Example: Matching Pairs

```json
{
  "challenge_type": "matching",
  "instructions": "Empareja cada animal con su sonido correspondiente.",
  "elements": [
    { "id": "card_cow", "type": "image", "content": "/uploads/stages/cow.png", "label": "Vaca" },
    { "id": "card_dog", "type": "image", "content": "/uploads/stages/dog.png", "label": "Perro" },
    { "id": "sound_cow", "type": "audio", "content": "/uploads/stages/moo.mp3", "label": "Moo" },
    { "id": "sound_dog", "type": "audio", "content": "/uploads/stages/bark.mp3", "label": "Woof" }
  ],
  "matching_pairs": [
    { "left_id": "card_cow", "right_id": "sound_cow" },
    { "left_id": "card_dog", "right_id": "sound_dog" }
  ],
  "show_confetti": true
}
```

---

## Schema Example: Classification

```json
{
  "challenge_type": "classification",
  "instructions": "Clasifica los siguientes verbos en Irregulares o Regulares.",
  "elements": [
    { "id": "play", "type": "text", "content": "Played" },
    { "id": "go", "type": "text", "content": "Went" },
    { "id": "work", "type": "text", "content": "Worked" },
    { "id": "eat", "type": "text", "content": "Ate" }
  ],
  "classification_categories": [
    { "id": "cat_reg", "title": "Regulares", "correct_element_ids": ["play", "work"] },
    { "id": "cat_irreg", "title": "Irregulares", "correct_element_ids": ["go", "eat"] }
  ],
  "show_confetti": true
}
```

---

## Interactive Builder Panel (Professor view)

The frontend "Challenge Builder" should translate UI actions into this JSON format:
1. **Drag items** to the "Library" to upload images/audio.
2. **Define logic**:
    - For Matching: Use lines to connect pairs.
    - For Classification: Create buckets and drop library items into "Correct answers" zones.
3. **Save**: Send the resulting JSON to `POST /api/stages/{stage_id}/interactive`.

## Student View Interaction
- **Touch interaction**: Libraries like `dnd-kit` (React) or `native drag/drop API` support mobile touch events.
- **Animations**: Frontend should use the `show_confetti` flag to trigger animations using libraries like `canvas-confetti`.
- **Multimedia**: Elements of type `audio` should show a "Play" icon. Elements of type `image` should show a thumbnail.

---

## API Integration

### Update Challenge
```http
POST /api/stages/15/interactive
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "challenge_type": "ordering",
  "instructions": "Ordena los pasos para hacer café.",
  "elements": [ ... ],
  "correct_order": ["step_boil", "step_pour", "step_mix"],
  "show_confetti": true
}
```
