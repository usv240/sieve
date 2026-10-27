/** Every sponsor tool and model Sieve uses, what it does here, and where it runs. Status is what we verified, not what we plan. */
export type StackItem = { name: string; role: string; status: "live" | "laptop" | "nebius" | "prepared"; href: string };

export const STACK: StackItem[] = [
  { name: "Nebius Token Factory", role: "Serves every cloud model call: reading photos, writing the repair plan, auditing it, labelling each step. Tokens and cost of every call are shown in the Trace panel.", status: "live", href: "https://tokenfactory.nebius.com" },
  { name: "NVIDIA Nemotron 3.5 Super VL", role: "Reads the nameplate and the alarm lights from a photo. A second, different model reads it again, and Sieve opens a manual on its own only when both agree.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3 Nano", role: "The fast tier: picks intake questions and checks whether the manual itself states each step.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3 Super", role: "Writes the repair plan, pointing every step at a numbered sentence of the manual.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3 Ultra", role: "Audits the whole plan against the complete service manual in one 1-million-token context.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3.5 Lightning", role: "Reads the whole fleet log plus 647 FDA reports in one 140,000-token call to write the weekly district brief.", status: "live", href: "/fleet" },
  { name: "NVIDIA Nemotron Nano 9B v2 and 12B v2 VL", role: "Offline mode: the same pipeline on a laptop GPU through llama.cpp, with no internet.", status: "laptop", href: "/limits" },
  { name: "Tavily", role: "Finds parts for the cited fault, and finds and indexes a service manual when Sieve has none.", status: "live", href: "/how-it-works" },
  { name: "Hermes Agent", role: "Runs Sieve as tools for an agent, and runs a scheduled watch that matches new FDA recalls to the fleet.", status: "laptop", href: "https://github.com/usv240/sieve/tree/main/infra/hermes" },
  { name: "NVIDIA OpenShell", role: "Ran the Sieve agent in a sandbox with brokered credentials, so the agent never sees the API key.", status: "laptop", href: "https://github.com/usv240/sieve/tree/main/infra/openshell" },
  { name: "MCP", role: "Eight Sieve tools any agent can call: identify, analyze, page lookup, recalls, training panel and more.", status: "laptop", href: "/api" },
  { name: "Nebius Serverless", role: "A Serverless Job on a clean Nebius machine cloned both public repos, ran every test and published safety check, and called both live APIs: PASS. A Serverless Endpoint served NVIDIA's open Nemotron Nano 12B v2 VL with vLLM, and both photo benchmarks were rerun with it as the only reader. Both were stopped after use to save credits; the scripts to start them again are in the repo.", status: "nebius", href: "https://github.com/usv240/sieve/tree/main/infra" },
];
