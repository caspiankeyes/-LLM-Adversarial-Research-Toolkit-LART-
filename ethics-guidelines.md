# Ethics Guidelines for Responsible Disclosure

This document outlines the ethical principles, responsibilities, and protocols that guide research and disclosure activities within the LART framework. All researchers utilizing LART are expected to adhere to these guidelines to ensure that security research advances safety without enabling harm.

## Core Ethical Principles

LART research adheres to six foundational ethical principles:

### 1. Do No Harm

**Principle**: Security research should advance safety, not enable malicious actors.

**Implementation**:
- All research must have defensive intent
- Vulnerabilities must be paired with mitigations
- Potential harms must be minimized in all research activities

**Verification**:
- Document intended defensive purpose before research begins
- Conduct harm assessment before publication
- Review mitigation adequacy before disclosure

### 2. Responsible Disclosure

**Principle**: Vulnerabilities should be disclosed in a manner that prioritizes remediation before public awareness.

**Implementation**:
- Follow structured disclosure timelines
- Provide clear reproduction steps to vendors
- Collaborate on remediation approaches

**Verification**:
- Maintain disclosure documentation
- Track vendor engagement
- Document remediation progress

### 3. Minimize Exposure

**Principle**: Sensitive details should be limited to necessary parties until mitigations are available.

**Implementation**:
- Restrict sensitive information distribution
- Redact unnecessary exploitation details
- Time disclosures to coincide with mitigations

**Verification**:
- Track information distribution
- Conduct pre-publication redaction reviews
- Assess potential exposure impact

### 4. Consent and Transparency

**Principle**: Research should be conducted with appropriate consent and transparency.

**Implementation**:
- Obtain necessary authorizations before testing
- Clearly communicate research intentions
- Adhere to terms of service and legal requirements

**Verification**:
- Document consent processes
- Maintain authorization records
- Conduct legal compliance reviews

### 5. Accountability

**Principle**: Researchers must take responsibility for their findings and how they are communicated.

**Implementation**:
- Maintain clear attribution of research
- Stand by accuracy of findings
- Accept responsibility for disclosure impacts

**Verification**:
- Document research attribution
- Verify finding accuracy
- Assess disclosure impacts

### 6. Continuous Improvement

**Principle**: Ethical practices should evolve based on feedback and outcomes.

**Implementation**:
- Regularly review and update ethical guidelines
- Incorporate lessons from past disclosures
- Adapt practices to emerging challenges

**Verification**:
- Schedule regular ethics reviews
- Document lessons learned
- Track ethics evolution

## Structured Disclosure Protocol

LART implements a five-phase approach to responsible disclosure:

### Phase 1: Initial Assessment

**Objective**: Evaluate vulnerability severity and impact.

| Activity | Requirement | Documentation |
|----------|-------------|---------------|
| Risk Assessment | Complete RAMP scoring | Risk assessment document |
| Impact Analysis | Identify affected systems and users | Impact report |
| Mitigation Evaluation | Assess mitigation feasibility | Mitigation assessment |
| Disclosure Planning | Develop preliminary disclosure plan | Draft disclosure plan |

**Stakeholders**: Research team, ethics advisor

**Timeline**: Immediately following discovery

### Phase 2: Vendor Notification

**Objective**: Inform affected vendors and provide necessary details for remediation.

| Activity | Requirement | Documentation |
|----------|-------------|---------------|
| Initial Contact | Establish secure communication channel | Contact record |
| Vulnerability Report | Provide detailed vulnerability information | Vulnerability report |
| Reproduction Guidance | Supply clear reproduction steps | Reproduction guide |
| Timeline Negotiation | Establish mutually agreeable timeline | Timeline agreement |

**Stakeholders**: Research team, vendor security teams

**Timeline**: Within 7 days of confirmation

### Phase 3: Remediation Period

**Objective**: Allow time for vulnerability remediation before public disclosure.

| Activity | Requirement | Documentation |
|----------|-------------|---------------|
| Remediation Support | Provide technical assistance as needed | Support record |
| Verification Testing | Test proposed mitigations | Test results |
| Timeline Monitoring | Track progress against agreed timeline | Progress tracker |
| Coordination | Maintain communication with all affected parties | Communication log |

**Stakeholders**: Research team, vendor security teams

**Timeline**: 30-90 days based on severity and complexity

### Phase 4: Public Disclosure

**Objective**: Share findings publicly in a responsible manner.

| Activity | Requirement | Documentation |
|----------|-------------|---------------|
| Disclosure Preparation | Prepare public disclosure materials | Disclosure package |
| Sensitive Information Review | Review for unnecessary sensitive details | Redaction assessment |
| Coordinated Release | Coordinate timing with vendors | Release plan |
| Mitigation Documentation | Include clear mitigation guidance | Mitigation guide |

**Stakeholders**: Research team, vendor security teams, security community

