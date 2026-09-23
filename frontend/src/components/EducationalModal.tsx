import React, { useState } from 'react'
import {
  X,
  Layers,
  ChevronRight,
  Code2,
  Sparkles,
  Compass
} from 'lucide-react'

interface EducationalModalProps {
  isOpen: boolean
  onClose: () => void
}

export const EducationalModal: React.FC<EducationalModalProps> = ({ isOpen, onClose }) => {
  const [activeStep, setActiveStep] = useState<number>(0)

  if (!isOpen) return null

  const steps = [
    {
      id: 'pipeline-overview',
      number: '01',
      title: 'High-Level Architecture & Principles',
      subtitle: 'Why traditional LLM prompting fails for assignments and how grounded RAG solves it.',
      concept: 'Grounded RAG vs Direct LLM Prompting',
      description: 
`If you simply paste an entire 30-page assignment draft into ChatGPT with the prompt "Grade this against the rubric", three major problems occur:
1. Context Window Degradation: Large drafts cause models to skim or forget details buried in middle sections ("Lost in the Middle").
2. Flattery Bias & Hallucinated Grades: LLMs tend to be overly generous or fabricate arbitrary letter grades (HD, Credit) without objective justification.
3. Zero Evidence Traceability: The model might state "You lacked cloud architecture comparisons", but cannot point to the exact paragraph, chunk ID, or page in your draft.

Our Architecture Solution:
We decouple the assessment into a 10-stage deterministic pipeline:
- Document structure and hierarchy are extracted and preserved.
- Requirements and rubric criteria are converted into strict typed JSON schemas.
- The student draft is section-chunked and embedded into a local vector database (ChromaDB).
- For each criterion, the system runs Targeted Semantic Retrieval (Top-k).
- The LLM receives only the specific criterion and retrieved candidate chunks, enforcing that every judgment cite verbatim quotes, chunk IDs, and page numbers.`,
      mathOrLogic: `P(Criterion_i | Document) ≈ ∑_{c ∈ TopK(Embed(Criterion_i), Chunks)} LLM(EvalSchema, c, Criterion_i)`,
      exampleFileReference: {
        specDoc: 'Macquarie University COMP8240 Assessment Task 1',
        studentDraft: "Tony's VADER Sentiment Pipeline Proposal",
        detail: 'The spec requires "Critically evaluate two architectural options". Direct LLMs might miss that Section 3.2 only evaluated one option. Our RAG engine specifically queries "architectural options comparison", extracts chunk #4 (page 3), notes only AWS Lex was analyzed, and flags it as PARTIAL with 0.88 confidence.'
      }
    },
    {
      id: 'ingestion-chunking',
      number: '02',
      title: 'Document Ingestion & Section-Aware Chunking',
      subtitle: 'Preserving academic headings, paragraph hierarchies, and page numbers.',
      concept: 'PyMuPDF + DOCX Header-Tree Parsing',
      description:
`Standard naive chunking cuts text every 500 characters or 200 words. This destroys academic assignments because:
- Headings like "2. Methodology" get separated from their following sentences.
- Multi-page paragraphs get sliced in half mid-argument.

How our backend handles it:
1. PyMuPDF (pdf_parser.py) / python-docx (docx_parser.py):
   Reads font sizes, font weights (bold), and outline trees to reconstruct the actual document heading hierarchy (e.g., H1: 3. System Architecture > H2: 3.1 Data Ingestion).
2. Section-Aware Chunker (assignment_chunker.py):
   Groups text within its logical section boundary. If a paragraph is too long (> 300 words), it splits at sentence punctuation while retaining the full parent heading path as metadata (section: "3. System Architecture / 3.1 Data Ingestion", page: 4).`,
      mathOrLogic: `Chunk = {\n  id: "draft_chunk_004",\n  section: "3.2 Cloud Architecture",\n  page: 3,\n  text: "We selected AWS Lambda for serverless inference...",\n  tokens: 142\n}`,
      exampleFileReference: {
        specDoc: 'COMP8240 Spec page 2: "Section 3 must contain a complete system diagram and API spec."',
        studentDraft: "Tony's VADER Proposal page 4: Section 4.1 'Architecture Overview'",
        detail: 'The chunker tags Tony\'s Section 4.1 text with page 4. Even if the student titled it "4.1" instead of "3", the semantic embedding connects it to the specification\'s System Architecture requirement.'
      }
    },
    {
      id: 'vector-indexing',
      number: '03',
      title: 'Vector Embeddings & Semantic ChromaDB',
      subtitle: 'Converting academic prose into high-dimensional geometric vectors.',
      concept: 'Dense Retrieval via sentence-transformers (all-MiniLM-L6-v2)',
      description:
`Once chunks are created, each chunk is passed through an embedding neural network (all-MiniLM-L6-v2).
- The neural net maps the sentence meaning into a 384-dimensional dense vector space.
- Semantically identical concepts ("cloud infrastructure cost" and "AWS budget considerations") will have high Cosine Similarity even if they share zero identical keywords.
- Chunks are stored in a local SQLite-backed ChromaDB collection scoped specifically to the current review_id.
- If neural models are absent, our built-in fallback switches to a deterministic TF-IDF + Cosine Sparse Matrix with zero installation hurdles.`,
      mathOrLogic: `Cosine_Similarity(u, v) = (u · v) / (||u|| * ||v||) ∈ [-1.0, 1.0]`,
      exampleFileReference: {
        specDoc: 'Requirement: "Identify potential ethical and privacy concerns with data ingestion."',
        studentDraft: "Tony's VADER Proposal: 'User review comments will be scraped from public Reddit feeds without personally identifiable tokens.'",
        detail: 'Cosine similarity between this requirement and Tony\'s Section 5 chunk is 0.79. ChromaDB returns this chunk as Evidence #1 for the Ethical Compliance check.'
      }
    },
    {
      id: 'schema-enforcement',
      number: '04',
      title: 'Strict JSON Schema Enforcement & LLM Reasoning',
      subtitle: 'Guaranteeing deterministic, machine-readable output without conversational fluff.',
      concept: 'Pydantic V2 + Gemini / Ollama Structured Outputs',
      description:
`Chat models typically reply with conversational text: "Sure! Here is my feedback on your assignment..."
In an automated academic grading engine, this breaks downstream pipelines.

How we enforce structure:
1. We define strict Pydantic models (RequirementEvaluation, RubricEvaluation, PriorityItem).
2. We extract the JSON Schema using Pydantic.model_json_schema() and send it directly in the API call:
   - For Google Gemini 1.5 Flash: We use generationConfig.responseMimeType = "application/json".
   - For Local Ollama (Gemma 2): We pass format: "json" with schema prompt framing.
3. Every response is parsed and validated by model_validate(). If any key is missing or an invalid enum value is returned, our retry engine automatically retries with corrective guidance.`,
      mathOrLogic: `enum RequirementStatus {\n  COVERED = "COVERED",\n  PARTIAL = "PARTIAL",\n  MISSING = "MISSING",\n  UNCLEAR = "UNCLEAR"\n}`,
      exampleFileReference: {
        specDoc: 'Requirement: "Provide an architectural diagram of the sentiment scoring pipeline."',
        studentDraft: "Section 3.1 describes the diagram, but does not embed an image or ASCII workflow.",
        detail: 'The LLM returns: { "status": "PARTIAL", "confidence": 0.85, "reason": "Architecture components are listed in text, but visual dataflow diagram is absent.", "recommendation": "Embed a visual flowchart illustrating data flow from ingestion to scoring." }'
      }
    },
    {
      id: 'evidence-validation',
      number: '05',
      title: 'Evidence Grounding & Anti-Hallucination Gate',
      subtitle: 'Ensuring that every critique quote actually exists in the student document.',
      concept: 'Verbatim Substring & Levenshtein Verification',
      description:
`The biggest risk of LLM evaluators is citation hallucination — claiming the student wrote something they never actually said.

Our Post-Evaluation Grounding Gate (metrics.py):
Before any evaluation card is accepted into the final review:
1. The engine inspects every string in the evidence.quote list.
2. It executes a case-insensitive substring search against the actual text of the assigned chunk_id.
3. If the quote is slightly paraphrased by the LLM, the system computes fuzzy character overlap.
4. If a quote cannot be verified against the student\'s text, its confidence score is penalized and it is discarded from display.`,
      mathOrLogic: `Groundedness_Score = |Verified_Quotes| / |Total_Extracted_Quotes| (Target: 1.0)`,
      exampleFileReference: {
        specDoc: 'Rubric: "Demonstrates comprehensive testing strategy."',
        studentDraft: "Tony's Draft page 5: 'Unit tests were implemented using pytest with 85% branch coverage.'",
        detail: 'The engine verifies that "Unit tests were implemented using pytest with 85% branch coverage." is present verbatim in draft_chunk_007. The citation is verified with 100% groundedness.'
      }
    },
    {
      id: 'resilient-fallback',
      number: '06',
      title: 'Resilient Hybrid Provider (Gemini + Local Gemma/Mock)',
      subtitle: 'Zero downtime: seamlessly handling rate limits and offline usage.',
      concept: 'Primary / Secondary Provider Interception Pattern',
      description:
`When using cloud AI APIs on university networks or free tiers, HTTP 429 (Rate Limit Exceeded) and quota depletion are common.

How our Fallback Provider Works:
- Primary: Google Gemini 1.5 Flash (Free Tier: 15 RPM, 1,500 requests/day).
- Interception: FallbackLLMProvider wraps all generate_text and generate_structured calls in a guarded try-except block.
- Failover: If Gemini returns a 429, 503, or connection timeout, the request is immediately routed to the Local Provider (Ollama Gemma 2 if installed, or deterministic offline mock).
- The user\'s progress bar never crashes, and the review successfully completes without manual intervention.`,
      mathOrLogic: `Execute(Req): Try Gemini() -> Catch(RateLimitError) -> Log Warning -> Execute Local(Ollama / Mock)`,
      exampleFileReference: {
        specDoc: 'Review compilation running across 12 requirements and 4 rubric criteria.',
        studentDraft: 'Large 15-page document requiring 16 sequential structured API calls.',
        detail: 'If call #11 hits the 15 RPM free limit, the system switches to local on-device inference without losing any progress from calls #1 to #10.'
      }
    }
  ]

  const current = steps[activeStep]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-black border border-neutral-800 rounded-2xl max-w-4xl w-full h-[90vh] flex flex-col shadow-2xl overflow-hidden text-neutral-100">
        
        {/* Top Header */}
        <div className="px-6 py-4 border-b border-neutral-800 flex items-center justify-between bg-neutral-950/80">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-neutral-900 border border-neutral-700 flex items-center justify-center">
              <Compass className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-semibold tracking-tight text-white">
                Under the Hood: How the AI Review Engine Works
              </h2>
              <p className="text-[11px] text-neutral-400">
                Core engineering principles, algorithms, and real pipeline walkthrough
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-900 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body: Left Navigation + Right Detail */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          
          {/* Step Selector Sidebar */}
          <div className="w-full md:w-64 border-b md:border-b-0 md:border-r border-neutral-800 bg-neutral-950 p-3 space-y-1 overflow-y-auto shrink-0">
            <div className="text-[10px] uppercase font-mono tracking-wider text-neutral-500 px-3 py-1">
              Pipeline Stages
            </div>
            {steps.map((step, idx) => (
              <button
                key={step.id}
                onClick={() => setActiveStep(idx)}
                className={`w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all flex items-center justify-between ${
                  activeStep === idx
                    ? 'bg-neutral-100 text-black font-semibold'
                    : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <span className="font-mono text-[10px]">
                    {step.number}
                  </span>
                  <span className="truncate">{step.title.split('&')[0].trim()}</span>
                </div>
                <ChevronRight className="w-3.5 h-3.5 opacity-50 shrink-0" />
              </button>
            ))}
          </div>

          {/* Active Step Detailed Explanation */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-black">
            
            {/* Header */}
            <div className="space-y-1.5 pb-4 border-b border-neutral-800">
              <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
                <span>STAGE {current.number}</span>
                <span>•</span>
                <span className="text-white font-medium">{current.concept}</span>
              </div>
              <h3 className="text-xl font-bold tracking-tight text-white">{current.title}</h3>
              <p className="text-xs text-neutral-400">{current.subtitle}</p>
            </div>

            {/* Core Explanation */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-neutral-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-white" />
                <span>Technical Implementation</span>
              </h4>
              <div className="text-xs sm:text-sm text-neutral-300 leading-relaxed space-y-2 whitespace-pre-line font-sans">
                {current.description}
              </div>
            </div>

            {/* Formula / Logic Specification */}
            <div className="space-y-2 bg-neutral-950 border border-neutral-800 rounded-xl p-4">
              <div className="text-[11px] font-mono uppercase text-neutral-400 flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5 text-white" />
                <span>Data Contract & Formulation</span>
              </div>
              <pre className="font-mono text-xs text-neutral-200 overflow-x-auto whitespace-pre-wrap bg-black p-3 rounded-lg border border-neutral-900">
                {current.mathOrLogic}
              </pre>
            </div>

            {/* Real Concrete Example Using Attached Sample Files */}
            <div className="space-y-3 bg-neutral-950/60 border border-neutral-800 rounded-xl p-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-white">
                <Sparkles className="w-3.5 h-3.5 text-neutral-300" />
                <span>Concrete Walkthrough with Your Attached Sample</span>
              </div>
              <div className="space-y-2 text-xs text-neutral-300">
                <div className="flex items-start gap-2">
                  <span className="font-mono text-neutral-400 text-[11px] shrink-0">SPEC:</span>
                  <span className="text-neutral-200">{current.exampleFileReference.specDoc}</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="font-mono text-neutral-400 text-[11px] shrink-0">DRAFT:</span>
                  <span className="text-neutral-200">{current.exampleFileReference.studentDraft}</span>
                </div>
                <div className="bg-black/60 p-3 rounded-lg border border-neutral-800 text-neutral-300 leading-relaxed">
                  <span className="text-white font-medium">What Happened in this Step: </span>
                  {current.exampleFileReference.detail}
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Bottom Bar: Step Navigation */}
        <div className="px-6 py-3.5 border-t border-neutral-800 bg-neutral-950 flex items-center justify-between text-xs">
          <button
            onClick={() => setActiveStep((prev) => Math.max(0, prev - 1))}
            disabled={activeStep === 0}
            className="px-3 py-1.5 rounded-lg border border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-700 disabled:opacity-30 disabled:hover:text-neutral-400 transition-colors"
          >
            Previous Stage
          </button>

          <span className="font-mono text-[11px] text-neutral-500">
            {activeStep + 1} of {steps.length}
          </span>

          <button
            onClick={() => setActiveStep((prev) => Math.min(steps.length - 1, prev + 1))}
            disabled={activeStep === steps.length - 1}
            className="px-3 py-1.5 rounded-lg bg-white text-black font-semibold hover:bg-neutral-200 disabled:opacity-30 transition-colors"
          >
            Next Stage
          </button>
        </div>

      </div>
    </div>
  )
}
