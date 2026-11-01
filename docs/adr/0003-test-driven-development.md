# ADR-0003: Test-driven development, with a defined exception for research spikes

Status: accepted
Date: 2026-11-01

## Context
Sparkgap exists to tell developers the truth about how a payment API
behaves, so incorrect behavior in the tool is worse than missing behavior.
A mock that accepts a bad request teaches the wrong lesson, and a doctor
check that gives a false pass hides a real fault. Contributors also need an
executable description of what each component is supposed to do.

Some work cannot be test-driven at the start, because the behavior of the
external system is not yet known. Day 0 experiments against the Daraja
sandbox are of this kind.

## Decision
All production code under src/ is written test first, following red, green,
refactor:

1. Write a test that describes the behavior and confirm it fails for the
   expected reason.
2. Write the smallest implementation that makes it pass.
3. Refactor with the tests passing.

The test and its implementation are committed together, so that every
commit remains green as required by ADR-0002. A bug fix begins with a test
that reproduces the bug.

Unit tests never use the network. HTTP behavior is tested with respx. Tests
that call the real Daraja sandbox carry the `live` marker and are excluded
from the default CI run. The marker will be registered in pyproject.toml in
the commit that adds the first live test.

Research spikes are exempt. A spike is exploratory code written to learn
how an external system behaves, such as the callback capture server. Spikes
live under scripts/ or docs/research/, say that they are spikes, and are not
imported by src/. Code promoted from a spike into src/ is rewritten test
first, using the recorded behavior as the specification.

CI reports coverage on every run. A minimum threshold for core logic will be
set by a later decision, once there is enough code for a number to mean
something.

## Alternatives considered
Tests written after the implementation. This is faster for a single change,
but tests then tend to confirm what the code does instead of what it should
do, and untested branches are common.

A separate commit for the failing test. It makes the red step visible in
history, but the commit fails CI and breaks the rule in ADR-0002 that every
commit is green.

A coverage threshold as the only control. It measures lines executed, not
behavior verified, and it is easy to satisfy with tests that assert nothing.

Test-driven development for everything, including spikes. Tests written
before the behavior of the sandbox is known would encode guesses, and they
would slow down the experiments whose purpose is to replace guesses with
evidence.

## Consequences
Easier: changing code with confidence, reviewing a pull request by reading
the tests first, and onboarding contributors, because the tests describe the
intended behavior.

Harder: each change costs more up front, and contributors unfamiliar with the
practice need guidance, which CONTRIBUTING.md provides.

Limits of enforcement: CI cannot verify that a test was written first. It can
only show that tests exist and pass. Reviewers check that behavior changes
arrive with tests in the same commit.

Risk of wrong tests: a test is only as accurate as the assumption behind it.
A test written against a mistaken belief about Daraja will pass while
encoding the mistake. Daraja facts are therefore labelled verified or
community-reported, and tests for verified behavior are based on recorded
sandbox responses where possible.

Risk to the spike boundary: spike code can drift into src/ without tests if
the boundary is not respected. The rule that src/ never imports from scripts/
and that promotion means a test-first rewrite is checked in review.
