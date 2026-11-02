# Domain Model Decision

## Decision
HoundIQ will maintain an explicit conceptual domain model describing its core greyhound racing concepts, relationships and business rules.

A lightweight representation is considered sufficient for the current scope. A dedicated domain layer is not justified until the complexity of the application's behaviour demonstrates a clear need for one.

## Domain Representation
The main concepts identified from the GBGB data are:
- **Greyhound:** An individual racing greyhound.
- **Meeting:** A racing event associated with a date and track.
- **Race:** A race belonging to a meeting, with its own characteristics and participants.
- **Race Participation:** The relationship between a greyhound and a specific race, including its trap, trainer, result, times and other participation-specific information.

A greyhound can have multiple race participations, while a race contains multiple participants. Historical performance is understood through these participations and their recorded results.

These concepts and relationships must remain consistent. Specific business rules, such as performance comparability, statistical calculations and data validity conditions, will be defined as the corresponding application requirements are developed.

## Architectural Approach
Adopting full Domain-Driven Design (DDD) would introduce additional abstractions and architectural complexity that are not currently justified by the project's scope.

**HoundIQ will therefore establish its domain concepts without committing to a traditional class-based model, a dedicated domain layer or a particular architectural pattern.** These implementation decisions will remain open until subsequent milestones provide sufficient technical and functional context.

## Relationship with Persistence and AI
The conceptual domain model will guide the design of the persistence model, ensuring that database structures and relationships reflect the actual racing concepts rather than simply reproducing the scraper's source-data structures.

The application will remain responsible for querying and processing persisted information and preparing the relevant context for AI components. The LLM will consume that information for analysis without directly managing or accessing persistence.

## Implementation Timing
The conceptual domain model is established during M0. Its concrete representation will be determined incrementally in subsequent milestones, alongside database design and application development.

More sophisticated domain abstractions will only be introduced when their benefits justify the additional complexity.