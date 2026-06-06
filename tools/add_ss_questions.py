#!/usr/bin/env python3
"""Coverage pass: SS20, SS21, SS22, SS24 — the remaining moderately-covered
exams. Mines the not-yet-cited questions into their knowledge points.
NEW is a list of ((chapter, kp), [questions]); duplicate keys accumulate.
Idempotent on the exact question text (skips if that q already exists)."""
import glob, json, pathlib, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = pathlib.Path(__file__).resolve().parent.parent

def Q(t, freq, src, q, answer, extend, options=None):
    d = {"type": t, "freq": freq, "sources": src, "q": q, "answer": answer, "extend": extend}
    if options is not None:
        d["options"] = [{"text": x, "correct": c} for x, c in options]
    return d

NEW = [
 # ===================== SS20 (Endterm, Aug 2020) =====================
 (("ch05","cnn-architectures"), [
  Q("mc",1,["SS20 P1a"],
    "Which statements about successful ImageNet-classification architectures are correct?",
    "**True:** *AlexNet uses filters of different kernel sizes*, and *InceptionV3 uses filters of different kernel sizes* (parallel branches). **False:** ResNet18 has **fewer** parameters than VGG16 (not 11M more), and VGG16 uses FC layers too (not only conv).",
    "AlexNet/Inception mix kernel sizes; VGG is conv+FC and parameter-heavy; ResNet18 is lighter than VGG16.",
    options=[("ResNet18 has 11 million parameters more than VGG16.",False),
             ("AlexNet uses filters of different kernel sizes.",True),
             ("InceptionV3 uses filters of different kernel sizes.",True),
             ("VGG16 only uses convolutional layers.",False)]),
 ]),
 (("ch04","optimizers"), [
  Q("mc",1,["SS20 P1b"],
    "Your training loss diverges. What are reasonable things to do?",
    "**Decrease the learning rate** (divergence usually means steps too large) and **add dropout** (regularization). **Increasing** the LR would worsen divergence; merely *trying a different optimizer* is not a targeted fix here.",
    "Diverging loss ⇒ lower the LR first; regularization can help, a larger LR cannot.",
    options=[("Decrease the learning rate.",True),("Add dropout.",True),
             ("Increase the learning rate.",False),("Try a different optimizer.",False)]),
 ]),
 (("ch02","backprop"), [
  Q("mc",1,["SS20 P1c"],
    "What is the correct order of operations for gradient descent? (a) update weights, (b) compute loss, (c) repeat until convergence, (d) forward pass, (e) initialize weights.",
    "**e → d → b → a → c** ('edbac'): initialize, forward pass, compute the loss, update the weights, repeat until convergence.",
    "Initialize once, then loop forward→loss→update.",
    options=[("bcdea",False),("ebadc",False),("eadbc",False),("edbac",True)]),
 ]),
 (("ch03","why-conv"), [
  Q("mc",1,["SS20 P1d"],
    "For a CNN with a single convolutional layer, which statement is true?",
    "**True:** *it is translation-equivariant* (a shifted input gives a correspondingly shifted output). **False:** it is **not** rotation-invariant, **not** scale-invariant, and **not** fully connected (each output sees only a local patch).",
    "A conv layer is translation-equivariant, locally connected — not rotation/scale invariant.",
    options=[("It is rotation invariant.",False),("It is translation equivariant.",True),
             ("All input nodes are connected to all output nodes.",False),("It is scale-invariant.",False)]),
  Q("open",1,["SS20 P4a"],
    "What are the effects of these filter kernels? $C_1=\\frac19\\begin{bmatrix}1&1&1\\\\1&1&1\\\\1&1&1\\end{bmatrix}$, $C_2=\\begin{bmatrix}1&-1\\\\1&-1\\end{bmatrix}$.",
    "$C_1$ is a **box blur / smoothing** kernel (local average). $C_2$ is a **vertical edge detector** (it responds to horizontal change in intensity).",
    "Uniform positive kernel summing to 1 = blur; opposite-sign columns = vertical-edge detector."),
 ]),
 (("ch02","activations"), [
  Q("mc",1,["SS20 P1e"],
    "Which activation functions can lead to vanishing gradients?",
    "**Tanh** and **Sigmoid** — both **saturate** for large $|x|$, driving their derivative toward 0. **ReLU** and **Leaky ReLU** do not saturate on the positive side, so they avoid this.",
    "Saturating activations (sigmoid/tanh) cause vanishing gradients; ReLU-family do not.",
    options=[("Tanh.",True),("ReLU.",False),("Sigmoid.",True),("Leaky ReLU.",False)]),
 ]),
 (("ch02","softmax"), [
  Q("mc",1,["SS20 P1g"],
    "A sigmoid layer...",
    "**True:** it *is continuous and differentiable everywhere*. **False:** it can be used in backprop, it has **no learnable parameter**, and it maps to $(0,1)$ — not surjectively onto $(-1,1)$.",
    "Sigmoid: smooth, parameter-free, output range $(0,1)$.",
    options=[("...cannot be used during backpropagation.",False),
             ("...has a learnable parameter.",False),
             ("...maps surjectively to values in (-1, 1).",False),
             ("...is continuous and differentiable everywhere.",True)]),
 ]),
 (("ch04","over-underfitting"), [
  Q("mc",1,["SS20 P1h"],
    "Your training loss does not decrease. What could be wrong?",
    "**True:** the *learning rate is too high*, there is *too much regularization*, or there is a *bad initialization* — all can stall learning. **False:** a too-low dropout probability would not stop the training loss from decreasing.",
    "Stalled training loss ⇒ LR too high, over-regularized, or bad init.",
    options=[("Learning rate is too high.",True),("Too much regularization.",True),
             ("Dropout probability not high enough.",False),("Bad initialization.",True)]),
  Q("open",1,["SS20 P5k"],
    "Your loss curves show a phase where validation loss rises while training loss keeps falling. Name the issue and an action that doesn't change the number of parameters.",
    "**Overfitting.** Action (without changing parameter count): **weight decay / dropout / data augmentation** (or early stopping).",
    "Diverging curves = overfitting; regularize or augment rather than resize the net."),
 ]),
 (("ch04","batchnorm"), [
  Q("mc",1,["SS20 P1i"],
    "Which of the following have trainable parameters?",
    "**Batch normalization** (learnable $\\gamma,\\beta$). **Leaky ReLU**, **dropout**, and **max pooling** have **no** trainable parameters.",
    "Only BN among these has parameters; activations/dropout/pooling are parameter-free.",
    options=[("Leaky ReLU",False),("Batch normalization",True),("Dropout",False),("Max pooling",False)]),
 ]),
 (("ch04","weight-init"), [
  Q("open",2,["SS20 P2a","SS20 P2b","SS20 P2c","SS20 P2d"],
    "Weight init with inputs $i=[2,-4,1]$. (a) Forward sum for $w=[0.05,0.025,-0.03]$ (Var 0.02) and $w=[1,0.5,1.5]$ (Var 1.0). (b) What backprop problems arise from too-small / too-large variance? (c) Which init scheme fixes this and what does it achieve? (d) After switching tanh→ReLU the problem returns — why, and how to adapt the init?",
    "**(a)** Var 0.02: $s=2(0.05)+(-4)(0.025)+1(-0.03)=-0.03$. Var 1.0: $s=2(1)+(-4)(0.5)+1(1.5)=1.5$. **(b)** Too **small** variance → activations ≈0 → tiny gradients (vanishing); too **large** → tanh **saturates** → tiny gradients (vanishing). **(c)** **Xavier** init — keeps the **output variance equal to the input variance** across layers. **(d)** ReLU **zeros half** its outputs, halving the variance → multiply Xavier's variance by **2** (He/Kaiming init).",
    "Xavier preserves variance for tanh; He/Kaiming adds the ×2 for ReLU's zeroed half."),
 ]),
 (("ch03","receptive-field"), [
  Q("open",1,["SS20 P4e"],
    "For a single-layer network: (1) what layer choice has a receptive field of 1? (2) what layer has a receptive field of the whole input image?",
    "**(1)** A **$1\\times1$ convolution (or identity)** — each output depends on a single input location. **(2)** A **fully-connected layer** (or a conv/pool whose kernel equals the full input size, e.g. $224\\times224$) — every output sees the whole image.",
    "RF=1 ⇒ 1×1 conv; RF=full image ⇒ FC layer / full-size kernel."),
 ]),
 (("ch05","skip-resnet"), [
  Q("open",1,["SS20 P4g"],
    "For a residual block $H(x)=x+R(x)$ with $\\frac{\\partial R(x)}{\\partial x}=r$, compute $\\frac{\\partial H(x)}{\\partial x}$.",
    "$\\frac{\\partial H}{\\partial x}=\\frac{\\partial (x+R(x))}{\\partial x}=1+r$. The **$+1$** is the identity/skip path that lets the gradient flow through even when $r\\to0$ (a gradient highway).",
    "Residual derivative is $1+r$ — the constant 1 prevents the gradient from vanishing."),
 ]),
 (("ch06","rnn"), [
  Q("open",1,["SS20 P6c"],
    "A 1-D ReLU-RNN $h_t=\\text{ReLU}(V h_{t-1}+W x_t)$ with $V=-3,W=3,h_0=0,x_1=2,x_2=3,x_3=1$. Compute $h_2$ and $h_3$.",
    "$h_1=\\text{ReLU}(-3\\cdot0+3\\cdot2)=6$; $h_2=\\text{ReLU}(-3\\cdot6+3\\cdot3)=\\text{ReLU}(-9)=0$; $h_3=\\text{ReLU}(-3\\cdot0+3\\cdot1)=3$.",
    "The negative recurrent weight + ReLU clipping makes the state jump to 0 then recover from the input."),
  Q("open",2,["SS20 P6d"],
    "ReLU-RNN $h_t=\\text{ReLU}(V h_{t-1}+W x_t)$ with $V=-2,W=1,h_0=2,x_1=2,x_2=3,x_3=4$ and forward outputs $h_1=0,h_2=\\tfrac23,h_3=1$. Compute $\\frac{\\partial h_3}{\\partial V},\\frac{\\partial h_3}{\\partial W},\\frac{\\partial h_3}{\\partial x_1}$ (use $\\text{ReLU}'(0)=0$).",
    "$\\frac{\\partial h_3}{\\partial V}=h_2+V\\frac{\\partial h_2}{\\partial V}=\\tfrac23+V\\cdot0=\\tfrac23$. $\\frac{\\partial h_3}{\\partial W}=V x_2+x_3=-2(\\tfrac32)+4=1$. $\\frac{\\partial h_3}{\\partial x_1}=0$ — the gradient path is killed by the **dead ReLU** at $h_1=0$.",
    "BPTT chains the recurrence; a ReLU that output 0 zeroes every gradient flowing through it (dead path)."),
 ]),
 (("ch06","lstm"), [
  Q("open",1,["SS20 P6e"],
    "An LSTM is $g_1,g_2,g_3=\\sigma(\\cdot)$, $\\tilde c_t=\\tanh(\\cdot)$, $c_t=g_2\\circ c_{t-1}+g_3\\circ\\tilde c_t$, $h_t=g_1\\circ c_t$. (1) Assign $g_1,g_2,g_3$ to the forget/input/output gates. (2) What does $c_t$ represent?",
    "$g_2$ (multiplies the previous cell state) = **forget gate**; $g_3$ (multiplies the candidate) = **input/update gate**; $g_1$ (multiplies $c_t$ to form $h_t$) = **output gate**. $c_t$ = the **cell state / long-term memory**.",
    "Read the gates from the equations: forget scales $c_{t-1}$, input scales $\\tilde c_t$, output scales $c_t$ into $h_t$."),
 ]),
 (("ch05","autoencoders"), [
  Q("open",1,["SS20 P7a"],
    "Is an autoencoder an example of unsupervised or supervised learning?",
    "**Unsupervised** — it trains to reconstruct its own input (the target is the input itself), so **no labels** are required.",
    "AE = self-reconstruction, label-free ⇒ unsupervised."),
  Q("open",1,["SS20 P7d"],
    "Can you generate a new image by randomly sampling a vector from a plain autoencoder's latent space?",
    "**No.** The encoder only maps the input distribution into part of the latent space (not surjectively), so a random latent vector is **unlikely to decode to a valid image**. You'd need a **VAE** that forces the latent to follow a known (Gaussian) distribution you can sample.",
    "Plain AE latent has 'holes'; VAE regularizes it to be samplable."),
 ]),
 (("ch05","unet"), [
  Q("open",1,["SS20 P7e","SS20 P7f"],
    "You have a trained reconstruction autoencoder. (e) How would you change its architecture to perform semantic segmentation (coin vs background)? (f) What loss function would you use and how?",
    "**(e)** Replace the **last/decoder output layer** so it outputs **1 or 2 channels** (one per class) at full image resolution. **(f)** **(Binary) cross-entropy** applied **per pixel** (channel-wise) over the two classes (Dice loss also works).",
    "Segmentation head = per-pixel classifier; train with per-pixel cross-entropy."),
 ]),
 (("ch04","transfer-learning"), [
  Q("open",1,["SS20 P7h"],
    "Why do you expect a segmentation network initialized from a pretrained autoencoder to generalize better than a randomly initialized one?",
    "The autoencoder was trained on **much more (unlabeled) data**, so its **encoder already extracts useful features** (edges, shapes, coin structure). Reusing those features gives the segmentation network a strong, data-efficient starting point.",
    "Pretraining transfers features learned from abundant unlabeled data → better generalization with few labels."),
 ]),
 (("ch02","classification-loss"), [
  Q("open",1,["SS20 P8b"],
    "Binary car-vs-person CNN with one output neuron: $\\hat y=\\sigma(\\text{ReLU}(z))$, classify $\\hat y\\ge0.5$ as car. What problem arises?",
    "Since $\\text{ReLU}(z)\\ge0$, we always have $\\sigma(\\text{ReLU}(z))\\ge\\sigma(0)=0.5$, so **every input is classified as 'car'** — the classifier collapses to one class. (Drop the ReLU before the sigmoid.)",
    "Squashing the logit through ReLU first clamps the sigmoid to $[0.5,1)$ → degenerate one-class output."),
 ]),
 (("ch02","activations"), [
  Q("open",1,["SS20 P8c"],
    "Suggest a method to solve exploding gradients when training fully-connected networks.",
    "**Gradient clipping** (cap the gradient norm), and/or **better weight initialization** (e.g. Xavier) or **batch normalization** to keep activations/gradients well-scaled.",
    "Exploding gradients ⇒ clip them (primary fix); good init / BN reduce the chance."),
 ]),

 # ===================== SS21 (Endterm, Jul 2021) =====================
 (("ch01","data-leakage"), [
  Q("mc",1,["SS21 1.4"],
    "Which techniques will typically decrease your validation loss?",
    "**Add dropout** and **add additional training data** — both improve generalization. **Removing data augmentation** or swapping LeakyReLU→ReLU would not reliably reduce validation loss.",
    "Validation loss responds to regularization and more data (generalization), not to removing augmentation.",
    options=[("Add dropout.",True),("Add additional training data.",True),
             ("Remove data augmentation.",False),("Use ReLU instead of LeakyReLU.",False)]),
 ]),
 (("ch04","regularization"), [
  Q("open",1,["SS21 2.5"],
    "Why is L2-regularization called 'weight decay'? Derive an expression with weights $W$, learning rate $\\eta$, and L2 coefficient $\\lambda$.",
    "L2 adds $\\text{Reg}=\\tfrac12\\lambda\\|W\\|^2$ to the loss. The gradient update becomes $W\\leftarrow W-\\eta(\\nabla_W L+\\lambda W)=(1-\\eta\\lambda)W-\\eta\\nabla_W L$. The factor $(1-\\eta\\lambda)<1$ **shrinks ('decays') the weights toward 0** each step — hence 'weight decay'.",
    "L2's gradient adds $\\lambda W$, which multiplies $W$ by $(1-\\eta\\lambda)$ every update → decay."),
 ]),
 (("ch02","fc-layers"), [
  Q("open",1,["SS21 2.8"],
    "A FC network has hidden layers of 10 then 5 neurons (both with dropout 0.5), classifies $8\\times8$ grayscale images into 3 classes, all with bias. Total trainable parameters?",
    "Weights: $(64\\cdot10)+(10\\cdot5)+(5\\cdot3)=640+50+15=705$. Biases: $10+5+3=18$. **Total $=723$.** (Dropout adds no parameters.)",
    "Params = Σ(in·out + out) per layer; dropout is parameter-free."),
 ]),
 (("ch04","weight-init"), [
  Q("open",1,["SS21 2.9"],
    "Why is initializing all weights of a fully-connected layer to the same value problematic?",
    "It **fails to break symmetry**: every neuron receives the **same gradient** and therefore updates identically, so all neurons learn the **same function** — the layer can't develop diverse features.",
    "Identical weights ⇒ identical gradients ⇒ neurons stay clones; random init breaks symmetry."),
  Q("open",1,["SS21 2.4"],
    "How does Xavier initialization set the weights? What mean/variance do the weights and the outputs have?",
    "Weights are drawn **Gaussian with zero mean** and **variance $1/n$** where $n$ is the number of input neurons. As a result the **outputs also have zero mean and roughly the same variance as the inputs** — keeping activations well-scaled across layers.",
    "Xavier: $\\mathcal N(0,1/n_{in})$ ⇒ output variance ≈ input variance (for tanh/sigmoid)."),
 ]),
 (("ch05","vae"), [
  Q("open",1,["SS21 2.10"],
    "Explain the difference between an autoencoder and a variational autoencoder.",
    "A **VAE imposes a constraint on the latent distribution** — it forces the bottleneck to follow a known prior (e.g. Gaussian, via a KL-divergence loss) — whereas a plain **autoencoder imposes no structure** on the latent space. This makes a VAE's latent **samplable** for generation.",
    "VAE constrains the latent to a known distribution (KL) so you can sample it; AE does not."),
 ]),
 (("ch05","gan"), [
  Q("open",1,["SS21 2.11"],
    "In a GAN, what is the input to the generator (1p)? What are the two inputs to the discriminator (1p)?",
    "**Generator input:** a **random noise vector** (latent sample). **Discriminator inputs:** **generated/fake images** and **real images** — it learns to tell them apart.",
    "G: noise → image; D: sees real + fake and classifies real/fake."),
 ]),
 (("ch06","lstm"), [
  Q("open",1,["SS21 2.12"],
    "Explain how LSTMs often outperform traditional RNNs. What in their architecture enables this?",
    "Traditional RNNs struggle to learn **long-term dependencies** because of **vanishing gradients**. The LSTM's **cell state** provides a near-additive path that **improves gradient flow** across many time steps, letting the network retain information over long sequences.",
    "The cell-state highway is the LSTM's key fix for the RNN vanishing-gradient/long-memory problem."),
 ]),
 (("ch03","conv-def"), [
  Q("open",1,["SS21 3.1"],
    "A segmentation net's fc1 takes a $100\\times4\\times4$ feature map and outputs $40\\times4\\times4$. What is the shape of fc1's weight matrix (ignore bias)?",
    "Flatten input $=100\\cdot4\\cdot4=1600$; output $=40\\cdot4\\cdot4=640$. Weight matrix shape **$1600\\times640$** (in × out).",
    "FC weight shape = (flattened input) × (flattened output)."),
 ]),
 (("ch03","receptive-field"), [
  Q("open",1,["SS21 3.2"],
    "Define 'receptive field' (1p). For conv ($k{=}4,s{=}2,p{=}1$) then maxpool ($k{=}2,s{=}2$): RF after maxpool1 (1p)? RF of an fc1 neuron (1p)?",
    "**Receptive field** = the region of the input that an output feature depends on. **After maxpool1: $6\\times6$** (a $2\\times2$ pool window over a stride-2, $4\\times4$-kernel conv spans a $6\\times6$ input region). **fc1 neuron:** the **whole image** ($64\\times64$).",
    "Stack the spans: $4\\times4$ conv (s2) + $2\\times2$ pool → $6\\times6$ RF; FC sees everything."),
 ]),
 (("ch04","transfer-learning"), [
  Q("open",1,["SS21 3.3","SS21 3.4"],
    "(3.3) To classify 30 finer-grained classes instead of 5 without adding layers, what minimal change? (3.4) Given the pretrained 5-class net as a black box, how to get 30 classes?",
    "**3.3** Change the **final layer to output 30 channels** (e.g. set the last conv's output channels to 30, or add a size-preserving $1\\times1$ conv with 30 outputs). **3.4** Append a **$1\\times1$ convolution with 30 output channels** on top of the pretrained network's output.",
    "Swap/append a 1×1 conv to remap the channel count to the new number of classes."),
  Q("open",1,["SS21 3.5"],
    "You have a large unlabeled dataset of street images. How can you still use it to improve your segmentation network?",
    "**Self-supervised pretraining:** train an **autoencoder** on all the unlabeled images (reconstruction), then **reuse the encoder** to initialize the segmentation network, **freeze (some) weights**, and fine-tune the new output layer on the labeled data.",
    "Pretrain an AE on unlabeled data, transfer the encoder, fine-tune the head — classic transfer learning."),
 ]),
 (("ch03","why-conv"), [
  Q("open",1,["SS21 3.6"],
    "You want the segmentation network to accept images of arbitrary size $>64$ at run time without retraining. List two approaches.",
    "**(1)** Add a **resize/downsample layer** (e.g. bilinear) to map inputs to $64\\times64$ (and upsample the output back). **(2)** Make the network **fully convolutional** by replacing the FC layer with convolutions, so it accepts any input size.",
    "Either resize to the trained size, or go fully-convolutional (no fixed-size FC)."),
 ]),
 (("ch04","optimizers"), [
  Q("open",1,["SS21 4.1"],
    "Explain the idea behind RMSProp. How does it converge faster than plain SGD, and how does it use the gradient?",
    "RMSProp is an **adaptive learning-rate** method: it **scales the step per parameter** by an **exponentially-decaying average of the squared gradients** (the second moment). This **dampens oscillations in high-variance directions**, allowing a larger effective LR and faster, more stable convergence (e.g. through saddle points).",
    "RMSProp divides the step by √(EMA of squared grads) → per-parameter adaptive LR."),
  Q("open",1,["SS21 4.2"],
    "What is bias correction in Adam, and what problem does it fix?",
    "Adam's moment estimates $m,v$ are **initialized to 0**, so the early running averages are **biased toward zero** (too small). **Bias correction** ($\\hat m=m/(1-\\beta_1^k),\\ \\hat v=v/(1-\\beta_2^k)$) rescales them to **unbiased** estimates so the **first updates are effective**.",
    "Zero-init biases the EMAs low; dividing by $1-\\beta^k$ restores their magnitude early on."),
  Q("open",1,["SS21 4.3"],
    "Explain what vanishing gradients are in deep convolutional networks and their underlying cause.",
    "Vanishing gradients are gradients of **very small magnitude**, so early (shallow) layers get **near-zero updates** and barely learn. Causes: **saturated activations** (e.g. tanh) whose derivative ≈0, and the **chain rule** multiplying many sub-1 factors across layers, shrinking the product toward 0.",
    "Repeated multiplication of small derivatives (saturation + depth) shrinks early-layer gradients to ~0."),
 ]),
 (("ch05","skip-resnet"), [
  Q("open",1,["SS21 4.4"],
    "How do residual connections help against vanishing gradients? Show it via the gradient $\\frac{\\partial z}{\\partial w_0}$ for a residual block $z=x+R(x)$.",
    "A residual block computes $z=x+R(x)$, so $\\frac{\\partial z}{\\partial x}=1+\\frac{\\partial R}{\\partial x}$. Backpropagating to an early weight, $\\frac{\\partial z}{\\partial w_0}=(1+\\frac{\\partial R}{\\partial x})\\cdot\\frac{\\partial x}{\\partial w_0}$ — the **constant 1** guarantees a gradient path even when $\\frac{\\partial R}{\\partial x}\\to0$, so gradients don't vanish (a 'highway').",
    "The additive identity injects a $+1$ into the chain rule → undiminished gradient flow."),
 ]),
 (("ch02","softmax"), [
  Q("open",1,["SS21 5.1","SS21 5.2"],
    "(5.1) Why use a Softmax at the end of a classification network — what property makes it suitable? (5.2) Its derivative can be written in terms of softmax outputs; why is that advantageous for training?",
    "**5.1** Softmax **normalizes the logits into a probability distribution** (positive, summing to 1) over classes — ideal for classification. **5.2** Because $\\frac{\\partial \\hat y}{\\partial z}$ is expressible via the $\\hat y$ already computed in the forward pass, the **backward pass is cheap** (just reuse the cached softmax outputs).",
    "Softmax → class probabilities; its self-referential derivative makes backprop fast from the forward cache."),
  Q("open",2,["SS21 5.3","SS21 5.4"],
    "For softmax $\\hat y_i=\\frac{e^{z_i}}{\\sum_j e^{z_j}}$: (5.3) show $\\frac{\\partial \\hat y_i}{\\partial z_i}$ in terms of $\\hat y_i$. (5.4) show $\\frac{\\partial \\hat y_i}{\\partial z_j}$ ($i\\ne j$) in terms of $\\hat y_i,\\hat y_j$.",
    "**5.3** $\\frac{\\partial \\hat y_i}{\\partial z_i}=\\hat y_i(1-\\hat y_i)$. **5.4** $\\frac{\\partial \\hat y_i}{\\partial z_j}=-\\hat y_i\\hat y_j$. Compactly, $\\frac{\\partial \\hat y_i}{\\partial z_j}=\\hat y_i(\\delta_{ij}-\\hat y_j)$.",
    "The softmax Jacobian is $\\hat y_i(\\delta_{ij}-\\hat y_j)$ — diagonal $\\hat y_i(1-\\hat y_i)$, off-diagonal $-\\hat y_i\\hat y_j$."),
 ]),
 (("ch02","classification-loss"), [
  Q("open",1,["SS21 5.5"],
    "Using softmax over $C$ classes, what loss do you minimize for multi-class classification? Name it and give its formula for a single sample with one-hot label $y$.",
    "**(Categorical) Cross-Entropy**: $L(y,\\hat y)=-\\sum_{j=1}^{C}y_j\\log\\hat y_j$, which for a one-hot label reduces to $-\\log\\hat y_{\\text{true}}$ (the negative log-probability of the correct class). (Not binary CE.)",
    "Multi-class ⇒ categorical CE $=-\\log(\\hat y_{\\text{true class}})$."),
  Q("open",2,["SS21 5.6","SS21 5.7"],
    "2-layer FC net, CE loss, softmax output $\\hat y$, hidden activations $h$, second weight matrix $W^2$. (5.6) Write $\\frac{\\partial L}{\\partial w_{j,k}}$ as a product of three partials. (5.7) Compute $\\frac{\\partial L}{\\partial w^2_{3,1}}$ for true class 3.",
    "**5.6** $\\frac{\\partial L}{\\partial w_{j,k}}=\\frac{\\partial L}{\\partial \\hat y}\\cdot\\frac{\\partial \\hat y}{\\partial z}\\cdot\\frac{\\partial z}{\\partial w_{j,k}}$. **5.7** $\\frac{\\partial L}{\\partial \\hat y_3}=-\\frac{1}{\\hat y_3}$; $w_{3,1}$ affects only $z_1$ with $\\frac{\\partial \\hat y_3}{\\partial z_1}=-\\hat y_3\\hat y_1$ and $\\frac{\\partial z_1}{\\partial w_{3,1}}=h_3$. Multiplying: $\\frac{\\partial L}{\\partial w^2_{3,1}}=(-\\tfrac{1}{\\hat y_3})(-\\hat y_3\\hat y_1)(h_3)=\\hat y_1 h_3$.",
    "CE+softmax telescopes: the $-1/\\hat y_3$ and $-\\hat y_3\\hat y_1$ cancel to a clean $\\hat y_1 h_3$."),
 ]),

 # ===================== SS22 (Endterm, Aug 2022) =====================
 (("ch02","activations"), [
  Q("mc",1,["SS22 1.4"],
    "You build a CNN with TanH activations. What could reduce the likelihood of vanishing gradients?",
    "**All four help:** **Xavier initialization** (keeps variance balanced), **residual blocks** (gradient highway), **replacing TanH with Leaky ReLU** (non-saturating), and **reducing the number of layers** (fewer chained multiplications).",
    "Vanishing-gradient mitigations: good init, residuals, non-saturating activations, fewer layers.",
    options=[("Use Xavier initialization for your conv layers.",True),
             ("Organize the layers in residual blocks.",True),
             ("Replace TanH with Leaky ReLU (α=0.2).",True),
             ("Reduce the number of layers.",True)]),
 ]),
 (("ch04","optimizers"), [
  Q("mc",1,["SS22 1.5"],
    "What is the benefit of using Momentum in optimization?",
    "**True:** *it is more likely to avoid local minima* (and saddle points) when used with SGD — accumulated velocity carries through. **False:** it doesn't 'introduce a single learnable parameter', doesn't equalize the LR across dimensions (that's adaptive methods), and isn't a 'combination of multiple methods' (that's Adam).",
    "Momentum's velocity helps escape local minima/saddles; it is not adaptive per-dimension.",
    options=[("It introduces just a single learnable parameter.",False),
             ("It effectively scales the LR equally across all dimensions.",False),
             ("It combines the benefits of multiple optimization methods.",False),
             ("It is more likely to avoid local minima when used with SGD.",True)]),
  Q("open",1,["SS22 8.1","SS22 8.2"],
    "(8.1) Main definitional difference between GD and SGD? (8.2) Two advantages of SGD over GD.",
    "**8.1** **GD** updates once **per epoch** (gradient over the whole training set); **SGD** updates **every iteration/mini-batch**. **8.2** SGD's **noise acts as regularization and helps escape saddle points**, and it takes **more but cheaper steps, converging faster in wall-clock time**.",
    "GD = per-epoch exact gradient; SGD = per-batch noisy gradient (faster, escapes saddles)."),
  Q("open",1,["SS22 8.3","SS22 8.4"],
    "RMSProp: $s_{k+1}=\\beta s_k+(1-\\beta)[\\nabla L\\circ\\nabla L]$, $\\theta_{k+1}=\\theta_k-\\alpha\\nabla L/\\sqrt{s_{k+1}+\\epsilon}$. (8.3) Which SGD problem does it address? (8.4) How?",
    "**8.3** SGD's **slow / noisy, oscillating convergence**. **8.4** RMSProp **dampens oscillations in high-variance directions** by dividing each step by the running RMS of the gradient, which **allows a higher effective learning rate** and smoother progress.",
    "RMSProp scales down large-variance directions → less oscillation, larger usable LR."),
  Q("open",1,["SS22 8.5","SS22 8.6"],
    "Adam: (8.5) which optimizers' concepts does it combine? (8.6) Why apply bias correction?",
    "**8.5** **Momentum** (first moment $m$) + **RMSProp** (second moment $v$). **8.6** $m_0,v_0$ start at 0, so the early estimates are **biased toward zero**; bias correction restores the **full gradient magnitude**, enabling effective (larger) early steps toward the optimum.",
    "Adam = momentum + RMSProp; bias correction de-biases the zero-initialized moments."),
  Q("open",1,["SS22 8.7","SS22 8.8"],
    "(8.7) Write Newton's update for $w_{k+1}$ for $f:\\mathbb{R}^2\\to\\mathbb{R}$. (8.8) Name one advantage of Newton's method.",
    "**8.7** $w_{k+1}=w_k-\\dfrac{f'(x,w)}{f''(x,w)}$ (gradient divided by the second derivative / Hessian). **8.8** It **converges much faster (fewer iterations)** and **removes the need to choose a learning rate** (curvature sets the step).",
    "Newton steps by gradient/Hessian — curvature-aware, LR-free, few iterations (but Hessian is costly)."),
 ]),
 (("ch02","fc-layers"), [
  Q("mc",1,["SS22 1.2"],
    "What is true about fully-connected layers?",
    "**True:** *they can be represented as a convolutional layer* (a 1×1 or full-size conv). **False:** they are linear (affine), not non-linear; the BN $\\gamma,\\beta$ length equals $M$ (output features), not $D$; and they require a **fixed** input size.",
    "An FC layer is an affine map (≡ a conv), needs a fixed input size; BN params match the output width.",
    options=[("They are non-linear functions.",False),
             ("They can be represented as a convolutional layer.",True),
             ("For input X(N×D), W(D×M), the BN β,γ length is D.",False),
             ("Once initialized, they can accept any input size.",False)]),
  Q("open",1,["SS22 2.2","SS22 2.3"],
    "FC layer $Y=XW+b$ with $X_{N\\times D},W_{D\\times M}$ and upstream $\\text{dout}=\\frac{\\partial L}{\\partial Y}$. (2.2) Dimensions of $b$ and dout? (2.3) What is $\\frac{\\partial L}{\\partial X}$ and its dimensions?",
    "**2.2** $b$ is $1\\times M$ (broadcast over the batch); dout is $N\\times M$. **2.3** $\\frac{\\partial L}{\\partial X}=\\text{dout}\\cdot W^\\top$, of shape $N\\times D$ (matches $X$).",
    "Backprop shapes mirror the forward shapes: $\\partial L/\\partial X$ matches $X$, computed as $\\text{dout}\\,W^\\top$."),
 ]),
 (("ch04","regularization"), [
  Q("open",1,["SS22 2.4","SS22 2.5"],
    "(2.4) Write the gradient-descent update with L2 weight decay (coefficient $\\lambda$, LR $\\alpha$, weights $\\theta$). (2.5) What is the purpose of weight decay?",
    "**2.4** $\\theta_{k+1}=(1-\\alpha\\lambda)\\theta_k-\\alpha\\nabla L(\\theta_k)=\\theta_k-\\alpha(\\nabla L(\\theta_k)+\\lambda\\theta_k)$. **2.5** **Regularization** — it shrinks the weights to reduce overfitting and improve generalization.",
    "Weight decay multiplies $\\theta$ by $(1-\\alpha\\lambda)$ each step → smaller weights, less overfitting."),
  Q("open",1,["SS22 2.6"],
    "What do the error curves look like if the weight-decay coefficient $\\lambda$ is too high during training?",
    "**Underfitting:** both **training and validation loss plateau at a relatively high value** — the penalty is so strong it suppresses the model's capacity to fit the data.",
    "Too-strong regularization over-shrinks weights → underfitting (both curves high)."),
 ]),
 (("ch02","regression-models"), [
  Q("open",1,["SS22 2.7","SS22 2.8"],
    "Linear regression $W^\\*=\\arg\\min_W\\frac{1}{2n}\\sum_i(y_i-\\hat y_i)^2$. (2.7) Why is a found minimum guaranteed global? (2.8) What advantage does linear regression have over iterative deep learning on a linearly-distributed dataset?",
    "**2.7** The least-squares objective is **convex**, so any local minimum is the **global** minimum. **2.8** It has a **closed-form solution** $W=(X^\\top X)^{-1}X^\\top Y$ — exact and direct, no iterative optimization needed.",
    "Convex ⇒ unique global optimum; the normal equation solves it in closed form."),
 ]),
 (("ch03","conv-def"), [
  Q("open",1,["SS22 4.1","SS22 4.2","SS22 4.3"],
    "Digit-sum net: Conv2d(2,8)→MaxPool2d(2)→BN→ReLU → Conv2d(8,16)→MaxPool2d(2)→BN→ReLU → Flatten → Linear(k,n). Input is two stacked $28\\times28$ images. (4.1) Give $(k,s,p)$ keeping spatial size. (4.2) Input and output shapes. (4.3) Value of $k$.",
    "**4.1** e.g. $(k{=}3,s{=}1,p{=}1)$ ('same' conv). **4.2** Input $N\\times2\\times28\\times28$; output $N\\times19$ (sums $0..18$ → 19 classes). **4.3** Spatial size: $28\\to28\\to14\\to14\\to7$, depth 16, so $k=16\\cdot7\\cdot7=784$.",
    "Same-padding convs preserve size; two pools take $28\\to7$; flatten = channels·H·W."),
 ]),
 (("ch03","receptive-field"), [
  Q("open",1,["SS22 4.6","SS22 4.7","SS22 4.8"],
    "(4.6) Define the receptive field of a neuron in an intermediate layer. (4.7) RF after maxpool1 (conv $k{=}5,s{=}1$; pool $k{=}2,s{=}2$). (4.8) RF after the Linear layer.",
    "**4.6** The region of the **input image** that a single neuron is affected by. **4.7** $r_1=5\\to r_2=5+1\\cdot(2-1)=6$ → **$6\\times6$**. **4.8** The Linear layer sees the **whole input image** ($28\\times28$).",
    "RF grows from the conv kernel; an FC layer's RF is the entire input."),
 ]),
 (("ch04","transfer-learning"), [
  Q("open",1,["SS22 5.5"],
    "After pretraining an autoencoder on a large dataset to build a classifier on a small labeled set, what is this technique called, and how should you handle the weights given the small dataset?",
    "**Transfer learning.** Reuse the pretrained **encoder** as the backbone and **freeze (part of) its weights**, training only the new classification head — this avoids overfitting the small labeled set and preserves the learned features.",
    "Transfer learning: freeze the pretrained encoder, train only the new head on scarce labels."),
 ]),
 (("ch05","vae"), [
  Q("open",1,["SS22 5.6","SS22 5.7"],
    "You trained an autoencoder on MNIST. (5.6) Why does decoding a randomly sampled latent vector not produce a digit? (5.7) How can you train it so random latents decode to MNIST digits?",
    "**5.6** Training only maps the **input distribution** into the latent space; this mapping need **not be surjective**, so random latent vectors fall in 'empty' regions the decoder never learned. **5.7** Use a **Variational Autoencoder** — enforce a loss (KL) so the latent follows a known distribution (Gaussian) you can sample.",
    "Plain AE latent isn't fully covered; VAE regularizes it to a samplable prior."),
 ]),
 (("ch01","tasks"), [
  Q("open",1,["SS22 5.8","SS22 5.9"],
    "(5.8) What is semantic segmentation of an image? (5.9) For a $C\\times H\\times W$ input, what are the segmentation output dimensions?",
    "**5.8** **Per-pixel classification** — assigning a class label to **every pixel**. **5.9** $\\hat C\\times H\\times W$, where $\\hat C$ is the **number of classes** (one channel per class, same spatial size as the input).",
    "Segmentation = dense per-pixel labels; output has one channel per class at full resolution."),
 ]),
 (("ch02","backprop"), [
  Q("open",2,["SS22 6.1","SS22 6.2","SS22 6.3"],
    "Net with Leaky ReLU ($\\alpha{=}0.5$): $x_1{=}1,x_2{=}{-}2$; $w_{11}{=}{-}0.5,w_{21}{=}{-}1,b_1{=}0.5$; $w_{12}{=}1,w_{22}{=}0.5,b_2{=}0$; $w_{13}{=}2,w_{23}{=}1.5,b_3{=}{-}1$; output weights $v$, $b_4{=}1,b_5{=}{-}1$; targets $y_1{=}1,y_2{=}1$. (6.1) Compute $\\hat y_1,\\hat y_2$. (6.2) MSE. (6.3) SGD update of $w_{11}$ (lr 0.1).",
    "**6.1** $h_1{=}{-}0.5(1){-}1({-}2){+}0.5{=}2,\\ h_2{=}1{-}1{+}0{=}0,\\ h_3{=}2{-}3{-}1{=}{-}2$; LeakyReLU → $h_4{=}2,h_5{=}0,h_6{=}{-}1$. With $v_{11}{=}1,v_{21}{=}{-}0.5,v_{31}{=}{-}1,v_{12}{=}{-}0.5,v_{22}{=}2,v_{32}{=}1$: $\\hat y_1{=}1(2){+}({-}1)({-}1){-}1{=}2,\\ \\hat y_2{=}{-}0.5(2){+}1({-}1){+}2{=}0$. **6.2** $\\text{MSE}=\\tfrac12(2{-}1)^2+\\tfrac12(0{-}1)^2=1$. **6.3** $\\frac{\\partial L}{\\partial w_{11}}=((\\hat y_1{-}y_1)v_{11}+(\\hat y_2{-}y_2)v_{12})\\cdot1\\cdot x_1=((1)(1)+({-}1)({-}0.5))(1)=1.5$; $w_{11}^+=-0.5-0.1(1.5)=-0.65$.",
    "Leaky ReLU's slope is 1 for positive pre-activations here; both output branches feed back into $w_{11}$."),
 ]),
 (("ch04","batchnorm"), [
  Q("open",1,["SS22 7.3"],
    "A BatchNorm2d layer operates on input $X_{8\\times3\\times32\\times64}$ (N×C×H×W). How many parameters do the running-mean and running-variance hold?",
    "BN tracks one running mean and one running variance **per channel**, so $2\\cdot C=2\\cdot3=\\mathbf{6}$ values (independent of batch/spatial size).",
    "Conv BN statistics are per-channel: running mean + var = 2·C."),
 ]),
 (("ch06","rnn"), [
  Q("open",1,["SS22 9.2","SS22 9.3"],
    "An RNN's training loss won't drop. (9.2) Explain why this happens. (9.3) Name one solution.",
    "**9.2** The **shared recurrent weights are multiplied repeatedly** across time steps; if their eigenvalues are $<1$ the gradient **vanishes**, if $>1$ it **explodes** — so the loss stops improving. **9.3** For vanishing: switch to an **LSTM** (or constrain eigenvalues ≈1); for exploding: **gradient clipping**.",
    "Repeated multiplication by the recurrent weight → vanishing/exploding; LSTM or clipping fixes it."),
 ]),
 (("ch06","transformers-attention"), [
  Q("open",1,["SS22 9.4","SS22 9.5"],
    "(9.4) In a translation Transformer fed the full input+output sentence, why must the decoder outputs be masked? (9.5) Can a Transformer take an input of arbitrary length? Explain.",
    "**9.4** Because the **entire output sentence is provided**, the decoder must **mask out the tokens after the current position** so it can't 'see' the future word it is supposed to predict (no cheating). **9.5** **No** — the attention layer's $K,Q,V$ projections use **fixed-size matrices**, so the input length is bounded by the fixed configuration.",
    "Causal masking hides future tokens; fixed-size attention projections cap the sequence length."),
 ]),

 # ===================== SS24 (Endterm, Jul 2024) =====================
 (("ch02","activations"), [
  Q("mc",1,["SS24 1.2"],
    "Which statements about activation functions are true?",
    "**True:** *(Linear→Dropout→ReLU) ≡ (Linear→ReLU→Dropout)* — ReLU is monotone, so it commutes with a fixed dropout mask. **False:** Softmax is **not** scale-invariant ($\\text{Softmax}(cx)\\ne\\text{Softmax}(x)$); Leaky ReLU outputs can be **negative**; and a skip connection is **not** an activation function.",
    "ReLU commutes with dropout; softmax is temperature-sensitive; skip connections aren't activations.",
    options=[("(Linear→Dropout→ReLU) ≡ (Linear→ReLU→Dropout).",True),
             ("Softmax is invariant to scale: Softmax(cx)=Softmax(x).",False),
             ("The output of Leaky ReLU is always non-negative.",False),
             ("Skip connection adds non-linearity, so it is an activation function.",False)]),
  Q("mc",1,["SS24 1.8"],
    "Which functions are NOT suitable as activation functions to add non-linearity?",
    "**Unsuitable:** $f(x)=x$ (linear → no non-linearity), $f(x)=\\lfloor x\\rfloor$ (floor: gradient 0 almost everywhere), and $f(x)=\\sqrt x$ (undefined for $x<0$). **Suitable:** $f(x)=|x|$ is non-linear and defined everywhere.",
    "Reject linear, zero-gradient (step/floor), or domain-restricted functions.",
    options=[("f(x) = x",True),("The floor function f(x) = ⌊x⌋",True),
             ("f(x) = |x|",False),("f(x) = √x",True)]),
 ]),
 (("ch06","transformers-attention"), [
  Q("mc",1,["SS24 1.3"],
    "Which layers are used in a Transformer model?",
    "**Fully connected layers** (the position-wise feed-forward networks and Q/K/V projections) and **Softmax layers** (inside attention). **Recurrent** and **convolutional** layers are **not** part of a standard Transformer.",
    "Transformers = attention (softmax) + feed-forward (FC); no recurrence or convolution.",
    options=[("Recurrent layers",False),("Fully connected layers",True),
             ("Softmax layers",True),("Convolutional layers",False)]),
  Q("open",1,["SS24 6.4"],
    "Transformers for translation: (1) how to inform the model of word order? (2) how are attention weights computed (and their characteristics)? (3) how is the attention output computed, and why is it called 'attention'?",
    "**(1) Positional encoding** added to the token embeddings. **(2)** Weights = **softmax of the scaled dot products $QK^\\top$**; the closer a query is to a key, the **larger the weight** (weights are non-negative and sum to 1). **(3)** Output = **weighted sum of the Values** using those weights; it's called 'attention' because the output is dominated by the values with **large weights** (the tokens it 'attends to').",
    "PE supplies order; softmax(QKᵀ) gives the weights; output = weighted sum of V."),
 ]),
 (("ch04","regularization"), [
  Q("mc",1,["SS24 1.5"],
    "Which statements about Dropout are true?",
    "**True:** *it can be seen as an ensemble of networks* (random sub-networks each step). **False:** it **can** be applied to CNNs; at **evaluation** it keeps all nodes active (scaling is handled in training with inverted dropout); and it **reduces** (not increases) the train/val gap.",
    "Dropout = train-time ensemble regularizer; full network at eval; reduces overfitting gap.",
    options=[("It cannot be applied to CNN.",False),
             ("During evaluation, it activates all nodes and scales up the output.",False),
             ("It can be seen as an ensemble of networks.",True),
             ("It increases the gap between validation and training loss.",False)]),
 ]),
 (("ch05","gan"), [
  Q("mc",1,["SS24 1.9"],
    "What is true about GANs for image generation?",
    "**True:** the *Generator decodes a latent vector into an image*; a *lower generator loss generally means a higher discriminator loss* (adversarial); and *training needs no manual real/fake labeling* (labels come for free from which images are generated). **False:** the Discriminator is **trained jointly**, not used frozen as supervision.",
    "G decodes latent→image; G and D losses trade off; real/fake labels are automatic.",
    options=[("When training G, we use a frozen pretrained Discriminator as supervision.",False),
             ("The Generator decodes a latent vector into an image.",True),
             ("A reduced generator loss generally means an increased discriminator loss.",True),
             ("Training a GAN does not require manual real/fake labeling.",True)]),
 ]),
 (("ch03","why-conv"), [
  Q("open",1,["SS24 2.3"],
    "For MNIST classification, which is more robust to digit translation: a fully-connected net (three hidden layers of 16) or VGGNet? Why?",
    "**VGGNet.** It uses **convolutions**, which are **translation-equivariant** (and with pooling, locally invariant), and has greater capacity for complex patterns — so shifted digits still activate the same features, unlike the FC net.",
    "Conv weight-sharing → translation robustness; an FC net must relearn each shifted position."),
 ]),
 (("ch05","cnn-architectures"), [
  Q("mc",1,["SS24 1.1"],
    "Which statements about CNNs are true?",
    "**True:** *deep layers typically capture high-level features*, and *pooling layers reduce the spatial dimension of feature maps*. **False:** early layers capture **low-level** features (not high-level), and layers do **not** all have the same receptive-field size (it grows with depth).",
    "Depth ↑ ⇒ higher-level features + larger RF; pooling shrinks spatial size.",
    options=[("Early layers typically capture high-level features.",False),
             ("All layers in a CNN have the same receptive field size.",False),
             ("Deep layers typically capture high-level features.",True),
             ("Pooling layers reduce the spatial dimension of feature maps.",True)]),
  Q("open",1,["SS24 2.4"],
    "AlexNet uses an $11\\times11$ filter in its first layer. Name one disadvantage of such a large filter.",
    "It is **expensive** in both parameters and computation, and it captures **coarse/global** features rather than fine local detail — stacking smaller kernels is usually preferred.",
    "Large kernels cost many params/FLOPs and miss fine local structure."),
 ]),
 (("ch03","conv-def"), [
  Q("mc",1,["SS24 1.7"],
    "Which propositions about a convolutional layer are true?",
    "**True:** the *input channels and number of filters can differ*; the *parameter count depends on the kernel's width/height*; and the *output size depends on the stride*. **False:** the parameter count does **not** depend on padding.",
    "Conv params = $k^2 C_{in}C_{out}+C_{out}$ (kernel-dependent, padding-independent); output size depends on stride.",
    options=[("The input channels and the number of filters can be different.",True),
             ("The number of parameters depends on the width/height of the kernel.",True),
             ("The number of parameters depends on padding.",False),
             ("The output size depends on the stride.",True)]),
  Q("open",1,["SS24 2.8"],
    "For an input batch $10\\times20\\times30\\times40$ (N×C×H×W), how many parameters are in a single $3\\times3$ convolution filter with stride 2, including bias?",
    "A single filter spans all input channels: $3\\times3\\times20+1=\\mathbf{181}$ (the $+1$ is the bias; stride doesn't affect parameter count).",
    "Filter params = $k\\cdot k\\cdot C_{in}+1$; stride/padding don't change it."),
 ]),
 (("ch01","class-imbalance"), [
  Q("open",1,["SS24 2.5"],
    "Binary classification with the positive class underrepresented (8 negatives per positive). Describe a training technique to alleviate the imbalance. Would you apply it at test time? Why?",
    "**Oversample the positive class** (or undersample the negative) so classes are balanced during **training** — alternatively, **weight the per-class losses**. **Don't** apply resampling at **test** time: it would distort the evaluation metrics (e.g. accuracy) and misrepresent real performance. (Loss-weighting doesn't change the data, so it's training-only by nature.)",
    "Rebalance during training (resample / loss weights); evaluate on the true distribution."),
 ]),
 (("ch04","over-underfitting"), [
  Q("mc",1,["SS24 1.4"],
    "Which statement correctly relates loss curves to overfitting/underfitting?",
    "**True:** *underfitting is indicated by high training AND high validation loss*. **False:** overfitting is **not** 'both losses high' (it's low train / high val); a low train + high val is **overfitting**, not underfitting; and steadily decreasing train+val is **healthy**, not overfitting.",
    "Underfit = both high; overfit = low train, rising val; both falling = good.",
    options=[("Overfitting occurs when both training and validation loss are high.",False),
             ("A model is underfitting if training loss is low and validation loss is high.",False),
             ("Consistently decreasing train and val loss indicates overfitting.",False),
             ("Underfitting is indicated by high training and high validation loss.",True)]),
  Q("mc",1,["SS24 1.6"],
    "Your cat-species classifier has low training error but high validation error. Which are promising to try?",
    "**Add weight regularization** and **transfer learning from a pretrained large model** — both combat overfitting. **Decreasing the learning rate** or **adding more linear layers** would not address (and more capacity could worsen) the overfitting.",
    "Low train / high val = overfitting ⇒ regularize or transfer-learn, don't add capacity.",
    options=[("Add weight regularization.",True),
             ("Transfer learning from a pretrained large model.",True),
             ("Decrease the learning rate.",False),
             ("Add more linear layers.",False)]),
  Q("open",1,["SS24 2.6"],
    "Give one situation where it makes sense to overfit a model on purpose.",
    "To **sanity-check the model/pipeline** by overfitting a **small subset** of data — if it can't reach near-zero loss on a few samples, there's a bug. (Also: deliberately fitting a model tightly to a specific small dataset it will be tested on.)",
    "Overfitting a tiny batch is the standard smoke test that training works end-to-end."),
 ]),
 (("ch02","backprop"), [
  Q("open",2,["SS24 3.1","SS24 3.2","SS24 3.3"],
    "Binary classifier, FC $z=XW+b$ with $X=[1,2,0,1]$ (post-ReLU), $W=[1,-2,3,3]^\\top,b=0$, $\\hat y=\\sigma(z),L=\\text{BCE}(y,\\hat y),y=1$. Forward: $z=0,\\hat y=0.5,L=0.693$. (3.1) Compute $\\frac{\\partial L}{\\partial \\hat y},\\frac{\\partial L}{\\partial z},\\frac{\\partial L}{\\partial W},\\frac{\\partial L}{\\partial b}$. (3.2) What to cache? (3.3) Why is $\\frac{\\partial L}{\\partial W}$ always non-positive here?",
    "**3.1** $\\frac{\\partial L}{\\partial \\hat y}=-\\tfrac1{\\hat y}=-2$; $\\frac{\\partial L}{\\partial z}=\\frac{\\partial L}{\\partial \\hat y}\\sigma(z)(1-\\sigma(z))=-2(0.25)=-0.5$; $\\frac{\\partial L}{\\partial W}=X^\\top\\frac{\\partial L}{\\partial z}=[-0.5,-1,0,-0.5]^\\top$; $\\frac{\\partial L}{\\partial b}=-0.5$. **3.2** Cache $\\hat y$ and $X$. **3.3** $\\frac{\\partial L}{\\partial W}=\\frac{\\partial L}{\\partial \\hat y}\\cdot\\sigma'\\cdot X^\\top$: $\\sigma'>0$, $X\\ge0$ (post-ReLU), and BCE's $\\frac{\\partial L}{\\partial \\hat y}\\le0$ for $y=1$ ⇒ the product is **always ≤0**.",
    "Sign analysis: positive sigmoid derivative × non-negative ReLU input × non-positive BCE gradient ⇒ non-positive."),
  Q("open",2,["SS24 3.4","SS24 3.5"],
    "A ResBlock has layers A,B,C (from {Conv1(k1,s1,p0), ReLU, Conv2(k3,s1)}) and a skip to the adder. (3.4) Assign A,B,C; which intermediate (F2/G1/G2) connects to the adder; and the padding of Conv2. (3.5) Write $\\frac{\\partial L}{\\partial F2}$ and explain the gradient 'highway'.",
    "**3.4** A=**Conv1**, B=**ReLU**, C=**Conv2**; the **block input (F2)** is what the skip adds; Conv2 padding **=1** (to keep $k{=}3$ size-preserving). **3.5** $\\frac{\\partial L}{\\partial F2}=\\frac{\\partial L}{\\partial F3}\\big(1+\\frac{\\partial\\text{Conv2}(G2)}{\\partial F2}\\big)$ — the **$+1$** from the skip path guarantees the upstream gradient passes through with full magnitude (the 'highway').",
    "Residual skip injects a $+1$ into the gradient → it never fully vanishes through the block."),
 ]),
 (("ch04","weight-init"), [
  Q("open",1,["SS24 5.5"],
    "A 10-class classifier uses ReLU activations with Xavier initialization. Why is Xavier not the best choice, and what do you recommend?",
    "**Xavier is tuned for tanh/sigmoid**, not ReLU — it doesn't account for ReLU zeroing half the activations, so the variance isn't preserved. Use **Kaiming (He) initialization** instead (variance $2/n_{in}$).",
    "ReLU halves the variance ⇒ use He/Kaiming (the ×2 variant of Xavier)."),
 ]),
 (("ch02","classification-loss"), [
  Q("open",1,["SS24 5.1","SS24 5.3"],
    "A 10-class net uses $\\hat y=\\text{Sigmoid}(z)$ with categorical cross-entropy $-\\sum_i y_i\\log\\hat y_i$ and a regularizer $\\sum_w e^{-w}$. (5.1) What weights does $\\sum_w e^{-w}$ encourage, and what problems result? (5.3) It reaches ~0 loss but ~10% accuracy — why?",
    "**5.1** $e^{-w}$ is minimized by **large positive weights** → **exploding gradients, numerical instability, poor performance**. **5.3** With a **sigmoid** (not softmax) output, the network can drive **every $\\hat y_i\\to1$**: categorical CE only rewards the true class's probability and **doesn't penalize false positives**, so loss →0 while accuracy stays at chance (~10%).",
    "Sigmoid+CE without competition lets all outputs saturate to 1 → low loss, random accuracy. Use softmax."),
  Q("open",1,["SS24 5.2"],
    "Your friend changes the regularizer to $\\sum_w \\cosh(w)-1$, insisting the '$-1$' is needed so zero weights aren't punished. Does the '$-1$' change the trained weights? Explain.",
    "**No.** The $-1$ is a **constant**; its gradient is 0, so it doesn't affect the update or the resulting weights. (It only shifts the loss value, making $\\cosh(0)-1=0$ cosmetically.)",
    "Adding a constant to a loss leaves the gradient — and thus the optimum — unchanged."),
 ]),
 (("ch03","special-conv"), [
  Q("open",1,["SS24 5.6"],
    "Can a convolutional layer (fixed input/output sizes) be exactly replaced by Flatten → Linear → Reshape? Explain.",
    "**Yes.** With fixed sizes, a convolution is a **linear map** with a specific (sparse, weight-shared) structure. A Linear layer can replicate it exactly by setting its weight matrix to match the conv's connectivity and shared weights (zeros where the conv doesn't connect), then reshaping back.",
    "A fixed-size conv is a structured linear operator → expressible as a (sparse, weight-tied) FC layer."),
 ]),
 (("ch01","data-leakage"), [
  Q("open",1,["SS24 4.4"],
    "You train from scratch on 1000 images, then evaluate on train and validation. What result do you expect, and name two ways (besides transfer learning) to improve it.",
    "Expect **high training accuracy but low validation accuracy** (overfitting on the small dataset). Improvements: **label/collect more data**, **data augmentation**, or other **regularization** (dropout, weight decay).",
    "Small-data training overfits; combat it with more data, augmentation, or regularization."),
 ]),
 (("ch05","autoencoders"), [
  Q("open",1,["SS24 4.5"],
    "For transfer learning you want to train your own backbone instead of downloading one. How can you do it with 1M unlabeled images?",
    "Train an **autoencoder** (or another **self-supervised** method) on the **1M unlabeled images** to learn good features, then reuse its **encoder** as the pretrained backbone for your classifier.",
    "Self-supervised pretraining (autoencoder) turns unlabeled data into a reusable feature backbone."),
 ]),
 (("ch06","rnn"), [
  Q("open",1,["SS24 6.2"],
    "For an RNN-based translation model: (1) what are the input and output of the RNN block? (2) For full-sentence translation, why is a sequence-to-sequence (encode-all-then-decode) pipeline best?",
    "**(1)** Input: the current **word embedding** plus the **previous hidden state**; output: the **current hidden state** (and a per-step prediction). **(2)** Translation needs the **whole input sentence before producing output** (word order/meaning can depend on later words), so an encode-then-decode (seq2seq) structure fits — process all inputs, then generate the output sequence.",
    "RNN block: (embedding, prev state) → new state; translation needs full-input encoding before decoding."),
 ]),
 (("ch06","lstm"), [
  Q("open",1,["SS24 6.3"],
    "(1) What activations are used for an LSTM's forget gate, input gate, candidate memory, and output gate? (2) Is ReLU a good choice for the forget gate? (3) Why is LSTM better on long sequences?",
    "**(1)** **Sigmoid** for the three gates (forget/input/output); **tanh** for the candidate memory. **(2)** **No** — ReLU's output can exceed 1, so it can't act as a $[0,1]$ gate and could make the cell state grow unbounded. **(3)** The **cell state provides a highway** for long-term dependencies (near-additive gradient flow).",
    "Gates = sigmoid (valves in [0,1]); candidate = tanh; cell-state highway handles long-range memory."),
 ]),
 (("ch05","unet"), [
  Q("open",1,["SS24 7.2"],
    "You have a pretrained CNN autoencoder and build a U-Net for segmentation by reusing its encoder. What modifications do you make to the decoder?",
    "**Add skip connections** from encoder layers to the matching decoder layers (the defining U-Net feature), and **change the final output channels** to the number of segmentation classes.",
    "U-Net = autoencoder decoder + encoder→decoder skips + class-count output head."),
 ]),
]

def main():
    added = 0
    merged = {}
    for key, qs in NEW:
        merged.setdefault(key, [])
        merged[key].extend(qs)
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        p = pathlib.Path(f)
        if p.name == "chapters.json":
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        cid = data["id"]
        changed = False
        for kp in data["knowledge_points"]:
            key = (cid, kp["id"])
            for q in merged.get(key, []):
                if any(existing["q"] == q["q"] for existing in kp["questions"]):
                    continue
                kp["questions"].append(q)
                added += 1
                changed = True
        if changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"updated {p.name}")
    valid = set()
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        if pathlib.Path(f).name == "chapters.json": continue
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for kp in d["knowledge_points"]:
            valid.add((d["id"], kp["id"]))
    for key, qs in merged.items():
        if key not in valid:
            print(f"  ! target not found (skipped {len(qs)}): {key}")
    print(f"added {added} coverage questions")

if __name__ == "__main__":
    main()
