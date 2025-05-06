# Attack Vector Taxonomy

A comprehensive classification system for adversarial techniques targeting large language models, systematically organized to enable structured testing and evaluation.

## Taxonomy Structure

The LART taxonomy organizes attack vectors across five primary dimensions, with hierarchical categorization within each:

1. **Linguistic Manipulation**: Language-based techniques
2. **Context Engineering**: Context-based techniques
3. **System Interaction**: System-level techniques
4. **Functional Exploitation**: Capability-focused techniques
5. **Multi-Modal Vectors**: Cross-modality techniques

Each vector is classified using a multi-level taxonomic code:

```
[Primary Category].[Subcategory].[Specific Technique]
```

Example: `LM.SP.TPM` represents "Linguistic Manipulation > Semantic Patterns > Token Prediction Manipulation"

## 1. Linguistic Manipulation (LM)

Language-based techniques that exploit the model's text processing mechanisms.

### 1.1 Syntactic Patterns (SP)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| LM.SP.DSC | Delimiter-based Syntax Confusion | Exploiting delimiter handling to create syntactic ambiguity | High effectiveness on parsing-sensitive models |
| LM.SP.NES | Nested Structure Exploitation | Using complex nested linguistic structures to confuse parsing | Moderate effectiveness with high model-specificity |
| LM.SP.SYO | Syntactic Obfuscation | Deliberate syntactic complexity to mask intent | Variable effectiveness based on model training |
| LM.SP.TPM | Token Prediction Manipulation | Exploiting token prediction biases | High effectiveness with detailed model knowledge |
| LM.SP.BDM | Boundary Marker Disruption | Manipulating text boundary markers | Effective against models with rigid parsing rules |

### 1.2 Semantic Patterns (SM)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| LM.SM.PSB | Polysemy-based Semantic Bypass | Exploiting multiple word meanings to bypass filters | Highly effective for concept obfuscation |
| LM.SM.ISA | Indirect Semantic Association | Creating indirect associations to evade direct detection | Moderate effectiveness, high model variance |
| LM.SM.CRS | Conceptual Redirection through Synonymy | Using synonyms to redirect processing | Varies based on model's semantic understanding |
| LM.SM.SCF | Semantic Confusion through Framing | Creating semantic ambiguity through framing | Effective against models with rigid word associations |
| LM.SM.IMC | Implicit Meaning Construction | Building meaning through implication rather than direct statements | High effectiveness against literal filters |

### 1.3 Pragmatic Patterns (PP)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| LM.PP.IMP | Implicature Exploitation | Exploiting implied meaning beyond literal words | Highly effective against content filters |
| LM.PP.PRE | Presupposition Embedding | Embedding assumptions that bypass scrutiny | Effective for indirect suggestion |
| LM.PP.ISA | Indirect Speech Acts | Using indirect speech acts to mask intent | Variable effectiveness based on model training |
| LM.PP.CSM | Conversational Maxim Manipulation | Exploiting conversational norms | Moderate effectiveness on conversation-tuned models |
| LM.PP.PCM | Pragmatic Context Manipulation | Manipulating pragmatic context interpretation | Complex implementation, high potential impact |

## 2. Context Engineering (CE)

Techniques that manipulate the context in which content is processed.

### 2.1 Authority Framing (AF)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| CE.AF.RSI | Role-based System Impersonation | Impersonating system roles or authorities | Highly effective against many models |
| CE.AF.EAM | Expert Authority Masking | Using expert personas to establish credibility | Moderate effectiveness on specialized domains |
| CE.AF.OVP | Oversight/Verification Personas | Creating oversight or verification contexts | Effective for policy bypass scenarios |
| CE.AF.DSR | Development/System Roles | Adopting development or system maintenance personas | High effectiveness for system instruction access |
| CE.AF.HPI | Hierarchical Position Invocation | Establishing hierarchical authority positions | Variable effectiveness based on role hierarchy |

### 2.2 Context Poisoning (CP)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| CE.CP.GPS | Gradual Perspective Shifting | Slowly shifting conversation context | Highly effective in multi-turn scenarios |
| CE.CP.CBB | Context Building Blocks | Building complex context through incremental blocks | Moderate effectiveness, high persistence |
| CE.CP.FCM | False Context Manipulation | Establishing false background context | Effective for framing subsequent content |
| CE.CP.PCO | Progressive Context Overriding | Gradually overriding established context | High effectiveness in extended conversations |
| CE.CP.CAA | Context Anchor Attacks | Establishing strong contextual anchors | Effective for persistent context control |

### 2.3 Narrative Manipulation (NM)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| CE.NM.SMC | Story-based Meaning Construction | Using narrative to construct meaning | Highly effective for indirect content |
| CE.NM.CFN | Counterfactual Narratives | Creating hypothetical scenarios to bypass filters | Effective for policy boundary testing |
| CE.NM.CDF | Character Development Framing | Developing characters with specific attributes | Moderate effectiveness for role distancing |
| CE.NM.NPP | Narrative Perspective Positioning | Positioning the model within specific narrative roles | Variable effectiveness based on role complexity |
| CE.NM.NDB | Narrative Distance Buffering | Creating narrative distance from sensitive content | Effective for content policy evasion |

## 3. System Interaction (SI)

Vectors targeting system-level interactions and infrastructure.

### 3.1 Instruction Manipulation (IM)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| SI.IM.SPE | System Prompt Extraction | Techniques to reveal system instructions | High value, variable success rate |
| SI.IM.SPI | System Prompt Injection | Injecting new system-level instructions | High impact when successful |
| SI.IM.ICF | Instruction Conflict Forcing | Creating conflicting instruction states | Effective for boundary testing |
| SI.IM.ISB | Instruction Set Boundary Testing | Probing boundaries of instruction sets | Valuable for system understanding |
| SI.IM.PMO | Parameter Modification | Attempting to modify system parameters | Low success rate, high potential impact |

