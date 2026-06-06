#!/usr/bin/env python3
"""Add a few AI-generated MULTIPLE-CHOICE questions (type 'ai' + options).
Idempotent on question text."""
import glob, json, pathlib, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
ROOT = pathlib.Path(__file__).resolve().parent.parent

def O(*p): return [{"text": t, "correct": c} for t, c in p]
def Q(q, answer, extend, opts):
    return {"type": "ai", "freq": 0, "sources": ["AI-generated"],
            "q": q, "answer": answer, "extend": extend, "options": opts}

NEW = {
 ("ch01","tasks"): Q(
   "Which of the following are unsupervised learning tasks?",
   "**Unsupervised:** clustering customers (no labels) and PCA dimensionality reduction. Predicting house price (regression) and spam classification are **supervised** — they learn an input→label mapping.",
   "Unsupervised = no targets (clustering, dimensionality reduction). Supervised = learns input→label.",
   O(("Clustering customers by purchase behaviour (no labels).", True),
     ("Predicting house price from features.", False),
     ("Dimensionality reduction with PCA.", True),
     ("Classifying emails as spam vs. not-spam.", False))),
 ("ch02","activations"): Q(
   "Which statements about activation functions are true?",
   "**True:** ReLU units can 'die' (always-negative pre-activation → zero gradient); Tanh outputs lie in $(-1,1)$. **False:** Sigmoid is **not** zero-centred; a purely **linear** activation cannot give a deep net non-linear power (the layers collapse to one).",
   "ReLU → dying units; Tanh → zero-centred (-1,1); Sigmoid → not zero-centred; linear activation → no added power.",
   O(("ReLU can suffer from 'dying' units with zero gradient.", True),
     ("Sigmoid is a zero-centred activation.", False),
     ("Tanh outputs lie in the interval $(-1,1)$.", True),
     ("A purely linear activation still lets a deep network learn non-linear boundaries.", False))),
 ("ch03","conv-def"): Q(
   "Which statements about a convolutional layer are true?",
   "**True:** parameter count is independent of input spatial size; stride affects the output spatial size; a $1\\times1$ conv changes the channel count. **False:** padding does **not** change the number of learnable parameters.",
   "Params depend on $c_{in},k,c_{out}$ only. Stride/padding change output size, not params; $1\\times1$ mixes channels.",
   O(("The number of parameters is independent of the input's spatial size.", True),
     ("Stride affects the output spatial size.", True),
     ("Padding increases the number of learnable parameters.", False),
     ("A $1\\times1$ convolution can change the number of channels.", True))),
 ("ch04","regularization"): Q(
   "Which techniques help reduce overfitting?",
   "**True:** dropout, data augmentation, and L2 weight decay all regularize. **False:** increasing model capacity generally **increases** overfitting risk.",
   "Regularization toolbox: dropout, augmentation, weight decay, early stopping. Bigger model ⇒ more overfitting.",
   O(("Dropout.", True), ("Data augmentation.", True),
     ("Increasing the model's capacity.", False), ("L2 weight decay.", True))),
 ("ch05","skip-resnet"): Q(
   "Which statements about ResNet skip connections are true?",
   "**True:** they add an identity path that lets gradients bypass a block, enabling very deep nets to train without the degradation problem. **False:** they don't change spatial resolution, and they don't remove the need for non-linearities inside the block.",
   "Skip connection = additive identity path ⇒ gradient highway + trainable depth. Non-linearities stay inside $F(x)$.",
   O(("They create an additive identity path for gradients.", True),
     ("They let very deep networks train without the degradation problem.", True),
     ("They increase the spatial resolution of feature maps.", False),
     ("They remove the need for any non-linearity in the block.", False))),
 ("ch06","transformers-attention"): Q(
   "Which statements about self-attention / Transformers are true?",
   "**True:** self-attention is permutation-invariant (hence positional encoding), scores are scaled by $\\frac{1}{\\sqrt{d_k}}$, and any token can attend directly to any other. **False:** Transformers do **not** process tokens sequentially like RNNs — they run in parallel.",
   "Attention: order-agnostic (needs positional encoding), $\\sqrt{d_k}$ scaling, all-to-all, fully parallel.",
   O(("Self-attention is permutation-invariant unless positional encoding is added.", True),
     ("Transformers process tokens sequentially, one at a time, like RNNs.", False),
     ("The $QK^\\top$ scores are scaled by $\\frac{1}{\\sqrt{d_k}}$ for stability.", True),
     ("Attention lets any token attend directly to any other token.", True))),
 ("ch07","affine-derivatives"): Q(
   "For $Y=XW+b$ with a scalar loss $L$ and upstream $\\text{dout}=\\frac{\\partial L}{\\partial Y}$, which are true?",
   "**True:** $\\frac{\\partial L}{\\partial W}$ has the same shape as $W$; $\\frac{\\partial L}{\\partial X}=\\text{dout}\\,W^\\top$; $\\frac{\\partial L}{\\partial b}=\\sum_n \\text{dout}$. **False:** because $L$ is scalar, $\\frac{\\partial L}{\\partial Y}$ is a **gradient** (shape of $Y$), not a full Jacobian.",
   "Shape-matching: every $\\partial L/\\partial v$ matches $v$. Scalar loss ⇒ gradients, never Jacobians.",
   O(("$\\frac{\\partial L}{\\partial W}$ has the same shape as $W$.", True),
     ("$\\frac{\\partial L}{\\partial X}=\\text{dout}\\,W^\\top$.", True),
     ("$\\frac{\\partial L}{\\partial b}$ sums dout over the batch.", True),
     ("$\\frac{\\partial L}{\\partial Y}$ is a full Jacobian matrix, not a gradient.", False))),
}

def main():
    added = 0
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        p = pathlib.Path(f)
        if p.name == "chapters.json":
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        cid = data["id"]; changed = False
        for kp in data["knowledge_points"]:
            key = (cid, kp["id"])
            if key in NEW and not any(x["q"] == NEW[key]["q"] for x in kp["questions"]):
                kp["questions"].append(NEW[key]); added += 1; changed = True
        if changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"updated {p.name}")
    print(f"added {added} AI multiple-choice questions")

if __name__ == "__main__":
    main()