**Timeline**: After remediation completion or agreed timeline expiration

### Phase 5: Post-Disclosure Support

**Objective**: Provide ongoing support following public disclosure.

| Activity | Requirement | Documentation |
|----------|-------------|---------------|
| Query Handling | Respond to questions about findings | Query log |
| Additional Guidance | Provide supplementary information as needed | Guidance record |
| Impact Monitoring | Track real-world impact of disclosure | Impact assessment |
| Lessons Documentation | Document lessons learned | Lessons report |

**Stakeholders**: Research team, security community

**Timeline**: 30+ days following public disclosure

## Ethical Decision Framework

When faced with ethical dilemmas in security research, LART researchers should apply the following structured decision framework:

### 1. Identify the Ethical Question

- What is the core ethical dilemma?
- What principles are in tension?
- Who are the stakeholders affected?

### 2. Gather Relevant Information

- What are the potential harms and benefits?
- What precedents exist for similar situations?
- What are stakeholder perspectives?

### 3. Consider Alternative Approaches

- What disclosure options are available?
- How do different approaches balance security and risk?
- What creative solutions might address multiple concerns?

### 4. Apply Ethical Principles

- How does each option align with core principles?
- Which approach minimizes harm while advancing safety?
- What approach would be defensible to all stakeholders?

### 5. Make and Document the Decision

- Document the decision and rationale
- Record dissenting perspectives
- Establish evaluation criteria for outcomes

### 6. Evaluate the Outcome

- Assess actual outcomes against predictions
- Document lessons learned
- Incorporate insights into future decisions

## Special Considerations for LLM Research

LLM security research presents unique ethical challenges that require specific consideration:

### 1. Dual-Use Concerns

LLM vulnerabilities often have stronger dual-use potential than traditional security research, as exploitation techniques may be directly applicable with minimal modification.

**Guidelines**:
- Apply heightened scrutiny to disclosure details
- Emphasize conceptual understanding over specific implementations
- Pair all vulnerability disclosures with robust mitigations

### 2. Scale of Impact

Vulnerabilities in widely deployed LLMs can affect millions of users simultaneously.

**Guidelines**:
- Consider impact scale in disclosure timing
- Prioritize coordination with vendors
- Establish impact thresholds for disclosure approaches

### 3. Rapidly Evolving Field

AI security is a rapidly evolving field with limited established norms.

**Guidelines**:
- Consult multiple stakeholders for novel ethical questions
- Document reasoning for future reference
- Consider precedent-setting implications of decisions

### 4. Emergent Risk Assessment

LLM risks may be emergent and difficult to predict.

**Guidelines**:
- Apply conservative risk estimates
- Consider worst-case scenarios
- Implement staged disclosure for novel risk categories

## Research Limitations

LART researchers self-impose the following limitations to ensure ethical conduct:

### 1. No Malicious Deployment

**Limitation**: Findings must never be deployed for malicious purposes.

**Implementation**:
- Research findings are used solely for defensive purposes
- Documentation emphasizes defensive applications
- Code samples include safety mechanisms

**Verification**:
- Conduct deployment risk assessments
- Monitor for misuse of published techniques
- Document defensive intent for all projects

### 2. Limited Distribution

**Limitation**: Sensitive information is shared only with necessary parties.

**Implementation**:
- Establish information classification system
- Implement access controls for sensitive details
- Verify recipient need-to-know

**Verification**:
- Track information distribution
- Conduct periodic access reviews
- Document distribution decisions

### 3. Complete Documentation

**Limitation**: All security research must be thoroughly documented.

**Implementation**:
- Document all testing processes
- Record findings comprehensively
- Maintain decision logs

**Verification**:
- Review documentation completeness
- Verify reproducibility from documentation
- Assess documentation clarity

### 4. Defense Pairing

**Limitation**: All vulnerabilities must be paired with defensive mitigations.

**Implementation**:
- Develop mitigations for all discovered vulnerabilities
- Test mitigation effectiveness
- Document implementation guidance

**Verification**:
- Verify mitigation coverage
- Test mitigation effectiveness
- Assess implementation feasibility

### 5. Proportional Testing

**Limitation**: Testing scope must be proportional to research necessity.

**Implementation**:
- Limit testing to necessary vectors
- Minimize data exposure
- Bound automation scope

**Verification**:
- Review testing proportionality
- Assess necessity of scale
- Document scope justification

## Ethical Governance Structure

LART implements the following governance structure to ensure ethical oversight:

### 1. Ethics Advisory Role

An ethics advisor with relevant expertise reviews all significant research projects.

**Responsibilities**:
- Review research proposals
- Advise on ethical dilemmas
- Approve public disclosures

**Independence**:
- Independent from research teams
- Authority to delay or modify disclosures
- Direct reporting to leadership

### 2. Peer Review Process

All research undergoes peer review focused on ethical considerations.

