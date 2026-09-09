# Neverinstall Signal Engine

A signal-based GTM research and prioritization engine built for Neverinstall.

The system researches target accounts, identifies qualified customer and
partner signals, evaluates evidence quality and recency, scores account fit,
determines actionability, and produces a ranked research/outbound queue.

---

## What this solves

Traditional prospecting often starts with:

> "Who should I contact?"

This engine starts with:

> "What changed or what technology evidence makes this account worth
> contacting?"

It is designed to reduce noisy prospecting by separating:

- Direct technology signals
- Supporting business signals
- Customer fit
- Partner fit
- Evidence strength
- Evidence recency
- Identity confidence
- Account priority
- Actionability

The result is a ranked account list that tells a BDR **what to investigate,
who to target, and why the account matters.**

---

## Architecture

```text
                    ┌─────────────────────┐
                    │    accounts.csv     │
                    │ Company + Region    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Research        │
                    │ OpenAI + Web Search  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Identity Resolution │
                    │ Customer / Partner  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Customer Signals│          │ Partner Signals │
       │ Citrix / VDI    │          │ SI / MSP / VDI  │
       │ AVD / Horizon   │          │ Cloud / Channel │
       └────────┬────────┘          └────────┬────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Evidence Layer      │
                    │ Strength + Recency  │
                    │ Sources              │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Validation          │
                    │ Schema + Guardrails  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Scoring             │
                    │ Fit + Combinations  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Actionability       │
                    │ HIGH / MEDIUM / LOW │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Outbound Brief      │
                    │ Buyer + Why Now     │
                    │ Neverinstall Angle  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Trigger Ranking     │
                    │ BDR Research Queue  │
                    └─────────────────────┘