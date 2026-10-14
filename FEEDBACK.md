# Feedback on Nebius Token Factory, Nebius AI Cloud, and NVIDIA tools

A running log kept from day one. The hackathon requires this section; we keep it honest and specific.

## Onboarding
- 2026-10-13: Credits: promo code route and Builders Program route both documented on Devpost resources; balance confirmation pending.
- Time from zero to first successful Token Factory call: (fill in after `make smoke`).

## What worked

## What needs work
- Model catalog metadata shows 0 parameters for Super and Ultra in the markdown catalog; NVIDIA figures used instead.
- Nemotron models do not carry the JSON-mode tag; we used tool calling for structured output. A documented guarantee for `response_format=json_schema` on Nemotron would remove a workaround.
- No official Nebius doc page covers `chat_template_kwargs.enable_thinking` for Nemotron; we found it in NVIDIA docs and community repos.
- Vision Nemotron (Nano Omni, Nano VL) is not on shared serverless endpoints since the Aug 31 2026 deprecation; teams must self-host on a Serverless Endpoint or use a non-NVIDIA image2text model.

## Would we build with it again

## Tavily

## NVIDIA models

## Tavily (2026-10-14)
- Signup to first successful search with `tavily-python`: under five minutes, no card. `include_domains` worked well for restricting parts searches to suppliers and manual searches to known mirrors.
- The agent-setup SKILL.md on tavily.com pushes CLI install, browser login and global skill installation; for an application that only needs the SDK and an env var, the Path B section was the only part needed. A shorter "I just want the SDK" entry point would save time.
- What worked: a brand-name query for a pesticide returned regulator and supplier pages with the active ingredient in the title on the first try.