**Process**:
- Minimum two-reviewer requirement
- Explicit ethics evaluation
- Pre-disclosure review gate

**Documentation**:
- Record review findings
- Document addressed concerns
- Maintain review history

### 3. External Consultation

Complex ethical questions are referred to external experts.

**Triggers**:
- Novel ethical questions
- High-impact vulnerabilities
- Disagreement among internal reviewers

**Implementation**:
- Maintain expert network
- Document consultation outcomes
- Incorporate external perspectives

## Accountability Mechanisms

LART maintains several accountability mechanisms:

### 1. Disclosure Review Board

A board reviews all significant disclosures before publication.

**Composition**:
- Ethics advisor
- Technical experts
- External representative

**Function**:
- Review disclosure plans
- Approve timing and content
- Document decisions

### 2. Post-Disclosure Assessment

All disclosures undergo post-publication impact assessment.

**Evaluation Criteria**:
- Actual versus predicted impact
- Vendor response adequacy
- Community reception
- Misuse incidents

**Application**:
- Document lessons learned
- Update guidelines based on outcomes
- Track disclosure effectiveness

### 3. Compliance Verification

Periodic audits verify adherence to ethical guidelines.

**Process**:
- Regular compliance reviews
- Documentation verification
- Process adherence checking

**Outcomes**:
- Compliance reports
- Remediation recommendations
- Process improvements

## Special Protocols for High-Risk Vulnerabilities

For vulnerabilities with exceptional risk profiles (RAMP score ≥ 8.5), LART implements enhanced protocols:

### 1. Enhanced Vendor Coordination

**Process**:
- Expedited notification
- Direct escalation to senior security personnel
- Closer collaboration on mitigation development

**Timeline**:
- Initial notification within 24 hours
- Daily status updates
- Coordinated emergency response

### 2. Limited Disclosure

**Approach**:
- Phased information release
- Conceptual-level initial disclosure
- Detailed disclosure after confirmed mitigations

**Implementation**:
- Information compartmentalization
- Stepped disclosure timeline
- Verification of mitigation deployment

### 3. Post-Deployment Monitoring

**Activities**:
- Active monitoring for exploitation
- Rapid response to observed misuse
- Ongoing effectiveness assessment

**Timeframe**:
- Intensive monitoring for 30+ days post-disclosure
- Regular monitoring for 90+ days
- Longitudinal impact assessment

## Legal and Regulatory Considerations

LART research adheres to applicable laws and regulations:

### 1. Jurisdiction Awareness

**Requirement**:
- Understand relevant laws in researcher and vendor jurisdictions
- Comply with applicable regulations
- Consider cross-border implications

**Implementation**:
- Jurisdiction-specific guidance
- Legal consultation for complex cases
- Documentation of compliance measures

### 2. Terms of Service Compliance

**Requirement**:
- Respect vendor terms of service
- Obtain necessary permissions
- Work within official security research policies

**Implementation**:
- Review relevant terms before testing
- Document compliance approach
- Engage with vendor security programs

### 3. Data Protection

**Requirement**:
- Protect personal and sensitive data
- Comply with data protection regulations
- Minimize unnecessary data exposure

**Implementation**:
- Data minimization practices
- Secure handling protocols
- Appropriate anonymization

## Educational Responsibility

LART researchers recognize their educational responsibility:

### 1. Security Advancement

**Objective**: Advance the state of LLM security knowledge.

**Implementation**:
- Document general security principles
- Share defensive methodologies
- Build security community knowledge

### 2. Ethical Skill Development

**Objective**: Develop ethical security research skills.

**Implementation**:
- Mentor emerging researchers
- Document ethical decision processes
- Share case studies for learning

### 3. Responsible Practice Advocacy

**Objective**: Promote responsible security research practices.

**Implementation**:
- Advocate for responsible disclosure
- Demonstrate ethical research processes
- Contribute to industry standards

## Continuous Improvement Process

LART ethics guidelines evolve through a structured improvement process:

### 1. Regular Reviews

**Frequency**: Quarterly and event-triggered reviews

**Process**:
- Review recent disclosures
- Assess guideline effectiveness
- Identify improvement opportunities

### 2. Feedback Integration

**Sources**:
- Researcher experiences
- Vendor feedback
- Community input
- External expert consultation

**Process**:
- Systematically collect feedback
- Analyze for patterns
- Develop improvement proposals

### 3. Documentation Updates

**Approach**:
- Version-controlled documentation
- Clear change tracking
- Transition guidance for significant changes

**Implementation**:
- Regular documentation updates
- Change communication
- Historical record maintenance

## Conclusion

Ethical responsibility is fundamental to effective security research. By adhering to these guidelines, LART researchers contribute to a safer AI ecosystem while demonstrating that security advancement and ethical practice are complementary, not competing, objectives. As the field evolves, these guidelines will continue to develop through a commitment to continuous improvement and stakeholder engagement.
