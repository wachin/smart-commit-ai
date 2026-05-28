


# Git Commit Message: The Rules, Examples, and Conventions
https://www.datacamp.com/tutorial/git-commit-message

A practical guide covering the structure, rules, and real-world examples developers need to write clear, consistent Git commit messages that improve debugging, speed up code reviews, and turn Git history into searchable documentation.

Jan 27, 2026  · 14 min read

Contents

* [Why a Git Commit Message Matters](#why-a-git-commit-message-matters-acomm)
- [Core Principles of a Good Git Commit Message](#core-principles-of-a-good-git-commit-message-<span)
- [Write for future readers](#write-for-future-readers-<span)
- [Be clear and concise](#be-clear-and-concise-<span)
- [Be consistent](#be-consistent-<span)
- [Explain what and why (not how)](#explain-what-and-why-\(not-how\)-<span)
* [The Structure of a Git Commit Message](#the-structure-of-a-git-commit-message-<span)
* [Subject line](#subject-line-<span)
* [Body (when needed)](#body-\(when-needed\)-<span)
* [Footer (optional)](#footer-\(optional\)-useth)
- [Common Git Commit Message Types and When to Use Them](#common-git-commit-message-types-and-when-to-use-them-manyp)
* [Rules for Writing a Better Git Commit Message](#rules-for-writing-a-better-git-commit-message-<span)
- [Examples of a Good Git Commit Message](#examples-of-a-good-git-commit-message-<span)
- [A simple fix](#a-simple-fix-<code)
- [A new feature](#a-new-feature-<code)
- [A refactor](#a-refactor-<code)
- [A documentation update](#a-documentation-update-<code)
- [Referencing an issue or ticket](#referencing-an-issue-or-ticket-<code)
* [Conventional Commits as a Git Commit Message Standard](#conventional-commits-as-a-git-commit-message-standard-<span)
* [Basic format](#basic-format-<span)
* [When conventional commits are useful](#when-conventional-commits-are-useful-teams)
- [Common Git Commit Message Mistakes to Avoid](#common-git-commit-message-mistakes-to-avoid-<span)
- [Vague or generic messages](#vague-or-generic-messages-<span)
- [Mixing unrelated changes](#mixing-unrelated-changes-<span)
- [Leaving work-in-progress messages](#leaving-work-in-progress-messages-<span)
* [Best Practices for Teams Using Git Commit Messages](#best-practices-for-teams-using-git-commit-messages-<span)
- [Conclusion](#conclusion-<span)
* [FAQs](#faq)

## Training more people?

Get your team access to the full DataCamp for business platform.

[For Business](https://www.datacamp.com/business)For a bespoke solution [book a demo](https://www.datacamp.com/business/demo-2).

Have you ever tried to debug a feature you wrote six months ago and found commit messages like "fix stuff" or "updates"?

That’s usually followed by spending 20-30 minutes clicking through diffs trying to understand what changed and why. This happens because most developers treat commit messages as an afterthought - something to get past before pushing code. But a commit message is kind of like documentation. It lives with your code, so you might want to invest a couple of additional keystrokes to make it clear.

A good Git commit message explains what changed and why it changed. It helps your team review code faster, makes debugging easier, and turns your Git history into a a progress bar of sorts.

In this article, I'll show you the conventions, structure, and examples you need to write helpful git commit messages.

If you’re new to Git, this isn’t where you should start learning. Opt for our [Introduction to Git](https://www.datacamp.com/courses/introduction-to-git) course instead. You’ll get the fundamentals down in one afternoon.

## Learn Git Fundamentals Today

For beginners: Master version control using Git.

[Start Learning For Free](https://www.datacamp.com/courses/introduction-to-git)

## Why a Git Commit Message Matters

A commit message explains your changes to anyone who reads the code later, including the future you.

Three months from now, you won't remember why you refactored that data pipeline or why you switched from pandas to polars for a specific operation. Your commit message is the only record of your reasoning. Without it, you're left guessing or digging through Slack threads and JIRA tickets.

Here are a couple more concrete reasons why git commit message matters.

Code reviews move faster with clear commit messages. Your reviewer can scan the message, understand the intent, and focus on whether the implementation matches. Vague messages force reviewers to reverse-engineer your thinking from the [diff](https://www.datacamp.com/tutorial/git-diff-guide) alone.

Debugging gets easier too. When a bug appears, you'll use `git log` or `git blame` to trace when the problematic code was introduced. A message like "fix authentication bug" tells you nothing. A message like "fix token expiration check in auth middleware" points you straight to the problem.

Team collaboration depends on readable history. When someone joins your project or picks up where you left off, they'll read through commits to understand how the codebase evolved. Clear messages turn your Git history into documentation that actually helps.

The bottom line is that a descriptive commit message takes 15-30 seconds to write. But it saves hours of confusion down the line.

## Core Principles of a Good Git Commit Message

Good commit messages follow a few simple principles - nothing more to it.

### Write for future readers

Your commit message isn't for you right now - it's for whoever reads it six months from now.

That person might be a new team member trying to understand why the codebase works a certain way. It might be you, trying to remember why you made a specific decision. Either way, they won't have the context you have today.

Focus on intent and reasoning, not just what changed. The diff shows what changed. Your message should explain why it changed and what problem it solves.

### Be clear and concise

Short, descriptive messages are easier to scan when you're looking through dozens of commits.

A message like "add caching" is vague. A message like "add Redis caching for API responses" tells you exactly what happened. You can read it in `git log --oneline` and know immediately what the commit does.

Your subject line should answer: what does this commit do? If you need more than 50-60 characters to answer that, you're probably committing too many changes at once.

### Be consistent

Consistency across your repository makes the history predictable and easier to parse.

When every commit follows the same format, you can quickly scan through history. You know where to look for the type of change, the scope, and the description. Teams that enforce consistent formats can also automate tasks like generating changelogs or filtering commits by type.

Pick a style and stick with it. If your team uses present tense imperatives, don't randomly switch to past tense.

### Explain what and why (not how)

The code shows how you solved the problem. Your commit message should explain what the problem was and why you chose this solution.

Don't write "refactored load\_data() to use list comprehension instead of for loop." Write "speed up data loading by 40% for large CSV files." The first message describes the code change. The second explains the impact.

Add context when it helps future readers understand your decision. If you tried three different approaches before settling on this one, mention that. If there's a related bug report or design decision, reference it.

## The Structure of a Git Commit Message

Most Git commit messages follow a standard three-part structure: subject line, body, and footer.

### Subject line

The subject line is a one-line summary that appears in `git log --oneline` and pull request lists.

Keep it under 50 characters if possible, 72 at most. This limit guarantees the message displays properly in terminal output and GitHub's UI without getting cut off. If you can't fit your summary in 50 characters, you're probably trying to describe too many changes in one commit.

Use the imperative mood - write "add feature" instead of "added feature" or "adds feature." Think of it as completing the sentence "If applied, this commit will...". So "If applied, this commit will add Redis caching" reads naturally, while "If applied, this commit will adds Redis caching" doesn't.

Examples:

* `fix null pointer exception in data loader`
* `add caching layer for API responses`
* `remove deprecated pandas functions`

### Body (when needed)

Skip the body for simple changes. If your subject line fully explains the commit, you're done.

Add a body when you need to explain why you made the change or provide context that helps future readers. Leave a blank line between the subject and body - Git uses this to separate the two parts.

The body should answer questions like: What problem does this solve? Why did you choose this approach? Are there any side effects or limitations? Did you consider other solutions?

Wrap lines at 72 characters to keep the text readable in terminal output. Most text editors can do this automatically.

Example:

```bash
add Redis caching for API responses

API response times were hitting 2-3 seconds for repeated queries.
Added Redis with 5-minute TTL to cache query results. This drops
response time to ~50ms for cached queries.

Considered using in-memory cache but Redis lets us scale horizontally
if needed.
```

### Footer (optional)

Use the footer to reference related issues, pull requests, or breaking changes.

If your commit fixes a GitHub issue, add `Fixes #123` or `Closes #456` in the footer. GitHub will automatically close the issue when the commit merges. For breaking changes, add `BREAKING CHANGE:` followed by a description of what broke and how to migrate.

Example:

```bash
remove support for Python 3.7

Python 3.7 reached end-of-life in June 2023. This commit drops
support and updates minimum version to Python 3.8.

BREAKING CHANGE: Python 3.7 users must upgrade to 3.8 or later.
Closes #789
```

You don't need a footer for most commits - only when you're linking to external references or marking breaking changes.

## Common Git Commit Message Types and When to Use Them

Many projects use commit type prefixes to categorize changes at a glance.

You don't need to memorize a strict list of labels. The goal is to help readers quickly identify what kind of change happened without reading the full diff.

Here are four categories to be aware of:

* Feature changes introduce new functionality. Use prefixes like `feat:` or `add:` when you're building something new - a new API endpoint, a data processing function, or a user-facing feature. Example: `feat: add CSV export for analysis results`.
* Bug fixes solve existing problems. Use `fix:` when you're correcting behavior that didn't work as intended. This could be anything from a null pointer exception to incorrect calculations in your model. Example: `fix: handle missing values in preprocessing pipeline`.
* Documentation updates improve code comments, README files, or inline documentation. Use `docs:` when you're not changing how the code works, just explaining it better. Example: `docs: add usage examples for data loader class`.
* Refactoring and maintenance work improves code structure without changing behavior. Use `refactor:` when you're reorganizing code to make it cleaner or more maintainable. Use `chore:` for routine tasks like updating dependencies or changing build configurations. Examples: `refactor: extract validation logic into separate module` or `chore: update pandas to 3.0.0`.

Pick whichever type best describes your change and move on - consistency matters more than picking the "perfect" label.

## Rules for Writing a Better Git Commit Message

Here's a checklist of rules that'll make your commit messages more useful.

* Keep the subject line under 50 characters. This guarantees it displays properly in `git log --oneline`, GitHub's commit list, and terminal output without truncation. If you can't fit your message in 50 characters, aim for 72 maximum.
* Use the imperative mood. Write "add feature" instead of "added feature" or "adds feature." Your subject line should complete the sentence "If applied, this commit will...". So "If applied, this commit will add caching" reads correctly.
* Separate subject and body with a blank line. Git uses this blank line to distinguish between the summary and detailed explanation. Without it, Git tools might display your message incorrectly.
* Skip the period at the end of the subject line. You're saving characters and the subject line isn't a complete sentence anyway. Write `fix null pointer in loader` instead of `fix null pointer in loader`.
* Capitalize the first word of your subject line. Write `Add caching for API calls` instead of `add caching for API calls`. This keeps your commit history looking consistent and professional.
* Use the body to explain why, not what. The diff shows what changed. Your body should explain the reasoning behind the change, alternative approaches you considered, and any trade-offs you made.
* Wrap body text at 72 characters. This prevents line wrapping issues in terminal output and keeps your commit messages readable across different tools.
* Make each commit atomic. One logical change per commit. If you're fixing a bug and refactoring code, split them into two commits with separate messages.

## Examples of a Good Git Commit Message

Here are real-world examples showing what good commit messages look like for different scenarios.

### A simple fix

```bash
fix: handle NaN values in feature engineering

The preprocessing pipeline crashed when encountering NaN values
in the 'age' column. Added fillna() with median imputation before
scaling features.
```

This works because it identifies the problem (NaN crashes), explains where it happened (preprocessing pipeline, age column), and describes the solution (median imputation).

### A new feature

```bash
feat: add model performance tracking to MLflow

Added automatic logging of model metrics, parameters, and artifacts
to MLflow after each training run. This replaces our manual CSV
logging and makes experiment comparison much easier.

Metrics tracked: accuracy, precision, recall, F1 score
Training time also logged for performance monitoring.
```

Good feature commits explain what you built, why it's useful, and any details that help readers understand the scope.

### A refactor

```bash
refactor: split data_loader.py into separate modules

Moved dataset classes to datasets.py, transformation logic to
transforms.py, and utility functions to utils.py. The original
file was 800+ lines and hard to navigate.

No behavior changes - all tests still pass.
```

Refactor messages should make it clear that you didn't change functionality, just structure. The "all tests still pass" line reassures reviewers.

### A documentation update

```bash
docs: add examples for custom loss functions

Previous documentation showed only built-in loss functions.
Added three examples: weighted cross-entropy, focal loss, and
custom regression loss with L1 regularization.

Each example includes code and explanation of when to use it.
```

Documentation commits should explain what you documented and why it was needed.

### Referencing an issue or ticket

```bash
fix: prevent memory leak in batch processing

Large datasets caused memory usage to grow unbounded during batch
processing. The issue was holding references to processed batches
in the results list.

Changed to yield results instead of accumulating them in memory.
Memory usage now stays constant regardless of dataset size.

Fixes #247
```

When you reference an issue, include enough context that someone can understand the fix without clicking through to the ticket. The `Fixes #247` at the bottom tells GitHub to auto-close the issue when this commits merges.

All examples follow the same pattern: start with what changed, explain why, add context that helps future readers, and reference related issues when relevant.

## Conventional Commits as a Git Commit Message Standard

Conventional commits is a popular format that adds structure to commit messages through a simple prefix pattern.

### Basic format

The format looks like this: `type(scope): description`.

The type describes what kind of change you're making - `feat` for features, `fix` for bug fixes, `docs` for documentation, `refactor` for code restructuring, and so on. The scope is optional and specifies what part of the codebase changed - like `(auth)` or `(api)`. The description explains what you did.

Examples:

```bash
feat(api): add endpoint for batch predictions
fix(auth): prevent token expiration edge case
docs(readme): add installation instructions for Windows
refactor(data): extract validation logic to separate module
```

Just keep in mind that this is a convention, not a requirement. Git doesn't care if you use this format. It mostly comes down to a team decision about how to structure your messages for consistency and tooling.

### When conventional commits are useful

Teams that automate release processes get the most value from conventional commits.

Tools can parse your commit history and automatically generate changelogs. When you tag a release, the tool scans commits since the last release, groups them by type (`feat`, `fix`, `docs`), and creates a formatted changelog. This saves the manual work of tracking what changed between versions.

Conventional commits also support semantic versioning automation. If all your commits since the last release are fixed, the tool bumps the patch version (1.2.3 → 1.2.4). If you added features, it bumps the minor version (1.2.3 → 1.3.0). Breaking changes trigger a major version bump (1.2.3 → 2.0.0).

But if your team doesn't use automated releases or changelog generation, conventional commits might be overkill. The structure helps machines more than humans, so keep that in mind.

## Common Git Commit Message Mistakes to Avoid

Even experienced developers sometimes make mistakes when writing commit messages, but that has more to do with laziness than a lack of knowledge.

Here’s a couple of mistakes you should avoid.

### Vague or generic messages

Messages like "fix bug" or "update code" tell future readers nothing.

When you're searching for a specific change in `git log`, you'll scan through dozens of commits. A message that says "fix bug" forces you to open the diff and read the code to understand what was fixed. A message that says "fix null pointer in data preprocessing" tells you immediately whether this is the commit you're looking for.

Generic messages waste everyone's time. If you can't remember what you changed well enough to write a specific message, you probably shouldn't be committing yet.

### Mixing unrelated changes

One commit should contain one logical change.

When you fix a bug and refactor unrelated code in the same commit, you make code reviews harder and `git bisect` useless. If that commit introduces a regression, someone will have to untangle which part of the change caused it. If they want to [revert](https://www.datacamp.com/tutorial/git-revert-last-commit) just the bug fix, they can't - they'll revert the refactor too.

You should always split changes into separate commits. Fix the bug in one commit, refactor in another. Each commit should be something you could revert independently without breaking the codebase.

If you've already mixed changes locally, use `git add -p` to stage parts of files separately and commit them in logical chunks.

### Leaving work-in-progress messages

Commits with messages like "WIP" or "temp fix" are fine locally but shouldn't make it to the main [branch](https://www.datacamp.com/tutorial/git-branch).

Before merging your feature branch, clean up your commit history. [Squash](https://www.datacamp.com/tutorial/git-squash-commits) WIP commits into meaningful ones with proper messages. Rewrite "asdf" and "trying something" into descriptions that explain what you actually did.

Use `git rebase -i` to combine commits, rewrite messages, and reorder changes before pushing. Your team should see a clean history of what changed and why, not read through your debugging process.

## Best Practices for Teams Using Git Commit Messages

If your team wants to make Git history truly useful, you need consistency. Here are some best practices to follow.

Agree on a shared style early. Decide whether you'll use conventional commits, a custom format, or just a set of basic rules. Pick one approach and stick with it across the entire team. When half your commits say "feat: add feature" and the other half say "Added new feature", your history becomes harder to scan and automation can break.

The style doesn't matter as much as everyone following it. Some teams prefer present tense imperative ("add feature"), others use past tense ("added feature"). Both work fine if applied consistently.

Document your conventions somewhere accessible. Add a CONTRIBUTING.md file to your repo explaining your commit message format with examples. Include it in onboarding docs for new team members. When someone asks "how should I format this commit?", point them to the documentation instead of explaining it again.

Your documentation should cover the basic format you use, when to add a body versus keeping it to just a subject line, how to reference issues or tickets, and a few real examples from your repo.

Use commit messages during code reviews. Good commit messages make pull request reviews faster and more focused. Reviewers can read the commit messages to understand the progression of changes before diving into the code.

When reviewing, check commit messages just like you check code. If a message is vague or misleading, ask for it to be rewritten before merging. A PR with clear commits is easier to review, easier to revert if needed, and easier to understand later.

## Conclusion

A clear commit message takes 30 seconds to write but saves hours of confusion later.

Think of your commit history as documentation that lives with your code. When you write "fix bug" instead of "fix null pointer in data preprocessing", you're wasting time for everyone who reads that commit later - including yourself.

Treat your commit messages like code. If you wouldn’t push sloppy, uncommented code to production, don't push sloppy commit messages either. Use the imperative mood, keep subject lines under 50 characters, explain the why in the body when needed, and make each commit atomic.

Now you know how to write meaningful commit messages. To take your skills to the next level, enroll in our [Intermediate Git](https://www.datacamp.com/courses/intermediate-git) course.

***

![Dario Radečić's photo](https://media.datacamp.com/legacy/v1727011788/image_1_753fadb04d.png?w=128)

Author

Dario Radečić

[](https://www.linkedin.com/in/darioradecic)

Senior Data Scientist based in Croatia. Top Tech Writer with over 700 articles published, generating more than 10M views. Book Author of Machine Learning Automation with TPOT.
