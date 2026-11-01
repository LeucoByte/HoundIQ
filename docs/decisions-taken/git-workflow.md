# Do or not do for this MVP these things?
TL;DR:
| Practice                      | Decision |
| ----------------------------- | -------- |
| Milestones                    | ✅        |
| Pull Requests and CI Workflow | ❌        |
| Branches                      | ❌        |
| User Stories                  | ✅        |
| Issues                        | ✅        |

## Milestones
Of course. Otherwise, I will lose track of what I am doing right now and what the next step should be. 

The fact that I am working on this project alone further supports this decision, it helps me visualize which tasks are strictly necessary to build an MVP for my entrepreneur idea.

## Pull Request and CI Workflow
No.

PRs provide three main benefits:
1. Reviewing changes before integration.
2. Verifying that tests pass.
3. Maintaining traceability between implementation work and its justification.

These benefits have been considered. However I am alone in this, with one developer working on one task at a time. There is no second developer available to review changes, and introducing a PR workflow would add process overhead without providing meaningful independent review.

Tests can still be executed locally when appropriate. Automating their execution through a CI workflow could reduce manual effort, but it would also introduce configuration and maintenance costs that are not currently justified.

Issue and commit history provide sufficient traceability for the project's current scale.

This is a deliberate scope decision, not a lack of awareness of PRs or CI practices. The approach can be reconsidered if the project grows, additional contributors become involved, or automated checks provide a clear practical benefit.

## Branches
I mean... I am the only one building this at the moment and, at least until Milestone 4 is completed, I will be focused on just one task at a time. I am not an octopus, nor can I divide myself into four versions of Marco Calvo. Therefore, I have no specific need to create branches, as I am not going to encounter any merge conflicts.

## User Stories
Answering this should be considered an insult. It is obvious that if I do not create a user journey, I will not know who I am building this for. If I do not know who the user is, I will have no clear direction on what I am doing, and I would simply be wasting my time on nothing.

## Issues
The same applies to issues. More importantly, all projects consist of complex problems and large tasks that must be broken down into subproblems. These subproblems are called issues because they have a specific, concrete reason to exist, and they typically form part of user stories to achieve a broader project goal.