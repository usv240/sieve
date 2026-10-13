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
