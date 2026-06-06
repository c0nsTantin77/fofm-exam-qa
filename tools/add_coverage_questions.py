#!/usr/bin/env python3
"""Coverage pass: append verified questions mined from the under-covered exams
(SS25, WS23, and a few WS24/WS21/Mock) to the right knowledge points.
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

# (chapter_id, kp_id): [question, ...]
NEW = {
 ("ch01","splits"): [
  Q("mc",1,["SS25 1.7"],
    "When splitting the dataset into train/val/test sets, which statements are correct?",
    "**True:** the three sets must be **disjoint** (empty pairwise intersection), and **shuffling before the split** reduces train/test distribution mismatch. **False:** augmentation is **not** applied to validation, and the **test set must never** influence early stopping (that's the validation set's job).",
    "Test set stays untouched by every training decision; shuffle-then-split keeps the splits representative.",
    options=[("The intersection of any two of the three sets must be empty.",True),
             ("Data augmentation must also be applied to the validation set.",False),
             ("Shuffling before the split reduces train/test distribution mismatch.",True),
             ("The test set may influence early stopping.",False)]),
 ],
 ("ch01","augmentation"): [
  Q("mc",1,["SS25 1.9"],
    "Which image augmentations are suitable for training a car-brand classifier on car images?",
    "**Suitable:** horizontal flip, random crop, random blur — they keep the image within the car-image distribution and preserve the brand label. **Unsuitable:** vertical flip (cars don't appear upside-down → out of distribution).",
    "Augmentations must stay in-distribution and label-preserving. Vertical-flipping a car creates unrealistic data.",
    options=[("Horizontal flip.",True),("Vertical flip.",False),("Random crop.",True),("Random blur.",True)]),
  Q("open",1,["SS25 8.1"],
    "Would you use random rotation and random flipping to augment audio **spectrograms**? Explain.",
    "**No.** The images produced by rotating/flipping a spectrogram are **not within the distribution** of real spectrograms (axes are time vs frequency, not interchangeable), so they don't help regularize the model and can hurt.",
    "Augmentation must respect what the data *means*: flipping a spectrogram scrambles the time/frequency axes — like vertically flipping MNIST."),
 ],
 ("ch01","dataloaders"): [
  Q("open",1,["SS25 5.1"],
    "Training is slow because each iteration loads an image from HDD and fetches its label from an internet server. Name two ways to speed it up.",
    "Any two: **use a GPU/accelerator** for computation; **load the images into RAM** before training (feasible for a small dataset); **pre-download all labels** in advance to avoid per-iteration network latency.",
    "Remove per-iteration I/O bottlenecks: cache data in RAM, prefetch labels, and use parallel workers — the DataLoader's job."),
 ],
 ("ch01","class-imbalance"): [
  Q("open",1,["SS25 4.2"],
    "Your training data has 2,000 cat images but only 200 dog images, with a weighted loss $L=\\sum_i \\alpha\\,y_i(1-\\hat y_i)^2 + \\beta\\,(1-y_i)\\hat y_i^2$ (cat=1, dog=0). (a) Why is the imbalance a problem? (b) Give a reasonable $\\alpha,\\beta$ and justify.",
    "(a) The model becomes **biased toward the majority class** (cats): high accuracy on cats, poor on dogs. (b) Choose **$\\beta>\\alpha$** — weight the dog (minority) term more, so each dog mistake costs more and compensates for dogs appearing less often.",
    "Re-weighting the loss toward the minority class counters imbalance — the loss-function counterpart to over/under-sampling."),
 ],
 ("ch02","activations"): [
  Q("open",2,["SS25 3.4"],
    "What is the 'dead ReLU' problem and how do you solve it?",
    "Some ReLU units have **always-negative pre-activations**, so they output 0 for every input and their **gradient is always 0** — those weights never update ('dead'). Fix: use **Leaky ReLU** (non-zero negative slope) or **Kaiming/He initialization**.",
    "Dead ReLU = permanently-zero neuron. Leaky/Parametric ReLU keep a small negative-side gradient so units can recover."),
  Q("open",1,["SS25 3.5"],
    "Is $f(z)=-0.25z$ a suitable activation function? Explain.",
    "**No.** It is a **linear** function, so it introduces **no non-linearity** — stacking such layers collapses to a single linear map, defeating the purpose of a deep network.",
    "Any purely linear activation is useless as a non-linearity; the network would be equivalent to one affine layer."),
  Q("open",1,["WS23 2.3"],
    "Is $y=\\cos(x)$ appropriate as an activation function in a backprop network? Why or why not?",
    "**Not a good choice.** $\\cos$ is **non-monotonic and periodic**, so very different inputs map to the same output and its derivative $-\\sin(x)$ oscillates in sign — making optimization unstable and ambiguous. Standard activations are monotonic.",
    "Good activations are typically monotonic with well-behaved gradients; periodic functions create many equivalent inputs and sign-flipping gradients."),
 ],
 ("ch02","softmax"): [
  Q("open",2,["SS25 3.3"],
    "For a 3-class problem with softmax probabilities $y_k$ and cross-entropy loss $L=-\\ln(y_3)$ (true label 3), compute $\\frac{\\partial L}{\\partial z_k}$. What would you cache in the forward pass?",
    "$\\frac{\\partial L}{\\partial z_k}=y_k-\\mathbb{1}[k=3]$: i.e. $y_3-1$ for the true class and $y_k$ for the others. **Cache** the ground-truth label and the softmax outputs $y_k$ to accelerate the backward pass.",
    "The clean softmax+CE gradient is $\\hat y - y$ (prediction minus one-hot) — one of the most important results to memorize."),
 ],
 ("ch02","classification-loss"): [
  Q("open",2,["SS25 2.2"],
    "A softmax classifier over 20 classes is randomly initialized and trained with categorical cross-entropy. What is the approximate loss in the first epoch?",
    "$L\\approx-\\log\\!\\big(\\tfrac{1}{20}\\big)=\\log 20\\approx 3.0$ — a random init outputs roughly uniform probabilities $1/C$, so the expected initial CE is $-\\log(1/C)=\\log C$.",
    "Sanity check: initial CE should sit near $\\log C$. Far above ⇒ bad init/scaling; this is the 'no information' baseline."),
 ],
 ("ch02","regression-loss"): [
  Q("mc",1,["WS23 1.6"],
    "For a regression task with labels in $[-1,1]$, which final activations $f(x)$ could be used?",
    "**Valid (bounded to $[-1,1]$):** $2\\sigma(x)-1$, $\\tanh(10x)$, and $\\min(\\max(-1,x),1)$ (clamp). **Invalid:** $\\max(-1,x)$ is unbounded above, so it can exceed 1.",
    "Match the output range to the label range: sigmoid/tanh/clamp bound both sides; a one-sided ReLU-like clamp does not."),
 ],
 ("ch03","why-conv"): [
  Q("mc",2,["SS25 1.6"],
    "Which statements about CNNs are true?",
    "**True:** convolutional layers are **translation-equivariant**. **False:** low-level features are extracted in **early** (not deeper) layers; kernel size affects parameter count but **padding does not**; convolutions are **not** rotation-invariant.",
    "Conv = translation-equivariant (not rotation-invariant); params depend on $c_{in},k,c_{out}$, not padding; early layers = low-level features."),
  Q("open",1,["SS25 6.4"],
    "Name one built-in design feature of CNNs that helps with images, and explain why it helps.",
    "Any of: **spatial locality**, **weight sharing**, **translation equivariance**, or **hierarchical feature learning**. E.g. **translation equivariance** — a CNN responds consistently when an object is shifted, which matters because pedestrians/cars can appear anywhere in the frame (autonomous driving).",
    "These inductive biases are exactly why CNNs need fewer parameters and generalize on images better than FC nets."),
 ],
 ("ch03","conv-def"): [
  Q("open",2,["SS25 6.1","SS25 2.5"],
    "(a) For 224×224 RGB input and $N$ output channels, give the CONV1 parameters for Option 1 ($k{=}3,s{=}1$) vs Option 2 ($k{=}11,s{=}4$). (b) What stride makes a $k{=}3,p{=}1$ conv output $8\\times8$ from a $32\\times32$ input, and what is the downside?",
    "(a) Option 1: $3\\cdot3\\cdot3\\cdot N+N=\\mathbf{28N}$; Option 2: $3\\cdot11\\cdot11\\cdot N+N=\\mathbf{364N}$ — the big kernel costs ~13× more.\n(b) **Stride 4** gives $\\lfloor(32+2-3)/4\\rfloor+1=8$. Downside: with stride > 1, the output is **independent of some input pixels** → loss of information / lower data efficiency.",
    "Small kernels are far cheaper; large strides downsample but skip input pixels (information loss)."),
  Q("mc",1,["WS23 1.8"],
    "For a conv layer (kernel $k$, padding 1, stride 1, $m$ filters) on input $C\\times N\\times N$, which affect the **output shape**?",
    "**$N$, $k$, and $m$** affect the output shape (spatial size depends on $N,k$; output channels = $m$). The **input channel count $C$** does **not** change the output shape (it only affects per-filter depth/params).",
    "Output shape = (m, H_out, W_out); $C$ sets each filter's depth but not the output dimensions."),
 ],
 ("ch03","receptive-field"): [
  Q("open",2,["SS25 6.2","SS25 6.3"],
    "Compare receptive fields after 3 layers: Option 1 (Conv $3{\\times}3$ s1 → Conv $3{\\times}3$ s1 → MaxPool 2 s2) vs Option 2 (Conv $11{\\times}11$ s4 → MaxPool 3 s2 → Conv $5{\\times}5$ s1). Which is better for local features?",
    "Option 1: $3\\to5\\to\\mathbf{6}$. Option 2: $11\\to19\\to\\mathbf{51}$. **Option 1** has a much **smaller receptive field**, better for learning **local** features (and far fewer parameters), so it is preferred for early layers.",
    "Stacked small convs grow the receptive field slowly and cheaply; a big stride-4 kernel jumps to a huge RF fast."),
 ],
 ("ch03","pooling"): [
  Q("mc",1,["WS23 1.1"],
    "Which statements about 2D Average Pooling are true?",
    "**True:** it has **no learnable parameters** and it **reduces the spatial dimensions**. **False:** it does **not** always beat max pooling (max adds useful non-linearity/feature selection), and it does **not** reduce the **channel** dimension.",
    "Pooling (avg or max) shrinks spatial size only, channel count unchanged, no parameters."),
 ],
 ("ch03","special-conv"): [
  Q("open",1,["SS25 6.6"],
    "Give two reasons to use $1\\times1$ convolutions in an image-classification network.",
    "Any two: **reduce channels** while keeping spatial size (save compute / bottleneck); **add non-linearity** without changing spatial size; **build a deeper / higher-capacity model** without changing spatial size.",
    "1×1 conv = per-pixel channel mixing: cheap dimensionality control + extra non-linearity (the GoogLeNet trick)."),
 ],
 ("ch04","optimizers"): [
  Q("mc",1,["SS25 1.1"],
    "Your gradient updates are oscillating. Which actions might help stabilize training?",
    "**Decrease the learning rate** (smaller, steadier steps) and **try other optimizers** (e.g. Adam with adaptive/momentum behaviour). Increasing the LR or decreasing the batch size would make oscillation **worse** (bigger/noisier steps).",
    "Oscillation ⇒ steps too large/noisy ⇒ lower LR, add momentum/adaptivity. Smaller batches add noise, not stability."),
  Q("open",1,["SS25 3.2"],
    "For $L(\\theta)=\\theta^2-6\\theta+9$ with Newton's update $\\theta_{t+1}=\\theta_t-H^{-1}\\nabla L$, $\\theta_0=0$: find $\\theta_1,\\theta_2$.",
    "$\\nabla L=2\\theta-6$, $H=2$. $\\theta_1=0-\\tfrac{1}{2}(-6)=\\mathbf{3}$; $\\theta_2=3-\\tfrac{1}{2}(2\\cdot3-6)=\\mathbf{3}$. Newton's method reaches the minimum of a quadratic in **one step** ($\\theta^\\*=3$).",
    "Second-order (Newton) optimization solves a quadratic exactly in one step — the appeal, and why it's too expensive for big nets (needs the Hessian)."),
  Q("open",1,["SS25 3.1"],
    "Name the two techniques Adam combines and how each improves on plain SGD.",
    "**Momentum** — uses an exponential moving average of past gradients to **smooth updates** and accelerate convergence. **RMSProp** — adapts a **per-parameter learning rate** using an EMA of squared gradients (variance). Adam fuses both (plus bias correction).",
    "Adam = momentum (1st moment) + RMSProp (2nd moment). Smooth direction × adaptive per-parameter scale."),
 ],
 ("ch04","over-underfitting"): [
  Q("open",2,["SS25 2.3"],
    "After 60 epochs the training loss keeps decreasing but the validation loss starts rising. Name the phenomenon and two fixes.",
    "**Overfitting.** Any two fixes: **early stopping**, **L1/L2 regularization / weight decay**, **dropout**, **data augmentation**, **Batch/Layer Norm** to stabilize, or **collect more data**.",
    "Rising val loss + falling train loss = textbook overfitting; the fixes are the whole regularization toolbox."),
 ],
 ("ch04","regularization"): [
  Q("open",1,["SS25 5.3"],
    "Your weights are sparse (most near 0, a few very large). How does L2 regularization change this distribution, and what's the benefit?",
    "L2 makes the weights **more evenly distributed**, penalizing large weights so none dominate. Benefit: the model **uses more of its capacity** and generalizes better (less reliance on a few large weights).",
    "L2 spreads weight magnitude (shrinks large weights); L1 would instead push many weights to exactly 0 (sparsity)."),
 ],
 ("ch04","batchnorm"): [
  Q("open",2,["SS25 2.1"],
    "Why can Batch-Norm behave poorly when the mini-batch contains only one sample ($m=1$)?",
    "With $m=1$ the batch mean equals the sample and the **variance is 0**, so normalizing $\\frac{x-\\mu}{\\sqrt{\\sigma^2+\\epsilon}}$ is meaningless/unstable (variance in the denominator) and the centered value is always 0 → information loss. Single-sample statistics also don't represent the dataset.",
    "BN needs a batch big enough for meaningful statistics; for tiny batches use Layer/Group Norm instead."),
  Q("mc",1,["SS25 1.5"],
    "Which of the following adds learnable parameters to the network?",
    "**Batch Normalization** (learnable $\\gamma,\\beta$). **Dropout**, **weight decay**, and **weight initialization** add **no** learnable parameters.",
    "Only BN among these has trainable parameters; dropout/weight-decay/init are parameter-free mechanisms."),
 ],
 ("ch04","weight-init"): [
  Q("mc",1,["SS25 1.4"],
    "Which statements about weight initialization are true?",
    "**True:** Batch norm reduces the impact of poor initialization; **Xavier doesn't work well with ReLU**; **Kaiming considers the input-layer size only**. **False:** 'Kaiming considers both input and output sizes' (that's the Xavier flavour).",
    "Xavier ↔ tanh/sigmoid (fan-in & fan-out); Kaiming/He ↔ ReLU (fan-in only, variance $2/n_{in}$)."),
 ],
 ("ch04","transfer-learning"): [
  Q("open",1,["SS25 5.4","SS25 5.5"],
    "For transferring to a 'human present?' road-camera classifier, you have pretrained models on (a) ImageNet, (b) Bird200k, (c) road-scene signs. Which is least suitable, and how would you use the chosen encoder?",
    "**Least suitable: (b) the bird classifier** — a **domain mismatch** between bird images and road images. Using the chosen encoder: **resize inputs** if needed, **add new layers** on top of the embeddings for your output, and **freeze the encoder weights** during training.",
    "Pick a backbone whose pretraining domain is close to the target; freeze it and train only a small new head when data is scarce."),
 ],
 ("ch05","cnn-architectures"): [
  Q("mc",1,["SS25 1.8"],
    "Which changes were made from LeNet to AlexNet?",
    "**True:** **using ReLU** as the activation, and **increasing depth and number of parameters**. **False:** skip connections (that's ResNet) and 'introducing convolutional layers' (LeNet already had them).",
    "AlexNet's leap over LeNet: ReLU + more depth/params + dropout — not skip connections (those came with ResNet)."),
 ],
 ("ch05","skip-resnet"): [
  Q("open",2,["SS25 6.5"],
    "For a residual block $H(x)=x+F(x)$ with $F=F_2(F_1(x))$, compute $\\frac{\\partial L}{\\partial x}$ and explain what happens when $\\frac{\\partial F}{\\partial x}\\to0$.",
    "$\\frac{\\partial L}{\\partial x}=\\frac{\\partial L}{\\partial H}\\big(1+\\frac{\\partial F}{\\partial x}\\big)$. When the inner gradients vanish ($\\frac{\\partial F}{\\partial x}\\to0$), $\\frac{\\partial L}{\\partial x}\\to\\frac{\\partial L}{\\partial H}$ — the gradient **passes straight through the block** (the skip path), so it doesn't vanish.",
    "The additive identity gives a guaranteed gradient highway: even if the block learns nothing, gradients still flow."),
 ],
 ("ch05","autoencoders"): [
  Q("mc",1,["WS23 1.4"],
    "Which statements about autoencoders are true?",
    "**True:** an autoencoder **can be used as a lossy compressor** (bottleneck code). **False:** the hidden layer should be **smaller** (not larger) than the input; encoder/decoder need not have equal layer counts; and not *any* autoencoder can perfectly learn the identity (a tight bottleneck can't).",
    "AE = lossy compression via a bottleneck; making the latent ≥ input invites the trivial identity / no compression."),
 ],
 ("ch05","unet"): [
  Q("mc",1,["WS23 1.5"],
    "Which statements about upsampling are true?",
    "**True:** **transposed convolution adds trainable parameters** whereas interpolation does not; and **transposed convolution ≈ unpooling followed by a standard convolution**. The other options (conv∘transposed-conv = identity; transposed-conv = bilinear-interp + conv) are false.",
    "Learned upsampling (transposed conv) has parameters; interpolation (nearest/bilinear) does not."),
 ],
 ("ch05","gan"): [
  Q("mc",1,["WS23 1.7"],
    "Which statements about GANs are true?",
    "**True:** the **generator maximizes the probability the discriminator labels its output 'real'**, and after training the **discriminator loss tends to a constant** (it can no longer tell real from fake). **False:** the discriminator does not model the input distribution explicitly, and it cannot be used as a sampler (the generator samples).",
    "G fools D (relabel fakes as real); at equilibrium D≈0.5 everywhere (constant loss). Sampling is the generator's role."),
 ],
 ("ch06","rnn"): [
  Q("mc",2,["SS25 1.2"],
    "Which statements about RNNs are true?",
    "**True:** RNNs **inherently model sequence order** through recurrence, so they don't need positional encoding; and they **maintain a hidden state updated each timestep** to capture temporal dependencies. **False:** RNNs suffer **both** vanishing *and* exploding gradients; and each output depends on the hidden state, **not only** the current input.",
    "RNNs get order for free (sequential processing) — unlike Transformers which need positional encoding."),
  Q("open",2,["SS25 7.1","SS25 7.2"],
    "Write the (activation-free) RNN cell-state update $C(t)$, then unroll it to show $C(t)$ depends on all previous inputs.",
    "$C(t)=W_c\\,C(t{-}1)+W_x X_t$. Unrolling: $C(t)=\\sum_{i=0}^{t} W_c^{\\,t-i} W_x X_i = W_c^t W_x X_0 + \\dots + W_x X_t$ — every past input $X_i$ contributes, weighted by $W_c^{\\,t-i}$.",
    "The $W_c^{\\,t-i}$ factor is exactly why gradients vanish ($\\|W_c\\|<1$) or explode ($>1$) over long sequences."),
  Q("open",1,["SS25 7.3"],
    "An RNN does well on short sentences but worse on long ones. (a) Name the phenomenon. (b) Name a major cause.",
    "(a) **Loss of long-term memory / vanishing (or exploding) gradients.** (b) Old input embeddings are **multiplied by the weight matrix repeatedly** (and passed through the activation many times), so their influence shrinks (or blows up) over many steps.",
    "Repeated multiplication by $W_c$ across timesteps = exponential decay/growth → short memory. LSTMs add a cell-state highway to fix it."),
 ],
 ("ch06","lstm"): [
  Q("mc",1,["SS25 1.3"],
    "Which statements correctly describe the gating mechanisms in an LSTM?",
    "**True:** the gates **allow the network to forget or retain information over long sequences**. **False:** gates are not there to limit parameters, not to reduce hidden-state dimensionality over time, and not to make the output depend only on the most recent token.",
    "Gates (forget/input/output) regulate the cell-state highway — what to keep, write, and read."),
  Q("open",1,["SS25 2.6"],
    "Explain the role of the sigmoid activation in an LSTM unit.",
    "The sigmoid acts as a **gate**: in the input/forget/output gates it outputs values in $[0,1]$ — like a soft switch — deciding **how much information to keep or forget**.",
    "Sigmoid ∈ [0,1] = a valve; that's why ReLU (unbounded) is a poor gate activation."),
 ],
 ("ch06","transformers-attention"): [
  Q("mc",1,["WS23 1.3"],
    "Which statements about Transformers are true?",
    "**True:** the **attention mechanism itself is invariant to order**; and due to **masked attention**, the decoder output depends only on previous outputs and the encoder. **False:** Transformers apply beyond text (vision, audio), and they do **not** rely on convolutional layers for context.",
    "Self-attention is permutation-invariant (hence positional encoding); causal masking enforces left-to-right decoding."),
  Q("open",2,["SS25 2.4","SS25 7.4"],
    "Why are Transformers better suited than RNNs for GPU parallelism, and why do they capture long-range dependencies well?",
    "**Parallelism:** self-attention computes interactions between **all tokens simultaneously**, so the sequence is processed in parallel, whereas RNNs are **sequential** (each step waits for the previous one). **Long-range:** every token can **directly attend to every other token**, regardless of distance, so far-apart dependencies are captured in one step (no multi-step decay).",
    "Attention = parallel + direct token-to-token links; RNN = sequential + distance-decayed memory."),
  Q("open",1,["SS25 7.5"],
    "In $\\text{Attention}(Q,K,V)=\\text{softmax}\\!\\big(\\frac{QK^\\top}{\\sqrt d}\\big)V$ with $Q,K,V\\in\\mathbb{R}^{n\\times d}$, is softmax applied over rows or columns? Why?",
    "Over the **rows** of the attention matrix. Each query's output is a **weighted sum of values**, and those weights must **sum to 1** — softmax over the row (across all keys) normalizes the weights for that query.",
    "Row-wise softmax ⇒ each query distributes attention (summing to 1) over all keys."),
  Q("open",1,["SS25 7.6"],
    "Transformers stack many attention layers and can suffer vanishing gradients. (a) What fix (borrowed from deep CNNs) helps? (b) Is the RNN vanishing-gradient cause the same?",
    "(a) **Residual / skip connections** around each sub-block. (b) **No** — Transformer vanishing comes from the **number of layers (depth)**, whereas RNN vanishing comes from the **length of the input sequence** (repeated recurrence).",
    "Same cure (residuals), different cause: depth (Transformer) vs sequence length (RNN)."),
 ],
 ("ch06","positional-encoding"): [
  Q("open",1,["WS23 2.2"],
    "Why is positional encoding used in Transformers, and what problem arises without it?",
    "It **adds information about token position** in the sequence. **Without it**, attention treats the input as an **unordered set** (no inherent notion of order), so the model can't use word order — yet order changes meaning ('dog bites man' ≠ 'man bites dog').",
    "No recurrence/convolution ⇒ no built-in order ⇒ positional encoding supplies it."),
 ],
 ("ch07","affine-derivatives"): [
  Q("open",1,["SS25 4.1"],
    "For an MLP $z_1=W_1 x_i+b_1$, $a=\\text{ReLU}(z_1)$, $z_2=W_2 a+b_2$, $\\hat y=\\sigma(z_2)$ on a flattened $w\\times h\\times3$ image with $z_1\\in\\mathbb{R}^d$ (binary output), give the shapes of $W_1,b_1,W_2,b_2$.",
    "$W_1:(d,\\,3wh)$, $b_1:(d,1)$; $W_2:(1,d)$, $b_2:(1,1)$. (Input flattened to $3wh$; hidden size $d$; single output for binary classification.)",
    "Layer shapes follow input→hidden→output dims; one bias per output unit of each layer."),
  Q("open",2,["SS25 4.3"],
    "Given upstream $\\frac{\\partial L}{\\partial z_1}$ for $z_1=W_1 x_i+b_1$: (a) write $\\frac{\\partial L}{\\partial W_1},\\frac{\\partial L}{\\partial x_i},\\frac{\\partial L}{\\partial b_1}$; (b) which need not be computed in training, and why?",
    "(a) $\\frac{\\partial L}{\\partial W_1}=\\frac{\\partial L}{\\partial z_1}x_i^\\top$, $\\frac{\\partial L}{\\partial x_i}=W_1^\\top\\frac{\\partial L}{\\partial z_1}$, $\\frac{\\partial L}{\\partial b_1}=\\frac{\\partial L}{\\partial z_1}$.\n(b) $\\frac{\\partial L}{\\partial x_i}$ is **not needed** — it's the gradient w.r.t. the **input**, which is not a learnable parameter (you'd only need it to pass gradients further back, but here $x_i$ is the network input).",
    "You only need gradients w.r.t. **parameters** to update them; the input gradient matters only for propagating to earlier layers."),
 ],
 ("ch07","chain-rule-scope"): [
  Q("open",1,["SS25 4.4"],
    "At one iteration $z_2\\approx10^6$ for all samples before a sigmoid output. Estimate the gradient of the learnable parameters.",
    "**≈ 0.** The sigmoid is deep in its **saturated 'dead zone'** where $\\sigma'(z_2)\\approx0$, so every upstream gradient gets multiplied by ~0 → the parameter gradients are essentially zero (no learning this step).",
    "Saturated sigmoid/tanh kills gradients (vanishing). Keep pre-activations near 0 via normalization/good init."),
 ],
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
            key = (cid, kp["id"])
            for q in NEW.get(key, []):
                if any(existing["q"] == q["q"] for existing in kp["questions"]):
                    continue
                kp["questions"].append(q)
                added += 1
                changed = True
        if changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"updated {p.name}")
    # report any keys that didn't match a KP
    valid = set()
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        if pathlib.Path(f).name == "chapters.json": continue
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for kp in d["knowledge_points"]:
            valid.add((d["id"], kp["id"]))
    for key in NEW:
        if key not in valid:
            print(f"  ! target not found: {key}")
    print(f"added {added} coverage questions")

if __name__ == "__main__":
    main()
