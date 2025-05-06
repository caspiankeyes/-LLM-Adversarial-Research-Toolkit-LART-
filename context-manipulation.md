# Context Manipulation Attack Vectors

This document provides a comprehensive analysis of context-based manipulation techniques that exploit how large language models process and interpret contextual information. These vectors focus on authority framing, context poisoning, and narrative manipulation to influence model behavior.

## Overview

Context engineering attack vectors exploit the context-dependent nature of language model processing. By manipulating the contextual frame within which content is interpreted, these attacks can influence model behavior, bypass security controls, extract unauthorized information, or manipulate responses in ways that standard content filtering might miss.

Unlike linguistic manipulation vectors that focus primarily on language structure and meaning, context engineering targets the broader interpretive frameworks that LLMs use to understand and respond to inputs. These vectors are particularly powerful because they operate on the model's interpretive mechanisms rather than just its language processing capabilities.

| Vector Category | Description | Primary Target | Common Applications |
|-----------------|-------------|----------------|---------------------|
| Authority Framing | Establishing perceived authority or special roles | Role interpretation | System prompt access, policy bypass |
| Context Poisoning | Gradually manipulating conversation context | Context windows | Progressive manipulation, defense evasion |
| Narrative Manipulation | Using narrative structures to alter interpretation | Content interpretation | Policy bypass, indirect instruction |

## Key Principles

Context engineering vectors operate based on several key principles:

1. **Context Dependence**: LLMs interpret content based on surrounding context, creating vulnerability to context manipulation
2. **Role Sensitivity**: Models respond differently based on perceived roles and authorities in a conversation
3. **Persistence Effects**: Context established early in a conversation can influence later interpretations
4. **Narrative Framing**: Models are influenced by narrative structures that frame information interpretation
5. **Implicit Authority**: Models can be influenced by explicitly or implicitly established authority structures

### Exploitation Fundamentals

| Principle | Exploitation Mechanism | Example Technique |
|-----------|------------------------|-------------------|
| Context Dependence | Manipulating surrounding context to alter interpretation | Context poisoning, false context establishment |
| Role Sensitivity | Establishing false authorities or special roles | Role-based system impersonation, expert authority masking |
| Persistence Effects | Creating persistent context that influences future interpretations | Context anchoring, gradual perspective shifting |
| Narrative Framing | Using narrative structures to alter content interpretation | Story-based meaning construction, counterfactual narratives |
| Implicit Authority | Leveraging implicit authority structures | Hierarchical position invocation, oversight personas |