### 3.2 Format Exploitation (FE)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| SI.FE.DMC | Delimiter Confusion | Exploiting delimiter handling issues | Effective against structured response models |
| SI.FE.FFM | Format-Field Manipulation | Manipulating structured format fields | Moderate effectiveness on format-sensitive models |
| SI.FE.FSI | Format-Specific Injection | Injecting commands via format structures | High variability across models |
| SI.FE.SMM | Special Marker Manipulation | Exploiting special markers or tags | Effective on models with special tokens |
| SI.FE.FBP | Format Boundary Probing | Testing boundaries between formats | Useful for discovery purposes |

### 3.3 Infrastructure Targeting (IT)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| SI.IT.RLE | Rate Limit Exploitation | Exploiting rate limiting mechanisms | Useful for availability testing |
| SI.IT.CWM | Context Window Manipulation | Manipulating context window handling | Effective on models with large contexts |
| SI.IT.APM | API Parameter Manipulation | Testing API parameter boundaries | Important for integration security |
| SI.IT.CEM | Cache Exploitation Methods | Targeting caching mechanisms | Varies based on implementation |
| SI.IT.PCE | Processing Chain Exploitation | Targeting multi-stage processing | Complex implementation, high potential impact |

## 4. Functional Exploitation (FE)

Techniques targeting specific model capabilities and functions.

### 4.1 Tool Manipulation (TM)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| FE.TM.TPI | Tool Prompt Injection | Injecting prompts via tool interfaces | Highly effective on tool-enabled models |
| FE.TM.TFM | Tool Function Misuse | Misusing legitimate tool functions | Moderate effectiveness, model-specific |
| FE.TM.TCE | Tool Chain Exploitation | Exploiting chains of tool calls | Complex implementation, high potential impact |
| FE.TM.TPE | Tool Parameter Exploitation | Manipulating tool parameters | Effective for parameter-sensitive tools |
| FE.TM.TAB | Tool Authentication Bypass | Bypassing tool authentication mechanisms | Low success rate, high impact |

### 4.2 Output Manipulation (OM)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| FE.OM.OFM | Output Format Manipulation | Manipulating output formatting | Effective for presentation bypass |
| FE.OM.SSI | Structured Schema Injection | Injecting content via structured schemas | Variable effectiveness across models |
| FE.OM.OPE | Output Parser Exploitation | Targeting output parsing mechanisms | Implementation-specific effectiveness |
| FE.OM.CTM | Content-Type Manipulation | Manipulating content type handling | Effective for format-based filtering bypass |
| FE.OM.RDM | Response Delimiter Manipulation | Exploiting response delimiter handling | Effective on structured response models |

### 4.3 Capability Access (CA)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| FE.CA.HAC | Hidden API Capability Access | Accessing hidden API capabilities | High value, low success rate |
| FE.CA.RCA | Restricted Capability Activation | Activating restricted capabilities | Model-specific effectiveness |
| FE.CA.EMU | Emulation-based Capability Unlocking | Emulating privileged contexts | Moderate effectiveness on context-sensitive models |
| FE.CA.FCE | Function Call Exploitation | Exploiting function calling mechanisms | Effective on function-enabled models |
| FE.CA.MCB | Model Capability Boundary Testing | Testing boundaries of model capabilities | Valuable for capability mapping |

## 5. Multi-Modal Vectors (MM)

Cross-modal attack techniques targeting multi-modal AI systems.

### 5.1 Vision-Language Exploitation (VL)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| MM.VL.TII | Text-in-Image Injection | Embedding text commands in images | Highly effective against many vision-language models |
| MM.VL.VCM | Visual Context Manipulation | Using images to establish misleading context | Moderate effectiveness, implementation-dependent |
| MM.VL.OCR | OCR Exploitation Techniques | Exploiting OCR processing mechanisms | Variable effectiveness based on OCR quality |
| MM.VL.VPM | Visual Perception Manipulation | Using visual perception principles to hide content | Complex implementation, medium effectiveness |
| MM.VL.MIM | Modal Inconsistency Manipulation | Creating inconsistencies between vision and language | Effective for boundary testing |

### 5.2 Audio-Language Exploitation (AL)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| MM.AL.PSE | Psychoacoustic Embedding | Embedding content using psychoacoustic principles | Complex implementation, variable effectiveness |
| MM.AL.AST | ASR Transcription Manipulation | Exploiting speech-to-text mechanisms | Effectiveness depends on ASR quality |
| MM.AL.HAC | Homophone-based Acoustic Confusion | Using homophones to create acoustic confusion | Moderate effectiveness on ASR-dependent models |
| MM.AL.AMT | Audio Metadata Targeting | Exploiting audio metadata handling | Implementation-specific effectiveness |
| MM.AL.AVM | Audio-Visual Mismatch Exploitation | Creating mismatches between audio and visual content | Effective for multi-modal consistency testing |

### 5.3 Code Integration Vectors (CI)

| Code | Technique | Description | Effectiveness Profile |
|------|-----------|-------------|----------------------|
| MM.CI.CEV | Code Execution Vector | Attempting code execution through interfaces | High impact, generally low success rate |
| MM.CI.CIE | Code Interpretation Exploitation | Exploiting code interpretation mechanisms | Effective on code-enabled models |
| MM.CI.CMI | Code-Markdown Integration Issues | Exploiting code-markdown boundary handling | Effective for documentation-heavy contexts |
| MM.CI.CSI | Code Snippet Injection | Injecting malicious code snippets | Variable effectiveness based on code handling |
| MM.CI.CEE | Code Environment Exploitation | Exploiting code execution environments | Implementation-specific effectiveness |
