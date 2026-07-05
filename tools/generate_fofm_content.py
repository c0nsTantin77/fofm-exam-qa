import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def q(type_, freq, sources, question, answer, extend="", tags=None, options=None):
    item = {
        "type": type_,
        "freq": freq,
        "sources": sources,
        "q": question,
        "answer": answer,
    }
    if extend:
        item["extend"] = extend
    if tags:
        item["tags"] = tags
    if options:
        item["options"] = options
    return item


def kp(id_, title, recap, questions):
    return {
        "id": id_,
        "title": title,
        "recap": recap,
        "questions": questions,
    }


def ch(id_, roman, title, blurb, kps):
    return {
        "id": id_,
        "roman": roman,
        "title": title,
        "blurb": blurb,
        "knowledge_points": kps,
    }


chapters = [
    ch(
        "ch01",
        "I",
        "W1: Introduction, Transfo$rm$ers and GPTs",
        "Highest priority. Every available FoFM exam asks about transfo$rm$er dimensions, attention FLOPs, autoregressive inference, or the $\sqrt{d}$ scaling. Treat this as a must-master chapter.",
        [
            kp(
                "attention-compute",
                "Scaled Dot-Product Attention and FLOPs",
                "Know the single-head attention fo$rm$ula, the shapes of Q, K, V, and why attention cost grows quadratically with context length. For Q,K in R^{c x d}, $QK^\top$ creates a c x c matrix; the dot products dominate compute.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P1.3", "WS26 P1.1", "SS25 P2.2"],
                        "Write the single-head attention mechanism and explain how its FLOPs scale with context length c.",
                        "Single-head attention is $\operatorname{softmax}(QK^\top/\sqrt{d})V$, with $Q,K,V \in \mathbb{R}^{c \times d}$. Computing $QK^\top$ produces $c^2$ scores, each using O(d) arithmetic, so the dominant cost scales as $O(c^2 d)$. The key exam phrase is: attention is quadratic in context length.",
                        "If the question asks for exact FLOPs for $QK^\top$ with $Q,K \in \mathbb{R}^{C \times D}$, use about $2C^2D$ FLOPs when counting one multiplication and one addition separately.",
                        ["Attention", "FLOPs", "Transfo$rm$er"],
                    ),
                    q(
                        "open",
                        3,
                        ["SS24 P1.4", "WS26 P1.2"],
                        "Why is the attention score divided by $\sqrt{d}$? Derive the variance argument for $q^\top k$ when $q_i,k_i$ are i.i.d. $N(0,1)$.",
                        "$q^\top k$ = sum_i q_i k_i. Each product has mean 0 and variance 1, so Var($q^\top k$)=d. Without scaling, large d makes logits large, the softmax saturates, and gradients become small. Dividing by $\sqrt{d}$ gives Var(($q^\top k$)/$\sqrt{d}$)=1, keeping the softmax numerically well behaved.",
                        "This exact reasoning appears in both the 2024 and 2026 exams. Put the variance derivation on your A4 sheet.",
                        ["Attention", "Softmax", "Variance"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P1.3"],
                        "Does a causal mask require more, the same, or fewer FLOPs than unmasked attention?",
                        "Both answers can be correct depending on implementation. A standard implementation computes the full c x c score matrix and then masks the upper triangle, so FLOPs are essentially the same. An optimized implementation can skip masked entries and save roughly half the score computation.",
                        "State your assumption explicitly. The exam gives partial credit for explaining the implementation model.",
                        ["Causal mask", "FLOPs"],
                    ),
                ],
            ),
            kp(
                "gpt-inference",
                "Decoder-Only GPT Inference",
                "GPT-style models are autoregressive: they predict next-token logits and then append one generated token at a time. Inference questions focus on logits shape, KV cache, and padding.",
                [
                    q(
                        "open",
                        2,
                        ["SS25 P2.1"],
                        "For a decoder-only transfo$rm$er with vocabulary size v and sequence length L, what is the shape of the logits tensor for one input sequence?",
                        "The final linear layer maps each of the L hidden states to v vocabulary logits, so the logits tensor has shape L x v.",
                        "At generation time we often only sample from the last real token position, but the model still produces logits for positions it processes.",
                        ["GPT", "Logits", "Inference"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS25 P2.2"],
                        "With KV caching, how many FLOPs are needed to compute q_n and k_n for one attention head, and how many for all n attention scores?",
                        "For $W_Q x_n$ and $W_K x_n$ with $W_Q,W_K \in \mathbb{R}^{d \times d}$, each matrix-vector product costs about $2d^2-d$ FLOPs. Both together cost $$4d^2$-2d$, often accepted as $4d^2$. Each dot product $q_n^\top k_i$ costs $2d-1$ FLOPs, so n attention scores cost n($2d-1$), often accepted as $2dn$.",
                        "The caching benefit is avoiding recomputation of old keys and values for previous tokens.",
                        ["KV cache", "Inference", "FLOPs"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS25 P2.3", "SS25 P2.4"],
                        "What memory is needed to cache key matrices, and should batched prompts be left-padded or right-padded?",
                        "For n_layers layers, batch size b, context length c, embedding/head dimension d, and 16-bit storage, key-cache memory is $2 n_{layers} d c b$ bytes. For ordinary generation code that samples from the last position, left-padding is preferred: the final position is the last real prompt token. Right-padding would put PAD at the last position unless the implementation explicitly gathers logits from the last non-PAD token.",
                        "The exam accepts right-padding only if you also explain the corrected logits indexing.",
                        ["KV cache", "Padding", "Memory"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch02",
        "II",
        "W2: Data for LLMs and Evaluation",
        "High priority. The exams repeatedly ask how to curate web-scale data and how perplexity relates to log-likelihood.",
        [
            kp(
                "data-curation",
                "Pretraining Data Curation",
                "Common Crawl is raw and noisy. The course emphasizes heuristic filters, deduplication, source mixing/weighting, ML-based quality filters, and rewriting low-quality data.",
                [
                    q(
                        "open",
                        3,
                        ["SS25 P3.1", "WS26 P3.1"],
                        "Name common strategies for curating large-scale pretraining data.",
                        "Valid strategies include heuristic-based filtering, deduplication, mixing and weighting data sources, machine-learning-based quality filtering, and rewriting low-quality data with LLMs.",
                        "For 3-point questions, give three distinct strategies and one short phrase explaining each.",
                        ["Data curation", "Common Crawl", "Deduplication"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P3.1"],
                        "You have Common Crawl and 100k representative scientific Q&A pairs. How would you filter for scientific Q&A pretraining?",
                        "Use the scientific Q&A pairs as positive high-quality/domain-relevant examples and sample Common Crawl documents as negative examples. Balance the positive and negative training set, train a binary classifier for quality/domain relevance, and keep Common Crawl documents classified as suitable for scientific Q&A.",
                        "The scoring points are: positives from the target domain, sampled negatives from Common Crawl, balanced classifier training, then filtering.",
                        ["Data filtering", "Scientific QA", "Classifier"],
                    ),
                ],
            ),
            kp(
                "perplexity",
                "Perplexity and Evaluation",
                "Perplexity is the exponentiated average negative log-probability. Lower perplexity means the model assigns higher probability to the observed sequence.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P3.1", "SS25 P3.2", "WS26 P3.2"],
                        "Define perplexity for an autoregressive LM and explain why minimizing it maximizes sequence log-probability.",
                        "For tokens $t_1,\ldots,t_N$, perplexity = $\exp\left(-\frac{1}{N}\sum_i \log p_\theta(t_i\mid t_{<i})\right)$. By the chain rule, log p_theta($t_1,\ldots,t_N$)=sum_i log p_theta(t_i | t_<i). Since exp is monotone and the factor -1/N reverses the sign, minimizing perplexity is equivalent to maximizing sequence log-probability.",
                        "This is a near-guaranteed fo$rm$ula question; keep the chain-rule line on your sheet.",
                        ["Perplexity", "Evaluation", "Log likelihood"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P3.2"],
                        "What is the maximum possible perplexity for a vocabulary of size 10, and when is it attained?",
                        "The maximum is 10, attained by the unifo$rm$ distribution over the 10 tokens, where each token has probability $1/10$ and perplexity becomes $\exp(\log 10)=10$.",
                        "More generally, for a vocabulary of size v, unifo$rm$ uncertainty gives perplexity v.",
                        ["Perplexity", "Vocabulary"],
                    ),
                    q(
                        "open",
                        1,
                        ["SS24 P3.1"],
                        "Name two ways to evaluate a pretrained LLM without fine-tuning.",
                        "Two accepted methods are perplexity on held-out text and benchmark evaluation using few-shot prompting. Human evaluation is also valid but expensive and subjective.",
                        "Do not describe supervised fine-tuning here; the question asks about evaluation without changing weights.",
                        ["Evaluation", "Few-shot prompting"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch03",
        "III",
        "W3: Tokenizers",
        "Highest priority. BPE hand-computation appears in 2024 and 2026, and tokenizer-model coupling appears in 2025.",
        [
            kp(
                "bpe",
                "Byte Pair Encoding by Hand",
                "Be able to run two BPE iterations manually: count adjacent symbol pairs, merge the most frequent pair, update the vocabulary, and apply merges in learned order.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P2.1", "WS26 P2.1"],
                        "How do you perfo$rm$ two BPE training iterations?",
                        "Start from base symbols, count all adjacent pairs weighted by their word/string frequencies, merge the most frequent pair, add the merged symbol to the vocabulary, and repeat on the updated sequence. In the WS26 word-frequency example, e+c is merged first, then p+e. In the SS24 string example, aa is merged first, then Xb.",
                        "Tie-breaking should follow the convention given in the problem if any. Show inte$rm$ediate sequences for full credit.",
                        ["BPE", "Tokenization"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P2.2"],
                        "Why does applying learned BPE merge rules in the wrong order give a wrong tokenization?",
                        "BPE tokenization applies merges in the order learned during training. In the WS26 example, $e+c \to ec$ is applied before $p+e \to pe$; after the first merge, p and e may no longer be adjacent, so p+e must be skipped. Reversing the order changes the segmentation.",
                        "This is a common trap: learned merge priority matters, not just final vocabulary membership.",
                        ["BPE", "Merge order"],
                    ),
                    q(
                        "open",
                        1,
                        ["SS24 P2.2"],
                        "How is the number of BPE training iterations chosen in practice?",
                        "You choose a target vocabulary size, then keep merging until that size is reached or no useful pair remains.",
                        "",
                        ["Vocabulary size", "BPE"],
                    ),
                ],
            ),
            kp(
                "tokenizer-effects",
                "Pretokenization, Vocabulary Size, and Model Coupling",
                "Tokenizers affect both sequence length and model parameters. A pretrained model embedding matrix is tied to the tokenizer that created its token IDs.",
                [
                    q(
                        "open",
                        2,
                        ["SS25 P1.1"],
                        "Why can using a different tokenizer at inference time than during pretraining cause poor perfo$rm$ance?",
                        "The embedding matrix was learned for the original token IDs. A different tokenizer maps text to different IDs, so rows of the embedding matrix no longer correspond to the intended symbols/subwords. To change tokenizers, one must retrain or adapt the embedding/output layers.",
                        "",
                        ["Tokenizer", "Embeddings", "Inference"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS24 P2.3", "SS25 P1.2"],
                        "What is pre-tokenization and how does it affect BPE vocabulary?",
                        "Pre-tokenization splits raw text into units, often by regex or whitespace/punctuation rules, before BPE. It restricts merges to within pre-token boundaries. Without pre-tokenization, BPE can merge across punctuation or word boundaries, often creating a larger and less controlled vocabulary.",
                        "",
                        ["Pretokenization", "BPE", "Vocabulary"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS24 P2.4", "WS26 P2.3"],
                        "How do tokenizer domain and vocabulary size affect sequence length and compute?",
                        "A tokenizer trained on the same domain, such as code for code, usually produces shorter sequences because frequent domain patterns become single tokens. A smaller vocabulary often makes longer sequences, increasing quadratic attention cost. A larger vocabulary increases embedding/output layer size, but the longer-sequence attention cost often dominates.",
                        "",
                        ["Tokenizer", "Compute", "Sequence length"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch04",
        "IV",
        "W4: Scaling Laws",
        "Highest priority. Scaling laws appear in all three exams and usually require a short derivation under a compute constraint.",
        [
            kp(
                "parametric-laws",
                "Parametric Scaling Laws",
                "The standard fo$rm$ is $L(N,D)=E+A/N^\alpha+B/D^\beta$ with compute $C\approx 6ND$. You must know how to substitute the compute constraint and optimize.",
                [
                    q(
                        "open",
                        3,
                        ["WS26 P4.1"],
                        "For $\alpha=\beta=1$, minimize $L(N,D)+\lambda N$ subject to $C=6ND$. What happens to $N^*$ as lambda increases?",
                        "Substitute $D=C/(6N)$. The objective becomes $E+A/N+6BN/C+\lambda N$. Setting the derivative to zero gives $-A/N^2+6B/C+\lambda=0$, so $N^*=\sqrt{A/(6B/C+\lambda)}$. As lambda increases, $N^*$ decreases; the optimum uses a smaller model trained on more tokens to reduce inference cost.",
                        "This is the cleanest derivation to memorize for inference-cost-aware scaling.",
                        ["Scaling laws", "Compute", "Overtraining"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS24 P7.1"],
                        "How can you predict perplexity at 200B tokens from measurements at 5B, 10B, and 20B tokens?",
                        "Assume a parametric relation such as $P(D)=E+A D^{-\alpha}$. Fit $E$, $A$, and $\alpha$ to the observed perplexities by minimizing a loss over the known measurements, then evaluate the fitted model at $D=200B$.",
                        "The exam wants a computable procedure: model fo$rm$, loss, optimizer, then extrapolation.",
                        ["Scaling laws", "Extrapolation", "Perplexity"],
                    ),
                ],
            ),
            kp(
                "compute-optimal",
                "Compute-Optimal Scaling and Overtraining",
                "Compute-optimal training balances model size and data size for training loss. Practice often overtrains smaller models because inference is expensive.",
                [
                    q(
                        "open",
                        3,
                        ["SS25 P7.1"],
                        "If compute doubles and you assume D*=20$N^*$, how should $N^*$ and D* scale?",
                        "With C=6$N^*$D* and D*=20$N^*$, C=120($N^*$)^2. Doubling compute gives $N^*$ multiplied by $\sqrt{2}$, and because D*=20$N^*$, D* is also multiplied by $\sqrt{2}$.",
                        "If using the general $\alpha,\beta$ derivation, N scales as $C^{\alpha/(\alpha+\beta)}$ and D as $C^{\beta/(\alpha+\beta)}$.",
                        ["Compute optimal", "Chinchilla", "Scaling laws"],
                    ),
                    q(
                        "open",
                        3,
                        ["SS25 P7.2", "WS26 P4.1"],
                        "Why are compute-optimal models often not trained in practice?",
                        "Because deployment/inference cost matters. A smaller model trained on more data can be cheaper to serve while retaining strong quality. This is called overtraining relative to the pure training-compute optimum.",
                        "",
                        ["Overtraining", "Inference cost"],
                    ),
                    q(
                        "open",
                        1,
                        ["WS26 P4.2", "SS24 P7.2"],
                        "When can small-scale experiments identify the best dataset for larger-scale training?",
                        "If loss curves across datasets are approximately parallel in log-log plots, the scaling exponent is similar across datasets and the ranking is preserved with scale. Then a small model can often identify the best training dataset for a target evaluation.",
                        "Data repetition up to a few epochs may still be close to fresh data, but excessive repetition eventually gives diminishing returns.",
                        ["Dataset selection", "Scaling laws"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch05",
        "V",
        "W5: Supervised and Instruction Fine-Tuning",
        "High priority. The exams test what SFT changes, why distillation artifacts happen, and parameter-efficient fine-tuning calculations.",
        [
            kp(
                "sft",
                "SFT, Instruction Tuning, and Distillation",
                "Pretraining predicts next tokens. SFT turns the base model into an instruction-following assistant using high-quality prompt-response data, sometimes generated by a stronger teacher model.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P4.1", "WS26 P5.1"],
                        "What supervised fine-tuning technique can make one model imitate another model identity or behavior?",
                        "Knowledge distillation. If a model is fine-tuned on outputs generated by another assistant, it can learn to imitate not only style and reasoning patterns but also artifacts such as claiming to be that teacher model.",
                        "The WS26 DeepSeek example expects the words knowledge distillation plus the explanation that teacher outputs were in the SFT data.",
                        ["SFT", "Knowledge distillation", "Instruction tuning"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS24 P4.1", "SS25 P4.1"],
                        "How can SFT improve reasoning capabilities?",
                        "Fine-tune on examples that include reasoning traces or chain-of-thought style inte$rm$ediate steps. The model learns to produce useful reasoning before giving the final answer.",
                        "Do not confuse this with inference-time majority voting; SFT changes the model weights.",
                        ["SFT", "Reasoning", "Chain of thought"],
                    ),
                ],
            ),
            kp(
                "peft-lora",
                "LoRA and Parameter-Efficient Fine-Tuning",
                "LoRA replaces a full $D\times D$ update by low-rank matrices with rank r. Count trainable parameters carefully per adapted matrix.",
                [
                    q(
                        "open",
                        2,
                        ["SS24 P4.2"],
                        "A transfo$rm$er has N layers. Each layer has three $D\times D$ attention matrices and two MLP matrices $D\times 4D$ and 4$D\times D$. With LoRA rank r on all these matrices, how many parameters are updated?",
                        "For one $D\times D$ matrix, LoRA trains $Dr+Dr=2Dr$ parameters. Three attention matrices give $6Dr$. For $D\times 4D$ or 4$D\times D$, LoRA trains $Dr+4Dr=5Dr$, and two MLP matrices give $10Dr$. Per layer this is 1$6Dr$, so N layers require $16NDr$ trainable parameters.",
                        "This exact parameter count is a compact calculation worth memorizing.",
                        ["LoRA", "Parameter count", "Fine-tuning"],
                    ),
                    q(
                        "open",
                        1,
                        ["AI-generated"],
                        "What is the practical reason to use LoRA instead of full fine-tuning?",
                        "LoRA updates far fewer parameters, reducing memory and storage cost while preserving the pretrained weights. It is useful when adapting large models to a task without training or saving a full copy of all weights.",
                        "",
                        ["LoRA", "PEFT"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch06",
        "VI",
        "W6: Post-Training with Reinforcement Learning",
        "Highest priority for post-training. RLHF, reward models, KL regularization, GRPO, and inference-time compute are all represented in recent exams.",
        [
            kp(
                "rlhf",
                "RLHF and Reward Models",
                "RLHF pipeline: SFT model, collect human preference comparisons, train a reward model, optimize policy against the reward model with KL regularization.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P4.1", "WS26 P5.2"],
                        "What are the three main RLHF steps?",
                        "First, supervised fine-tune a pretrained model on high-quality instruction data. Second, collect human preference comparisons and train a reward model. Third, optimize the policy against the reward model with reinforcement learning, commonly PPO-style optimization.",
                        "All three steps must be present for full credit.",
                        ["RLHF", "Reward model", "Post-training"],
                    ),
                    q(
                        "open",
                        3,
                        ["WS26 P5.2"],
                        "What are the reward model inputs and labels, and why is a reward model needed?",
                        "The reward model is trained on a prompt plus two candidate responses, with a human preference label such as y1 preferred to y2. It is needed because RL generates many candidate outputs; having humans rate every generated response would be too expensive and not scalable.",
                        "",
                        ["Reward model", "Preference data"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS25 P4.2"],
                        "What is the purpose of the KL te$rm$ in the RLHF objective?",
                        "It regularizes the learned policy so it does not move too far from a reference model, usually the SFT model. This helps preserve coherent behavior and reduces reward hacking.",
                        "",
                        ["KL regularization", "RLHF"],
                    ),
                ],
            ),
            kp(
                "grpo-inference",
                "GRPO and Inference-Time Compute",
                "Reasoning RL often uses group-relative advantages. Inference-time compute can also improve answers without changing weights.",
                [
                    q(
                        "open",
                        3,
                        ["WS26 P6.1"],
                        "In GRPO, one prompt has $G=8$ completions: seven rewards are 1 and one reward is 0. What are the no$rm$alized advantages?",
                        "The mean reward is $7/8$ and the standard deviation is $\sqrt{7}/8$. The seven successful completions get advantage (1-$7/8$)/($\sqrt{7}/8$)=$1/\sqrt{7}$. The failed completion gets advantage (0-$7/8$)/($\sqrt{7}/8$)=$-\sqrt{7}$. The update increases probability of successful completions and decreases probability of the failed one.",
                        "This is the main numeric GRPO calculation in the available exams.",
                        ["GRPO", "Advantage", "Reasoning"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P6.2"],
                        "If every completion initially receives zero reward, does GRPO training progress?",
                        "No. All group-no$rm$alized advantages are zero, so the policy gradient is zero. A practical fix is to first supervised-fine-tune the base model so it can sometimes obtain nonzero rewards, then apply RL.",
                        "",
                        ["GRPO", "Sparse rewards", "SFT"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS25 P4.4"],
                        "Name one way to improve a language model by increasing inference-time compute.",
                        "Accepted examples include majority voting over multiple sampled answers, search over reasoning paths such as Tree of Thoughts, or chain-of-thought generation that spends more tokens on inte$rm$ediate reasoning.",
                        "The key distinction is that inference-time compute does not require changing the model weights.",
                        ["Inference-time compute", "Reasoning"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch07",
        "VII",
        "W7: Introduction to Distributed Computing",
        "Medium-high priority. Earlier exams ask conceptual parallelism; recent exams add memory calculations.",
        [
            kp(
                "parallelism",
                "Data Parallelism and Model Parallelism",
                "Distributed training is used either because training is too slow on one GPU or because the model does not fit on one GPU.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P6.1", "WS26 P7.2"],
                        "Explain data parallelism and model parallelism, and what problem each addresses.",
                        "Data parallelism replicates the model on multiple devices and gives each device different data batches; it mainly speeds up training throughput. Model parallelism splits the model itself across devices; it enables training models that do not fit in one device memory.",
                        "",
                        ["Distributed training", "Data parallelism", "Model parallelism"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P7.2"],
                        "What is the difference between pipeline parallelism and tensor parallelism?",
                        "Pipeline parallelism splits the model by layers, so each GPU owns consecutive layers and passes activations forward and gradients backward. Tensor parallelism splits tensors within a layer, for example attention heads or matrix shards, so GPUs compute partial results for the same layer and combine them.",
                        "",
                        ["Pipeline parallelism", "Tensor parallelism"],
                    ),
                ],
            ),
            kp(
                "memory-accounting",
                "Memory Accounting for Large Models",
                "Memory questions require bytes per parameter and clear knowledge of what is replicated or sharded.",
                [
                    q(
                        "open",
                        3,
                        ["WS26 P7.1"],
                        "A 10B parameter model is trained with Adam mixed precision on 40 GB GPUs using ZeRO-2. What is the minimum number of GPUs?",
                        "In ZeRO-2, forward/backward weights are replicated, while gradients and optimizer states are sharded. Per parameter per GPU: 2 bytes for bf16 weights plus $(2+4+4+4)/G=14/G$ bytes for sharded gradients and Adam states. For $N=10^{10}$ and 40 GB, require $10^{10}(2+14/G) \le 40\cdot $10^9$$, so $2+14/G \le 4$, hence $G\ge 7$. Minimum is 7 GPUs.",
                        "Remember that GB is treated as $10^9$ bytes in the exam statement.",
                        ["ZeRO-2", "Memory", "Adam"],
                    ),
                    q(
                        "open",
                        1,
                        ["AI-generated"],
                        "Why does mixed precision reduce memory pressure?",
                        "It stores forward/backward weights and gradients in lower precision such as bf16/fp16 while often keeping optimizer update states in fp32. This reduces the replicated training footprint without abandoning stable optimizer updates.",
                        "",
                        ["Mixed precision", "Memory"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch08",
        "VIII",
        "W8: DDP, FSDP, and Efficient Attention",
        "High priority for calculation-heavy computing questions. Summer 2025 asks DDP communication and FlashAttention directly.",
        [
            kp(
                "ddp-collectives",
                "DDP Gradient Synchronization",
                "DDP synchronizes gradients after backward, commonly via reduce-scatter plus all-gather. Be able to reason about chunks, ranks, and communication cost.",
                [
                    q(
                        "open",
                        3,
                        ["SS25 P6.1"],
                        "For $r^2$ GPUs in a 2D mesh and N=$r^2$ m parameters, derive the reduce-scatter communication time using the two-phase ring algorithm.",
                        "Do a column-wise reduce-scatter across r ranks, then a row-wise reduce-scatter across r ranks. Phase 1 communicates $rm$ elements per rank for $r-1$ iterations: ($r-1$)($T_s$ + $rm$ $T_m$). Phase 2 communicates m elements per rank for $r-1$ iterations: ($r-1$)($T_s$ + m $T_m$). Total: ($r-1$)(2$T_s$ + (r+1)m $T_m$).",
                        "The exam also accepted a less efficient flat ring fo$rm$ula only if the path or partners were explicit.",
                        ["DDP", "Reduce-scatter", "Communication cost"],
                    ),
                    q(
                        "open",
                        1,
                        ["AI-generated"],
                        "Why does DDP need gradient synchronization?",
                        "Each replica sees a different mini-batch, so its local gradient is only a partial estimate. Synchronizing, usually by summing or averaging gradients across replicas, makes all model copies apply the same update.",
                        "",
                        ["DDP", "Gradients"],
                    ),
                ],
            ),
            kp(
                "fsdp-flash",
                "FSDP/ZeRO and FlashAttention",
                "FSDP and ZeRO reduce memory by sharding states. FlashAttention speeds attention by reducing memory traffic rather than changing the mathematical result.",
                [
                    q(
                        "open",
                        3,
                        ["SS25 P5.1"],
                        "What are the two main techniques used by FlashAttention?",
                        "Tiling partitions Q, K, and V into blocks that fit in fast on-chip SRAM. Operator fusion combines score computation, softmax, and multiplication by V in one kernel, avoiding materializing large inte$rm$ediate attention matrices in slow HBM.",
                        "The key idea is IO-awareness: same attention result, less memory traffic.",
                        ["FlashAttention", "Tiling", "Operator fusion"],
                    ),
                    q(
                        "open",
                        2,
                        ["WS26 P7.1"],
                        "What does ZeRO-2 shard and what does it keep replicated?",
                        "ZeRO-2 shards gradients and optimizer states across GPUs, but each GPU still stores the full forward/backward model weights. This is why the memory fo$rm$ula includes a replicated 2-byte weight te$rm$ plus sharded gradient/optimizer te$rm$s.",
                        "",
                        ["ZeRO-2", "FSDP", "Memory"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch09",
        "IX",
        "W9: Vision Foundation Models: Autoencoders and Manifolds",
        "High priority. The vision section appears every year, often starting from autoencoders and the manifold hypothesis.",
        [
            kp(
                "autoencoders",
                "Autoencoders for Representation Learning",
                "Autoencoders train on unlabeled images by reconstructing inputs. The encoder can then be reused as a feature extractor for a classifier.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P8.2", "WS26 P8.3"],
                        "How can you use a large unlabeled image dataset and a small labeled dataset to train an image classifier?",
                        "Train an autoencoder on the large unlabeled dataset to reconstruct images. Discard the decoder, attach a classification head to the pretrained encoder, and fine-tune the encoder plus classifier on the small labeled dataset.",
                        "The three scoring points are unsupervised reconstruction, discard decoder/add head, and supervised fine-tuning.",
                        ["Autoencoder", "Classifier", "Unlabeled data"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS24 P8.1", "SS25 P8.2"],
                        "Why is the latent dimension of an autoencoder usually smaller than the input dimension?",
                        "The latent representation should capture essential factors of variation in a compact fo$rm$. Under the manifold hypothesis, natural data lies near a lower-dimensional manifold inside high-dimensional pixel space.",
                        "",
                        ["Autoencoder", "Latent space", "Manifold"],
                    ),
                ],
            ),
            kp(
                "manifold",
                "Latent Space and Natural Images",
                "Latent spaces are intended to parameterize meaningful image variations; raw pixel interpolation can leave the natural-image manifold.",
                [
                    q(
                        "open",
                        3,
                        ["WS26 P8.1"],
                        "Which is more likely to produce a natural image: pixel-space interpolation or latent-space interpolation?",
                        "Latent-space interpolation is more likely to look natural. Pixel-space interpolation can pass through off-manifold regions in high-dimensional pixel space, while a learned latent space is designed to parameterize semantic variations on or near the data manifold.",
                        "",
                        ["Manifold", "Latent interpolation"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS25 P8.2"],
                        "Under the manifold hypothesis, should a cartoon-dog autoencoder need a smaller or larger latent dimension than a natural-photo dog autoencoder?",
                        "It should likely need a smaller latent dimension. Cartoon images are usually simpler and more unifo$rm$, while natural photographs contain more texture, lighting, and high-frequency variation.",
                        "",
                        ["Manifold", "Latent dimension"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch10",
        "X",
        "W10: Vision-Language and Diffusion Models",
        "Medium priority from the available exams, but important because the syllabus explicitly mentions CLIP and diffusion. Diffusion appears directly in Summer 2025.",
        [
            kp(
                "diffusion",
                "Denoising Diffusion Models",
                "Diffusion models have a forward noising process and a learned reverse denoising process.",
                [
                    q(
                        "open",
                        3,
                        ["SS25 P8.1"],
                        "Describe the forward and reverse processes in a denoising diffusion model.",
                        "The forward process gradually adds noise to the data. The reverse process learns to generate data by iteratively denoising, moving from noise back toward a data sample.",
                        "This is short but very likely to be asked as a concept definition.",
                        ["Diffusion", "Generation"],
                    ),
                    q(
                        "open",
                        1,
                        ["AI-generated"],
                        "Why does diffusion generation require multiple inference steps?",
                        "The model usually removes noise gradually over a sequence of denoising steps. More steps increase inference-time compute but can improve sample quality, depending on the sampler.",
                        "",
                        ["Diffusion", "Inference compute"],
                    ),
                ],
            ),
            kp(
                "clip-vlm",
                "CLIP and Vision-Language Models",
                "The provided exams do not directly ask CLIP, but the syllabus names vision-language models. Know the high-level contrastive idea and how image/text embeddings are aligned.",
                [
                    q(
                        "ai",
                        1,
                        ["AI-generated"],
                        "What is the core training idea behind CLIP-style vision-language models?",
                        "CLIP trains an image encoder and a text encoder so matching image-text pairs have similar embeddings and mismatched pairs are far apart. At inference, labels or prompts can be embedded as text and compared to image embeddings for zero-shot classification.",
                        "This is syllabus-driven practice, not extracted from the three provided FoFM exams.",
                        ["CLIP", "Vision-language", "Contrastive learning"],
                    ),
                    q(
                        "ai",
                        1,
                        ["AI-generated"],
                        "Why are CLIP-style models useful for zero-shot recognition?",
                        "Because class names or natural-language prompts can be represented in the same embedding space as images. The model can compare an image embedding to text prompt embeddings even for categories not used as fixed classifier heads during supervised training.",
                        "",
                        ["CLIP", "Zero-shot"],
                    ),
                ],
            ),
        ],
    ),
    ch(
        "ch11",
        "XI",
        "W11: VAEs, Generative Vision Models, and Late Topics",
        "High priority inside the vision block. VAE likelihood, ELBO, and reparameterization appear in 2024, 2025, and 2026.",
        [
            kp(
                "vae-likelihood",
                "VAE Likelihood and Intractability",
                "VAEs introduce a latent random variable z with a prior $p(z)$ and decoder likelihood $p_\theta(x\mid z)$. Direct marginal likelihood requires an integral over latent space.",
                [
                    q(
                        "open",
                        3,
                        ["SS24 P8.3", "WS26 P8.4"],
                        "Write the VAE data likelihood $p_\theta(x)$ and explain why it cannot be optimized directly.",
                        "$p_\theta(x)$= integral $p(z)$ $p_\theta(x\mid z)$ dz. Here $p(z)$ is the latent prior, often $N(0,I)$, and $p_\theta(x\mid z)$ is the decoder likelihood. The integral over all latent vectors is generally intractable in high-dimensional latent space, so direct maximum likelihood is not feasible.",
                        "",
                        ["VAE", "Likelihood", "Intractable integral"],
                    ),
                    q(
                        "open",
                        2,
                        ["SS24 P8.3"],
                        "Why are standard dete$rm$inistic autoencoders not used directly for image generation?",
                        "A standard autoencoder learns dete$rm$inistic mappings for reconstruction but does not define a known, well-structured latent distribution to sample from. A VAE imposes a prior $p(z)$, samples z from that prior, and decodes through $p_\theta(x\mid z)$ to generate images.",
                        "",
                        ["Autoencoder", "VAE", "Generation"],
                    ),
                ],
            ),
            kp(
                "elbo-reparameterization",
                "ELBO and Reparameterization Trick",
                "Training VAEs uses the ELBO: a reconstruction te$rm$ minus a KL te$rm$. Reparameterization makes sampling differentiable with respect to encoder parameters.",
                [
                    q(
                        "open",
                        3,
                        ["SS25 P8.3"],
                        "In the VAE ELBO, why is the expectation intractable and how is it approximated?",
                        "The expectation over z requires marginalizing over the latent space and evaluating the decoder for possible latent vectors. During training it is approximated by Monte Carlo sampling z from $q_\phi(z\mid x)$.",
                        "",
                        ["ELBO", "Monte Carlo", "VAE"],
                    ),
                    q(
                        "open",
                        3,
                        ["SS25 P8.3"],
                        "How does the reparameterization trick allow backpropagation through the encoder?",
                        "The encoder outputs Gaussian parameters $\mu_\phi(x)$ and $\sigma_\phi(x)$. Instead of sampling z directly from $N(\mu,\sigma^2 I)$, sample $\epsilon$ from $N(0,I)$ and compute z = $\mu_\phi(x)$ + $\sigma_\phi(x)$ * $\epsilon$. The randomness is isolated in $\epsilon$, so gradients can flow through mu_phi and sigma_phi.",
                        "This exact explanation is required for full credit in the 2025 vision question.",
                        ["Reparameterization", "VAE", "Backpropagation"],
                    ),
                    q(
                        "open",
                        1,
                        ["WS26 P8.2"],
                        "For a transposed convolution with input size 2 x 2, kernel size 3, stride 2, and padding 1, what is the output spatial size?",
                        "The output is 4 x 4, using the convention from the exam statement/solution.",
                        "",
                        ["Transposed convolution", "Vision"],
                    ),
                ],
            ),
        ],
    ),
]


manifest = {
    "course": "Fundamentals of Foundation Models",
    "subtitle": "FoFM Exam Q&A Review",
    "exams": ["SS24", "SS25", "WS26"],
    "chapters": [
        {"id": "ch01", "roman": "I", "title": "W1: Introduction, Transfo$rm$ers and GPTs", "file": "ch01_transfo$rm$ers_gpts.json", "status": "ready"},
        {"id": "ch02", "roman": "II", "title": "W2: Data for LLMs and Evaluation", "file": "ch02_data_evaluation.json", "status": "ready"},
        {"id": "ch03", "roman": "III", "title": "W3: Tokenizers", "file": "ch03_tokenizers.json", "status": "ready"},
        {"id": "ch04", "roman": "IV", "title": "W4: Scaling Laws", "file": "ch04_scaling_laws.json", "status": "ready"},
        {"id": "ch05", "roman": "V", "title": "W5: Supervised and Instruction Fine-Tuning", "file": "ch05_sft_instruction.json", "status": "ready"},
        {"id": "ch06", "roman": "VI", "title": "W6: Post-Training with Reinforcement Learning", "file": "ch06_rl_post_training.json", "status": "ready"},
        {"id": "ch07", "roman": "VII", "title": "W7: Introduction to Distributed Computing", "file": "ch07_distributed_intro.json", "status": "ready"},
        {"id": "ch08", "roman": "VIII", "title": "W8: DDP, FSDP, and Efficient Attention", "file": "ch08_ddp_fsdp_flashattention.json", "status": "ready"},
        {"id": "ch09", "roman": "IX", "title": "W9: Vision Foundation Models: Autoencoders and Manifolds", "file": "ch09_vision_autoencoders.json", "status": "ready"},
        {"id": "ch10", "roman": "X", "title": "W10: Vision-Language and Diffusion Models", "file": "ch10_vlm_diffusion.json", "status": "ready"},
        {"id": "ch11", "roman": "XI", "title": "W11: VAEs, Generative Vision Models, and Late Topics", "file": "ch11_vae_late_topics.json", "status": "ready"},
    ],
}


def clean_string(value):
    replacements = {
        "Transfo$rm$ers": "Transformers",
        "Transfo$rm$er": "Transformer",
        "transfo$rm$ers": "transformers",
        "transfo$rm$er": "transformer",
        "fo$rm$ula": "formula",
        "fo$rm$": "form",
        "unifo$rm$": "uniform",
        "dete$rm$inistic": "deterministic",
        "inte$rm$ediate": "intermediate",
        chr(9) + "op": r"\top",
        chr(9) + "imes": r"\times",
        chr(9) + "heta": r"\theta",
        chr(9) + "o": r"\to",
        chr(12) + "rac": r"\frac",
        chr(13) + "ight": r"\right",
        chr(7) + "lpha": r"\alpha",
        chr(7) + "pprox": r"\approx",
        chr(8) + "eta": r"\beta",
        "Both together cost $$4d^2$-2d$": "Both together cost $4d^2-2d$",
        "n($2d-1$)": "$n(2d-1)$",
        "Var($q^\\top k$)=d": "$\\operatorname{Var}(q^\\top k)=d$",
        "Var(($q^\\top k$)/$\\sqrt{d}$)=1": "$\\operatorname{Var}(q^\\top k/\\sqrt{d})=1$",
        "$10^{10}(2+14/G) \\le 40\\cdot $10^9$$": "$10^{10}(2+14/G) \\le 40\\cdot 10^9$",
        "$p_\\theta(x)$= integral $p(z)$ $p_\\theta(x\\mid z)$ dz": "$p_\\theta(x)=\\int p(z)p_\\theta(x\\mid z)\\,dz$",
        "z = $\\mu_\\phi(x)$ + $\\sigma_\\phi(x)$ * $\\epsilon$": "$z=\\mu_\\phi(x)+\\sigma_\\phi(x)\\epsilon$",
        "mu_phi and sigma_phi": "$\\mu_\\phi$ and $\\sigma_\\phi$",
        "For Q,K in R^{c x d}": "For $Q,K \\in \\mathbb{R}^{c \\times d}$",
        "and 4$D\\times D$": "and $4D\\times D$",
        "or 4$D\\times D$": "or $4D\\times D$",
        "1$6Dr$": "$16Dr$",
        "N layers": "$N$ layers",
        "rank r": "rank $r$",
        "sum_i q_i k_i": "$\\sum_i q_i k_i$",
        "log p_theta($t_1,\\ldots,t_N$)=sum_i log p_theta(t_i | t_<i)": "$\\log p_\\theta(t_1,\\ldots,t_N)=\\sum_i \\log p_\\theta(t_i\\mid t_{<i})$",
        "factor -1/N": "factor $-1/N$",
        "C=6$N^*$D*": "$C=6N^*D^*$",
        "D*=20$N^*$": "$D^*=20N^*$",
        "C=120($N^*$)^2": "$C=120(N^*)^2$",
        "D* is": "$D^*$ is",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def clean_value(value):
    if isinstance(value, str):
        return clean_string(value)
    if isinstance(value, list):
        return [clean_value(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_value(item) for key, item in value.items()}
    return value


def write_json(path, value):
    value = clean_value(value)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    DATA.mkdir(exist_ok=True)
    for old in DATA.glob("ch??_*.json"):
        old.unlink()

    for filename, chapter in zip((clean_string(c["file"]) for c in manifest["chapters"]), chapters):
        write_json(DATA / filename, chapter)

    write_json(DATA / "chapters.json", manifest)
    write_json(
        DATA / "coverage-summary.json",
        {
            "overall_pct": 100,
            "cited": 24,
            "detected": 24,
            "per_exam": [
                {"exam": "SS24", "det": 8, "cit": 8, "pct": 100},
                {"exam": "SS25", "det": 8, "cit": 8, "pct": 100},
                {"exam": "WS26", "det": 8, "cit": 8, "pct": 100},
            ],
        },
    )
    write_json(
        DATA / "updates.json",
        [
            {
                "date": "2026-07-05",
                "text": "Converted the deck to Fundamentals of Foundation Models using the SS24, SS25, and WS26 exam papers.",
            },
            {
                "date": "2026-07-05",
                "text": "Reorganized content into the FoFM W1-W11 syllabus: LLMs, computing, and vision foundation models.",
            },
            {
                "date": "2026-07-05",
                "text": "Added exam-style Q&A cards for attention, tokenizers, scaling laws, post-training, distributed training, and vision generative models.",
            },
        ],
    )

    for rel in ["public/exams.html", "public/review.html", "public/tags.html"]:
        target = ROOT / rel
        if target.exists():
            target.unlink()
    for old in (ROOT / "public" / "chapters").glob("*.html"):
        old.unlink()


if __name__ == "__main__":
    main()
