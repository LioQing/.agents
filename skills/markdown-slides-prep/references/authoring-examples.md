# Authoring examples

Read the renderer's current format contract first. These examples illustrate source organization and permission boundaries, not a fixed presentation structure. Their fixture content must not be reused as real user evidence.

## Conversational brief with an explicitly requested diagram

Example user material:

> I need to explain our onboarding handoffs. The steps are submit request, manager approves, and operations creates account. Include a flow diagram and end with a question about ownership. We have not measured turnaround time, so do not suggest timings.

Prepared source:

```markdown
# Onboarding handoffs

- Submit request.
- Manager approves.
- Operations creates account.

---
instruction: |
  Turn the following steps into a flow diagram in the supplied order.
  Keep the step labels and a readable text equivalent.
  Do not infer timings, service targets, or additional steps.

# Request to account

1. Submit request.
2. Manager approves.
3. Operations creates account.

> [!NOTE]
> Turnaround time has not been measured.

---
# Ownership discussion

Which handoff needs clearer ownership?
```

The first and final slides need no annotation. Drafting the narrative did not authorize further content rewriting. Only the diagram is deferred, and its semantic content remains visible for review.

## Exact table with requested visualization

Example user material:

> Prepare a slide comparing A at 12 minutes and B at 18 minutes. These are illustrative values, not measurements. I want the rendering agent to make a horizontal bar chart.

Prepared source:

```markdown
instruction: Create a horizontal bar chart from the supplied table. Preserve labels, values, minute units, the illustrative-data warning, and an accessible exact-value equivalent.

# Illustrative comparison

| Option | Time (minutes) |
| --- | ---: |
| A | 12 |
| B | 18 |

> [!IMPORTANT]
> These are illustrative values, not measurements.
```

The annotation does not prescribe palette, font, or chart library. Those belong to the renderer's design contract or explicit user overrides. Do not turn an unrequested table into a chart just to add a customization instruction.

## Literal code and ordinary content

Example user material:

> Show the exact delimiter example below, then put the deployment conditions on another slide. Testing is still pending, not passed, and traffic expansion is not yet approved. Preserve the caution about expanding traffic before testing finishes.

Prepared source:

````markdown
# Delimiters inside code

```markdown
---
instruction: This is literal example text.
# Example heading
```

The fenced separator is code, not another slide.

---
# Deployment conditions

- Testing is pending.
- Traffic expansion is not yet approved.

> [!CAUTION]
> Do not expand traffic before testing finishes.
````

Neither slide requires agent customization. `instruction:` inside a code example does not become an annotation. Save the actual deck contents without the outer explanatory fence shown in this reference.

## Missing information and review handoff

If a brief mentions a launch date but supplies no date, ask for it before finalizing. If the user explicitly requests a provisional draft, retain a visible limitation such as "Launch date: awaiting confirmation" rather than invented specifics. Do not add an instruction telling the renderer to manufacture the missing date.

Keep drafting questions, parser diagnostics, and approval requests in the conversation, not YAML front matter or invented metadata. A concise handoff can state the `.md` path, slide count, slides with proposed customizations, and any missing facts/assets. Then stop. The user can edit the source and later use the `markdown-slides` skill to render it.
