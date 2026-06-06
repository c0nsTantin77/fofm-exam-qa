#!/usr/bin/env python3
"""One-off: append a hand-authored AI practice question to every knowledge
point that lacks one, so requirement 5 ('a few AI questions per knowledge
point') holds for all 43 KPs. Idempotent: skips KPs that already have an 'ai'."""
import glob, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

def ai(q, answer, extend):
    return {"type": "ai", "freq": 0, "sources": ["AI-generated"],
            "q": q, "answer": answer, "extend": extend}

# keyed by (chapter id, knowledge-point id)
AI = {
 ("ch01","preprocessing"): ai(
  "You normalize images using the mean/std computed over the whole dataset (train+val+test together). Why is this subtly wrong, and what is the fix?",
  "Computing the statistics over val+test **leaks** their information into the pipeline, giving an optimistically biased evaluation. Fix: estimate $\\mu,\\sigma$ on the **training set only**, then apply those fixed constants to val and test.",
  "Normalization statistics are 'parameters' fit on train only — cross-links to the data-leakage point in Ch I."),
 ("ch02","regression-models"): ai(
  "A friend claims 'logistic regression can only draw a straight boundary, so it's useless for the XOR problem.' Is the premise right, and how do you fix the model?",
  "The premise is **correct** — logistic regression is linear and cannot separate XOR with a single straight boundary. Fix: add **non-linear features** or **hidden layers + activations** (an MLP) so the model can learn a non-linear decision boundary.",
  "Linear model ⇒ linear boundary. Depth + non-linear activations are what break that limit."),
 ("ch03","receptive-field"): ai(
  "You stack five $3\\times3$ stride-1 convolutions. What is the receptive field, and why is this preferred over a single large kernel of the same size?",
  "Receptive field $=1+5\\cdot2=\\mathbf{11}\\times11$. Stacking small kernels is preferred because it uses **fewer parameters** and inserts **more non-linearities** (more ReLUs) than one $11\\times11$ kernel with the same receptive field.",
  "VGG's core insight: many small $3\\times3$ convs beat one big kernel — cheaper and more expressive."),
 ("ch03","pooling"): ai(
  "Compare how gradients flow back through MaxPool vs AvgPool for a $2\\times2$ window.",
  "**MaxPool** routes the entire upstream gradient to the single **argmax** position (the other 3 entries get 0). **AvgPool** spreads the gradient **equally**, giving each of the 4 entries $\\frac{1}{4}$ of the upstream gradient.",
  "Max = sparse/selective gradient (needs cached positions); Avg = evenly distributed gradient."),
 ("ch03","handcrafted"): ai(
  "Why might initializing a conv layer with a Sobel edge-detector kernel still be useful, even though we don't keep handcrafted kernels fixed?",
  "It gives the layer a useful **prior** (edge detection) to start from; training then **adapts** it to the task. You get faster/better convergence while keeping **learnability** — unlike a frozen handcrafted kernel.",
  "Handcrafted kernels survive only as initialization or in augmentation, never as frozen layers."),
 ("ch04","over-underfitting"): ai(
  "Train loss = 0.05, validation loss = 0.9 and rising. Name the regime and two fixes that do NOT change the dataset.",
  "**Overfitting.** Data-free fixes: add **regularization** (dropout / weight decay), use **early stopping**, or **reduce model capacity**.",
  "Low-train / high-val = overfit. The no-new-data levers are regularization, early stopping, smaller model."),
 ("ch04","batchnorm"): ai(
  "Why does Batch Normalization behave differently at train vs test time, and what breaks if you wrongly use batch statistics at test time?",
  "**Train** uses the current mini-batch mean/variance (and updates running averages); **test** uses the **cached running statistics**. Using batch stats at test time makes a single sample's output **depend on the rest of its batch** → non-deterministic, inconsistent predictions.",
  "Cache running $\\mu,\\sigma$ during training; at inference there is no batch to estimate from."),
 ("ch04","weight-init"): ai(
  "You initialize all weights of a ReLU MLP to 0. Describe what happens during training, and what He initialization fixes.",
  "With all-zero (or all-equal) weights, every neuron computes the same output and gets **identical gradients** → symmetry never breaks, so the layer learns nothing. **He init** $W\\sim\\mathcal{N}(0,\\frac{2}{n_{in}})$ samples random weights (breaking symmetry) and keeps activation variance stable for ReLU.",
  "Zero/equal init = dead symmetry; random init breaks it; He scales the variance specifically for ReLU."),
 ("ch04","hyperparams-lr"): ai(
  "You have 4 hyperparameters with 5 candidate values each. How many runs does full grid search need, and what cheaper strategy is often just as good?",
  "$5^4=\\mathbf{625}$ runs. **Random search** over the same budget is often as good or better, because not all hyperparameters matter equally — it samples more distinct values of the important ones.",
  "Grid search scales exponentially in #hyperparameters; random/Bayesian search scales far better."),
 ("ch04","transfer-learning"): ai(
  "You have only 500 labeled medical images. Why fine-tune an ImageNet-pretrained CNN instead of training from scratch, and which layers would you freeze?",
  "500 images is far too few to train a deep net from scratch (it would overfit). A pretrained backbone already has generic low-level features: **freeze the early conv layers**, **replace the head** for your classes, and **fine-tune the later layers** on your data.",
  "Small data ⇒ reuse generic early features; train only the task-specific head / late layers."),
 ("ch05","cnn-architectures"): ai(
  "Why did replacing sigmoid/tanh with ReLU (AlexNet) and stacking $3\\times3$ convs (VGG) enable deeper networks than LeNet?",
  "**ReLU** doesn't saturate for positive inputs → mitigates **vanishing gradients**, so deeper nets train. **Stacked $3\\times3$ convs** grow the receptive field with fewer parameters and more non-linearities than big kernels. Together they made depth both trainable and efficient.",
  "ReLU (gradient flow) + small-kernel stacks (efficiency) = the road to depth, later perfected by ResNet."),
 ("ch05","skip-resnet"): ai(
  "A 56-layer plain CNN has HIGHER training error than a 20-layer one (the degradation problem). How do residual blocks fix this?",
  "Residual blocks learn $F(x)$ and add the identity: $x+F(x)$. If the extra layers aren't useful they can learn $F(x)\\approx0$, so a deeper net can **always match** a shallower one. The additive identity path also keeps gradients flowing (the $+1$ term).",
  "Skip connections solve both vanishing gradients and the degradation problem of plain deep nets."),
 ("ch05","autoencoders"): ai(
  "How would you turn a plain autoencoder into an anomaly detector?",
  "Train the autoencoder **only on normal data** so it reconstructs normal inputs well. At test time, inputs with **high reconstruction error** are flagged as anomalies — the model can't reconstruct patterns it never learned.",
  "Reconstruction error as an anomaly score — a classic unsupervised use of autoencoders."),
 ("ch05","unet"): ai(
  "Why are U-Net's encoder→decoder skip connections crucial for segmentation but harmful for a compressing autoencoder?",
  "For **segmentation**, the skips carry high-resolution spatial detail (lost in downsampling) to the decoder for precise boundaries. For a **compressing autoencoder**, the skips let the model copy the input across the bottleneck (an identity shortcut), so it never learns a compressed representation.",
  "Same mechanism, opposite verdict — it depends on whether you WANT the bypassed high-res detail."),
 ("ch05","vae"): ai(
  "Why can't a plain autoencoder generate new images by sampling random latent vectors, while a VAE can?",
  "A plain AE's latent space is **unstructured / has gaps**, so a random vector decodes to garbage. A VAE's **KL term** forces the latent toward a known prior $\\mathcal{N}(0,1)$, making it **continuous and structured**; you can then sample $z\\sim\\mathcal{N}(0,1)$ and decode realistic images (the reparameterization trick makes this trainable).",
  "KL regularization + reparameterization = a smooth, sampleable latent space."),
 ("ch05","gan"): ai(
  "During GAN training the discriminator becomes near-perfect early (D≈1 on real, ≈0 on fake). Why is this a problem for the generator?",
  "A near-perfect discriminator gives the generator **vanishing gradients** (its loss saturates), so the generator **stops learning**. Remedies: balance D/G training, use a **non-saturating or Wasserstein** loss, or weaken D.",
  "GAN training needs a balanced adversary; an over-strong D starves G of gradient — a core GAN instability."),
 ("ch06","transformers-attention"): ai(
  "Why is the dot-product attention score scaled by $\\frac{1}{\\sqrt{d_k}}$ before the softmax?",
  "For large key dimension $d_k$, dot products grow large in magnitude, pushing softmax into **saturated** regions with tiny gradients. Dividing by $\\sqrt{d_k}$ keeps the scores at a reasonable scale, so softmax gradients stay healthy.",
  "The $\\sqrt{d_k}$ scale stabilizes attention; combined with LayerNorm it prevents exploding gradients."),
 ("ch06","positional-encoding"): ai(
  "'dog bites man' and 'man bites dog' contain the same tokens. Without positional encoding, would self-attention distinguish them? Why?",
  "**No.** Self-attention is **permutation-invariant** — scores depend only on token content, not order — so both yield the same set of representations. **Positional encodings** inject order so the model can tell them apart.",
  "Attention has no built-in notion of order; positional encodings supply it (RNNs get order from sequential processing)."),
 ("ch07","gradients-jacobians"): ai(
  "For a layer $y=f(x)$ with $x\\in\\mathbb{R}^n,\\ y\\in\\mathbb{R}^m$, what is the shape of $\\frac{\\partial y}{\\partial x}$? After composing with a scalar loss $L$, what is the shape of $\\frac{\\partial L}{\\partial x}$?",
  "$\\frac{\\partial y}{\\partial x}$ is the **Jacobian**, shape $m\\times n$. After the scalar loss, $\\frac{\\partial L}{\\partial x}$ is a **gradient** of shape $n$ (same as $x$): $\\frac{\\partial L}{\\partial x}=\\big(\\frac{\\partial y}{\\partial x}\\big)^\\top\\frac{\\partial L}{\\partial y}$.",
  "Vector→vector gives a Jacobian; the scalar loss contracts it into an input-shaped gradient."),
 ("ch07","chain-rule-scope"): ai(
  "In a Conv→ReLU→Conv block, the second conv receives dout. List what it must compute and what it passes to the ReLU below it.",
  "The second conv uses its incoming $\\text{dout}=\\frac{\\partial L}{\\partial Y}$ to compute its **parameter gradients** ($\\frac{\\partial L}{\\partial W},\\frac{\\partial L}{\\partial b}$) and its **input gradient** $\\frac{\\partial L}{\\partial X}$; it then passes $\\frac{\\partial L}{\\partial X}$ **down** as the dout for the ReLU below.",
  "Each layer: receive dout → compute local param grads → emit input-grad as the next layer's dout. This locality is exactly how autograd works."),
}

def main():
    added = 0
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        p = pathlib.Path(f)
        if p.name == "chapters.json":
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        cid = data["id"]
        changed = False
        for kp in data["knowledge_points"]:
            if any(q["type"] == "ai" for q in kp["questions"]):
                continue
            key = (cid, kp["id"])
            if key in AI:
                kp["questions"].append(AI[key])
                added += 1
                changed = True
            else:
                print(f"  ! no AI authored for {key}")
        if changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"updated {p.name}")
    print(f"added {added} AI questions")

if __name__ == "__main__":
    main()
