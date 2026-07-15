# ANRYCAMPANY Character Generation Gate

Use this file before generating any ANRYCAMPANY image that contains a person.

This gate exists to prevent substituting a new person for a registered Character ID.

## Non-Negotiable Rule

When a Character ID is specified, the image must use that registered person. A similar person, same job type, same age group, same clothing, or same mood is not acceptable.

If the generated person does not visually match the registered Character ID, the frame is failed even when the scene, pose, equipment, and composition are otherwise correct.

## Before Generation

Do not generate the image until all items are true:

- The target Character ID is named.
- The registered character reference image path has been identified and will be attached when available.
- The full Character ID note has been checked when generating, not only the quick reference.
- Patient clothing source has been checked when the character is a patient.
- The image prompt begins with the registered Character ID identity, before scene or composition instructions.
- The prompt explicitly says: same registered person, no new person, no substitute face, do not change age, hairstyle, body type, or required clothing.
- The prompt describes only the needed pose, expression, camera angle, environment, and props after the identity lock.

## Prompt Order

Use this order for every person image prompt:

1. Character ID identity lock.
2. Required reference image usage.
3. Face, age, hairstyle, body type, and clothing lock.
4. Scene and pose.
5. Camera/framing.
6. Props and medical environment.
7. Negative constraints.

Do not start with the medical scene. Starting with the scene makes the generator create a generic healthcare person.

## Required Negative Constraints

Include these ideas in the prompt when relevant:

- no different person
- no younger or older substitute
- no different hairstyle
- no different face shape
- no different clothing
- no generic nurse, doctor, technician, or patient
- no background people unless explicitly approved

## Sample Frame Review

For the first 1-2 sample frames, judge character identity before judging the scene.

Fail the sample and stop if any of these are true:

- The face does not match the registered reference.
- The age range visibly changes.
- The hairstyle or hair length changes.
- The body type changes.
- The required clothing changes.
- An unregistered person appears as the main subject.
- The assistant cannot confidently say this is the same registered Character ID.

Do not continue to remaining images after a failed character sample. Revise the prompt or image method first.

## Reporting

When reporting a sample frame, state whether the registered character match passed or failed. Do not say "existing character used" unless the visual match passed.
