#!/usr/bin/env python3
"""Coverage pass: WS24 (WS_2024). Mines the WS24 endterm into the right knowledge
points. Multi-part problems are bundled into one card with several sources.
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
 ("ch01","data-leakage"): [
  Q("open",2,["WS24 2.1"],
    "You observe the validation loss is *smaller* than the training loss and your supervisor suspects a bug. Name a potential problem in your code or data that could cause this.",
    "Any of: **data leakage** — the validation set contains training samples; the **validation set has unusually easy samples**; **too-aggressive augmentation on the training set** inflates the training loss; or train and validation are drawn from **different distributions** / the validation set is **too small**.",
    "Val < train is a red flag for leakage or an unrepresentative/easy validation split, or for heavy train-only augmentation."),
 ],
 ("ch01","augmentation"): [
  Q("open",1,["WS24 2.5"],
    "How can data augmentation improve model generalization (1p)? Give one example of an augmentation technique (1p).",
    "It **increases the diversity of the training set** by creating modified versions of the inputs, making the model **robust to variations / introducing feature invariance** (and virtually increasing dataset size). Example: **random rotation, flipping, cropping, color jittering, or adding Gaussian noise**.",
    "Augmentation = more in-distribution variety ⇒ invariance and less overfitting, without collecting new data."),
 ],
 ("ch01","class-imbalance"): [
  Q("open",1,["WS24 2.14"],
    "You have 4,000 cat images and 100 dog images for binary classification. What problem do you foresee with this distribution (1p)? Provide two solutions for training without acquiring more data (1p).",
    "**Problem:** class imbalance → the network is **biased toward the majority class** (cats), giving poor accuracy on dogs. **Two solutions (any):** undersample cats / oversample dogs / augment the minority class / reweight the dataloader (e.g. `WeightedRandomSampler`) / reweight the loss function / use transfer learning.",
    "Counter imbalance by rebalancing the data stream or the loss. (Per-class LR tweaks and k-fold do NOT fix imbalance.)"),
 ],
 ("ch02","activations"): [
  Q("mc",2,["WS24 1.2"],
    "Which of the following is/are true about activation functions?",
    "**True:** *Sigmoid can lead to vanishing gradients* (it saturates). **False:** $\\log(\\text{ReLU}(x+1))$ is a poor activation (undefined where $\\text{ReLU}(x+1)=0$); *Parametric ReLU* avoids the Dead-ReLU problem via its learnable negative slope; *Tanh* still saturates and **does** suffer vanishing gradients despite being zero-centered.",
    "Zero-centering (Tanh) helps optimization but does NOT remove saturation/vanishing gradients.",
    options=[("Sigmoid can lead to vanishing gradients.",True),
             ("$\\log(\\text{ReLU}(x+1))$ is suitable to add non-linearity to a network.",False),
             ("Parametric ReLU always has the 'Dead ReLU' problem.",False),
             ("Tanh will not lead to vanishing gradients because it is zero-centered.",False)]),
  Q("open",2,["WS24 2.10"],
    "Describe what 'vanishing gradient' is in the context of backpropagation through activation functions (1p). Give one example of a function that suffers from it (1p).",
    "When activation functions **saturate**, their derivative becomes ~0, so by the **chain rule** the gradient of the loss w.r.t. parameters gets **extremely small in the early (shallow) layers** → those layers barely learn. **Example: Sigmoid or Tanh** (ReLU does not suffer this).",
    "Vanishing gradient ≠ dead ReLU: it's saturation-driven shrinkage through many layers, classically from Sigmoid/Tanh."),
 ],
 ("ch02","backprop"): [
  Q("mc",1,["WS24 1.7"],
    "In PyTorch, what is/are the correct order(s) of steps when training a model with gradient descent?",
    "**Valid:** any order where the gradients are **zeroed before backpropagation** and parameters are **updated after** it — both *zero → forward → backward → update* and *forward → zero → backward → update* work. **Invalid:** backprop before zeroing, or updating before backprop.",
    "Invariant: `optimizer.zero_grad()` before `loss.backward()`, and `optimizer.step()` after it. The forward pass may sit before or after the zeroing.",
    options=[("Zero the gradients → forward pass → backpropagation → update parameters.",True),
             ("Forward pass → zero the gradients → backpropagation → update parameters.",True),
             ("Backpropagation → zero the gradients → update parameters.",False),
             ("Forward pass → update parameters → backpropagation.",False)]),
 ],
 ("ch02","classification-loss"): [
  Q("open",2,["WS24 2.4"],
    "Explain why minimizing the cross-entropy $H(p,q)$ between class probabilities $q$ (network) and target $p$ is equivalent to minimizing the KL divergence $D_{KL}(p\\|q)=H(p,q)-H(p)$.",
    "Because $H(p)$ — the **entropy of the fixed target distribution** $p$ — does **not depend on the model parameters**; it is a **constant** with zero gradient. So $\\min_\\theta D_{KL}(p\\|q)=\\min_\\theta\\big(H(p,q)-H(p)\\big)=\\min_\\theta H(p,q)$.",
    "Dropping a parameter-independent constant doesn't change the argmin — that's why CE training = KL minimization."),
  Q("open",2,["WS24 2.13"],
    "Write down the formula for the binary cross-entropy loss (1p) and define all the variables (1p).",
    "$L(\\hat y_i,y_i)=-\\big(y_i\\log\\hat y_i+(1-y_i)\\log(1-\\hat y_i)\\big)$, or batched $L=-\\frac1N\\sum_{i=1}^{N}\\big(y_i\\log\\hat y_i+(1-y_i)\\log(1-\\hat y_i)\\big)$. Here $y_i\\in\\{0,1\\}$ is the **ground-truth label**, $\\hat y_i\\in(0,1)$ is the **model's predicted probability**, and $N$ is the **batch size**.",
    "BCE needs a single probability output $\\hat y_i$ (sigmoid); the two log terms reward the correct class for label 1 vs 0."),
 ],
 ("ch03","why-conv"): [
  Q("mc",1,["WS24 1.6"],
    "You classify centered hieroglyphs, but some are slightly translated. Which layers help make the model robust to these translations?",
    "**Convolutional layers combined with Max Pooling layers.** Convolutions are translation-**equivariant**, and max pooling adds **local translation invariance**, so small shifts don't change the prediction. Conv-only, pool-only, or conv+FC are weaker against translation.",
    "Conv (equivariance) + pooling (local invariance) is the classic translation-robustness combo.",
    options=[("Only Convolutional layers.",False),
             ("Only Max Pooling layers.",False),
             ("Convolutional layers combined with Max Pooling layers.",True),
             ("Convolutional layers combined with fully connected (FC) layers.",False)]),
  Q("open",2,["WS24 2.6"],
    "Give two reasons why convolutional layers are more efficient for image-related tasks than dense (fully-connected) layers.",
    "Any two: (1) convs operate on **neighboring, correlated pixels / extract local features** instead of connecting to all pixels; (2) **translation invariance/equivariance**; (3) **parameter sharing** → far **fewer parameters**; (4) they **don't require a fixed input size**.",
    "Locality + weight sharing are the core inductive biases that make CNNs cheap and effective on images."),
  Q("open",1,["WS24 3.1"],
    "Explain the role of the convolutional layers, pooling layers, and fully connected layers in a CNN (one or two sentences each).",
    "**Conv layers:** extract spatial features / detect patterns (edges, textures), building hierarchical representations. **Pooling layers:** reduce the spatial dimensions of feature maps → lower compute and overfitting while retaining essential info (and adding translation invariance). **FC layers:** integrate the extracted features into final class scores → make the classification/regression decision.",
    "Conv = feature extraction, pool = spatial downsampling, FC = decision head."),
 ],
 ("ch03","conv-def"): [
  Q("open",1,["WS24 2.8"],
    "For a convolutional layer with kernel size 3, how can you set the padding and stride so the output has the same size as the input? What is the shape of the weights if the output has only one channel?",
    "**Padding = 1, stride = 1** (for $k=3$, $p=\\frac{k-1}{2}=1$ with $s=1$ preserves spatial size). Weight shape (PyTorch $[out,in,h,w]$): $\\mathbf{[1,\\,C_{in},\\,3,\\,3]}$ — with $C_{in}=1$ for grayscale or $3$ for RGB (TensorFlow $[h,w,in,out]=[3,3,C_{in},1]$).",
    "'Same' padding for odd kernel $k$: $p=(k-1)/2$, $s=1$. One output channel ⇒ a single $C_{in}\\times3\\times3$ filter."),
  Q("open",1,["WS24 2.9"],
    "Write down the conv weights (one output channel, RGB input, $3\\times3$, padding 1, stride 1) so the layer maps an RGB image to grayscale by $Y=0.30R+0.59G+0.11B$.",
    "Three $3\\times3$ kernels (one per input channel), each **all zeros except the center**: R-kernel center $=0.30$, G-kernel center $=0.59$, B-kernel center $=0.11$. With padding 1 / stride 1, the center-only weight performs a **per-pixel weighted sum** of the three channels → grayscale.",
    "Center-only kernels = a $1\\times1$-style channel combination embedded in a $3\\times3$ filter (the off-center weights are 0)."),
  Q("open",1,["WS24 3.4"],
    "Explain a pro (1p) and a con (1p) of using a larger kernel size in the convolutional layers.",
    "**Pro:** a larger kernel gives a **larger receptive field per layer**, so the model can detect broader patterns earlier. **Con:** it has **more parameters** → higher computational cost and a greater risk of **overfitting** (which is why stacking small $3\\times3$ kernels is usually preferred).",
    "Bigger kernel = bigger RF fast but costly; stacked small kernels reach the same RF with fewer params and more non-linearity."),
 ],
 ("ch03","receptive-field"): [
  Q("open",2,["WS24 3.2","WS24 3.3"],
    "Explain the term 'receptive field' (1p). For a first conv layer with 6 filters, kernel size 5, stride 1, padding 1, what is its receptive field (1p)? What is the receptive field of a neuron in the final fully-connected layer (1p)?",
    "**Receptive field** = the region of the input image that a particular output feature is sensitive to / depends on. **First conv layer:** RF $=$ kernel size $=\\mathbf{5\\times5}$. **Final FC neuron:** it connects to all features, so its receptive field is the **whole image** (e.g. $32\\times32$).",
    "RF grows from the kernel size (first conv) to the entire image (a fully-connected neuron sees everything)."),
 ],
 ("ch03","special-conv"): [
  Q("mc",1,["WS24 1.3"],
    "Which of the following is/are true about $1\\times1$ convolutions?",
    "**True:** they **change the size of the channel dimension**, and they can perform **feature-map pooling across channels**. **False:** for an $H\\times W\\times C$ input the output keeps spatial size ($H\\times W\\times C_{out}$, not $1\\times1\\times C$); and their parameter count depends on $C_{in}\\cdot C_{out}$ (+bias), **not** on the input's spatial dimensions.",
    "1×1 conv = per-pixel channel mixing: it reshapes the channel axis only, spatial size unchanged.",
    options=[("It is used to change the size of the channel dimension.",True),
             ("Given an HxWxC input, the output of a 1x1 conv layer has dimensionality 1x1xC.",False),
             ("It can be used for feature-map pooling.",True),
             ("The number of parameters of a 1x1 conv layer depends on the input's spatial dimensions.",False)]),
 ],
 ("ch04","over-underfitting"): [
  Q("mc",1,["WS24 1.5"],
    "Training for a while, the training loss keeps decreasing but the validation loss is increasing. Which methods can optimize this issue?",
    "This is **overfitting**. **Early stopping** and a **learning-rate schedule** help. **Increasing the learning rate** or **removing data augmentation** would make overfitting **worse**.",
    "Falling train + rising val = overfitting; cure with early stopping / regularization, not by removing augmentation.",
    options=[("Early-stopping.",True),
             ("Increase the learning rate.",False),
             ("Use a learning-rate schedule.",True),
             ("Remove data augmentation.",False)]),
  Q("open",2,["WS24 4.1","WS24 4.2","WS24 4.3"],
    "Two CNNs are trained with the same optimizer/hyperparameters. (4.1) After 200 epochs, Model 1 has high loss on **both** train and val — which is worse, what is the phenomenon, how to improve it? (4.2) After adding layers to Model 1, its **validation** loss rises while train falls — what is the phenomenon? (4.3) Which model would you deploy, and what technique gives the best performance?",
    "**4.1** Model 1 is **underfitting** (too low capacity) → increase parameters/capacity, tune hyperparameters, add BatchNorm, normalize inputs. **4.2** Now Model 1 **overfits**. **4.3** Deploy the model with the **lowest validation loss** and use **early stopping** (keep the epoch with best val loss) to avoid the overfitting tail.",
    "Underfit ⇒ add capacity; overfit ⇒ regularize + early stopping. Deployment choice is driven by validation loss."),
 ],
 ("ch04","hyperparams-lr"): [
  Q("open",2,["WS24 2.12"],
    "For GPU-memory reasons you decrease your mini-batch size. Should you increase or decrease your learning rate (1p)? Why (1p)?",
    "**Decrease** the learning rate. A smaller mini-batch is **less representative of the full data** — its gradient estimate has **higher variance / more noise** — so a large LR on noisy gradients risks **overshooting / diverging**; lowering the LR keeps updates stable.",
    "Smaller batch ⇒ noisier gradient ⇒ smaller, safer steps. (Linear-scaling rule: LR roughly scales with batch size.)"),
  Q("open",1,["WS24 6.6"],
    "A scheduler computes `get_lr = base_lr * gamma ** (epoch // n)`. What class is this (1p)? Explain its role during training (1p) and give two variants (2p).",
    "It is a **(step) learning-rate scheduler** (`StepLR`). **Role:** it **decays the learning rate by a factor `gamma` every `n` epochs**, which stabilizes training, avoids overshooting / oscillation around the minimum, and helps converge better. **Two variants (any):** `ExponentialLR`, `CosineAnnealingLR`, `MultiStepLR`, `PolynomialLR`, `LinearLR`, `CyclicLR`, `OneCycleLR`, `ReduceLROnPlateau`, `LambdaLR`.",
    "Step decay drops LR in stages; cosine/exponential/plateau schedulers vary how the LR is annealed over training."),
  Q("open",1,["WS24 4.4"],
    "Grid-searching three learning rates $\\tau_1,\\tau_2,\\tau_3$ for vanilla SGD gives three training-accuracy curves. The official answer is $\\tau_1>\\tau_3>\\tau_2$. Explain the reasoning that orders learning rates from these curves.",
    "A **larger LR** makes training accuracy **rise faster initially** but, if too large, plateaus lower or oscillates; a **smaller LR** rises **slowly and steadily**. Reading the curves: the fastest, stable climber is the largest stable LR ($\\tau_1$), the slowest climber is the smallest ($\\tau_2$), leaving the intermediate one ($\\tau_3$) in between → $\\tau_1>\\tau_3>\\tau_2$.",
    "Larger LR ⇒ faster but rougher convergence; smaller LR ⇒ slower but smoother. Map curve speed/stability to LR magnitude."),
 ],
 ("ch04","optimizers"): [
  Q("open",2,["WS24 6.1"],
    "Identify the optimizer from each pseudocode: **Alg1** updates $b_t\\!\\leftarrow\\!\\mu b_{t-1}+g_t,\\ \\theta_t\\!\\leftarrow\\!\\theta_{t-1}-\\gamma b_t$; **Alg2** uses $v_t\\!\\leftarrow\\!\\alpha v_{t-1}+(1-\\alpha)g_t^2,\\ \\theta_t\\!\\leftarrow\\!\\theta_{t-1}-\\gamma g_t/(\\sqrt{v_t}+\\epsilon)$; **Alg3** keeps $m_t,v_t$ with $\\beta_1,\\beta_2$ and bias-corrected $\\tilde m_t,\\tilde v_t$.",
    "**Alg1 = GD/SGD with momentum** ($\\mu$ is the momentum coefficient; $b_t$ is a running average of gradients). **Alg2 = RMSprop** (EMA of squared gradients re-scales each step). **Alg3 = Adam** (first + second moment EMAs with bias correction).",
    "Recognize by the state: velocity only ⇒ momentum; squared-grad EMA ⇒ RMSprop; both + bias correction ⇒ Adam."),
  Q("open",2,["WS24 6.2","WS24 6.3"],
    "(6.2) What is the major difference between the momentum optimizer (Alg1) and RMSprop (Alg2), and the idea behind it? (6.3) What happens when the momentum coefficient $\\mu>0$ in Alg1?",
    "**6.2:** RMSprop introduces **second-moment (squared-gradient / variance) information** to **re-scale each update by its variance**, dampening high-variance directions — Alg1 uses only a running average of gradients (first moment). **6.3:** With $\\mu>0$, Alg1 **accumulates a moving average of gradients (momentum)** → it **reduces oscillations and speeds up convergence**, but can **overshoot / diverge** past minima.",
    "Momentum smooths the *direction* (1st moment); RMSprop adapts the *scale* (2nd moment). Adam fuses both."),
  Q("open",1,["WS24 6.4"],
    "Explain the $\\beta_1$ and $\\beta_2$ hyperparameters of Adam.",
    "$\\beta_1$ is the **decay-rate coefficient of the running average of the first moment** (gradient mean); $\\beta_2$ is the **decay-rate coefficient of the running average of the second moment** (squared gradients / variance). They control how much past vs current gradient information is retained.",
    "Higher $\\beta$ ⇒ longer memory of past gradients. (Making $m,v$ biased is a *consequence*, not the purpose, of $\\beta$.)"),
  Q("open",1,["WS24 6.5"],
    "What is the major difference between Newton's method and the first-order optimizers above, and why is it not widely used for deep learning?",
    "Newton's method is **second-order** — it uses the **Hessian** (curvature), not just the gradient. It is impractical for deep learning because **computing and inverting the Hessian** over millions of parameters is **prohibitively expensive in compute and memory**.",
    "Second-order = exact curvature (one-step on quadratics) but $O(\\text{params}^2)$ Hessian ⇒ infeasible at scale."),
 ],
 ("ch04","batchnorm"): [
  Q("open",2,["WS24 2.3"],
    "A convolutional layer outputs shape $N,H,W,C$ and batch normalization is applied. Across which dimension(s) is the normalization performed? (Equivalently, state the shape of the mean array.)",
    "Normalization is performed **across $N,H,W$** — one mean/variance **per channel** — so the **mean array has shape $(1,1,1,C)$**. Each channel is normalized using statistics pooled over the batch and the spatial dimensions.",
    "Conv BN = per-channel: pool over batch + spatial; FC BN = per-feature (pool over batch only)."),
 ],
 ("ch05","vae"): [
  Q("open",2,["WS24 2.2"],
    "What are the main differences between a standard autoencoder and a variational autoencoder?",
    "A **standard AE** imposes **no structure on the latent space** — it only compresses and reconstructs the input (reconstruction loss only). A **VAE imposes a prior on the latent space** (learns a probability distribution), **samples from the latent distribution**, and adds a **KL-divergence term** to the loss → enabling generation of new samples.",
    "VAE = AE + a regularized, samplable latent (KL to a prior). Plain AE's latent has 'holes', so it can't generate."),
 ],
 ("ch05","autoencoders"): [
  Q("open",1,["WS24 3.6","WS24 3.7"],
    "Explain the primary purpose of an autoencoder (3.6). What are its two main components and the role of each (3.7)?",
    "**Purpose:** compress the input into a **lower-dimensional (bottleneck) representation** and **reconstruct** it, minimizing reconstruction error → dimensionality reduction / feature extraction. **Components:** the **Encoder** compresses the input, capturing the essential information as a latent code; the **Decoder** reconstructs the original input from that code.",
    "Encoder ↓ to bottleneck, Decoder ↑ back to input; the bottleneck forces a compact representation."),
  Q("open",1,["WS24 3.8"],
    "How can you modify an autoencoder to perform classification (1p)? What difference does pretraining the autoencoder on the same dataset before fine-tuning make (1p)?",
    "**Modification:** replace the **decoder** with a **fully-connected classification head** on top of the encoder's latent code. **Pretraining effect:** the encoder learns **good latent representations**, so the classifier **converges faster (and potentially better)** during fine-tuning.",
    "Encoder-as-feature-extractor + new head is the standard AE→classifier recipe; pretraining warm-starts the encoder."),
 ],
 ("ch05","unet"): [
  Q("open",1,["WS24 2.11"],
    "Describe the two steps involved in an upconvolution (transposed convolution).",
    "In order: **(1) upsample** the input by inserting zeros between elements (intermediate zero-padding / unpooling); **(2)** apply a **regular convolution** over the upsampled feature map. (Calling it 'transposed convolution' is only accepted if broken down into these two steps.)",
    "Upconv = zero-insertion upsampling **then** an ordinary conv; order matters."),
 ],
 ("ch06","rnn"): [
  Q("open",2,["WS24 7.1"],
    "When training an RNN, the training loss doesn't decrease. What problem with RNNs could cause this?",
    "**Vanishing or exploding gradients.** Repeated multiplication by the recurrent weight across timesteps makes gradients **shrink toward 0** (no learning) or **blow up** (unstable), so the loss fails to decrease.",
    "Same recurrent weight applied every step ⇒ exponential decay/growth of gradients over the sequence."),
  Q("open",2,["WS24 7.2","WS24 7.3","WS24 7.4"],
    "For a simplified linear RNN $h_t=W_h h_{t-1}+W_x x_t$ with scalar states and $o=h_n$, $\\frac{\\partial L}{\\partial o}=1$: (7.2) derive $\\frac{\\partial L}{\\partial W_x}$ for $n=3$; (7.3) give the general-$n$ formula; (7.4) for which $W_h$ does the problem occur, the multi-dim condition, the problematic term, and an easy fix that doesn't change the architecture.",
    "Since $\\frac{\\partial L}{\\partial o}=1$, $\\frac{\\partial L}{\\partial W_x}=\\frac{\\partial h_n}{\\partial W_x}$. **(7.2) $n=3$:** $\\;x_3+W_h x_2+W_h^2 x_1$. **(7.3) general:** $\\;\\frac{\\partial L}{\\partial W_x}=\\sum_{k=1}^{n}W_h^{\\,n-k}x_k=x_n+W_h x_{n-1}+\\dots+W_h^{\\,n-1}x_1$. **(7.4)** vanishing if $|W_h|<1$, exploding if $|W_h|>1$; multi-dim: the largest **$|$eigenvalue$|$** of $W_h$ is $<1$ or $>1$; the problematic part is the **exponential term $W_h^{\\,n-1}$**; an easy fix is **gradient clipping** (for the exploding case).",
    "The $W_h^{\\,n-k}$ factors are exactly the source of vanishing/exploding gradients; LSTMs add a cell-state highway, clipping caps explosions."),
 ],
 ("ch06","lstm"): [
  Q("open",2,["WS24 2.7"],
    "In LSTMs, why do we apply Tanh to the cell state before using it (1p), but sigmoid for the gates (1p)?",
    "**Tanh** bounds the cell-state values to $[-1,1]$, **preventing uncontrolled growth** over long sequences. **Sigmoid** (range $[0,1]$) makes the gates act as **soft switches**, controlling **how much information flows through** (forget / write / read fractions).",
    "Tanh = bounded content; sigmoid = a valve in $[0,1]$. That's why ReLU (unbounded) is a poor gate activation."),
  Q("open",1,["WS24 7.5"],
    "Explain how the three gates in an LSTM control the cell state.",
    "**Forget gate:** decides how much of the previous (long-term) cell state to **discard**. **Input gate:** controls how much **new information is written** into the cell state. **Output gate:** controls how much of the cell state is **exposed as the output** / short-term hidden state.",
    "Forget→erase, input→write, output→read — three sigmoidal valves regulating the cell-state highway."),
 ],
 ("ch06","transformers-attention"): [
  Q("open",2,["WS24 7.7"],
    "Given $Q,K,V$ of shape $N\\times C$, write the formula of (scaled dot-product) attention.",
    "$\\text{Attention}(Q,K,V)=\\text{softmax}\\!\\Big(\\frac{QK^\\top}{\\sqrt{C}}\\Big)V$. The softmax is taken **over the rows** (each query over all keys), and the scores are divided by $\\sqrt{C}$ (the feature/channel dimension).",
    "Memorize the exact form: $K$ transposed, divide by $\\sqrt{C}$, softmax inside, $V$ outside."),
  Q("open",1,["WS24 7.8"],
    "What is the role of dividing by the channel dimension ($\\sqrt{C}$) in the attention formula?",
    "It **scales down the dot-product scores** (which grow with the dimension $C$) so the softmax input stays in a sensible range → **numerical stability**, avoiding an overly **peaked softmax** and the resulting **small / vanishing gradients**.",
    "Without $1/\\sqrt{C}$, large-$C$ dot products saturate the softmax (near one-hot) and gradients vanish."),
  Q("open",1,["WS24 7.9"],
    "Why does the self-attention mechanism become challenging for extremely long sequences?",
    "It requires a **quadratic amount of memory and compute, $O(n^2)$**, in the sequence length $n$ — every token attends to every other token — so cost blows up for long sequences.",
    "The $n\\times n$ attention matrix is the bottleneck; efficient-attention variants approximate it to scale."),
  Q("open",2,["WS24 7.6"],
    "Multi-head attention with embedding dim 8, 3 heads, $Q/K$ dim 4, $V$ dim 6, weights multiplied from the right ($Y=XW$), output dimension must match the input for the residual. Give the shape of each weight matrix (use $k\\times(n\\times m)$ for per-head weights).",
    "$W_q:\\ 3\\times(8\\times4)$, $W_k:\\ 3\\times(8\\times4)$, $W_v:\\ 3\\times(8\\times6)$, $W_o:\\ (18\\times8)$. Each head projects the 8-dim embedding to its $Q/K$ (4) or $V$ (6); the three heads' value outputs concatenate to $3\\cdot6=18$, then $W_o$ maps $18\\to8$ to restore the residual dimension.",
    "Per-head projections are not shared (hence $3\\times$); the output projection $W_o$ merges concatenated heads back to the model dim."),
  Q("open",1,["WS24 7.10"],
    "In a Transformer for machine translation (predicting the next word, full input+output sentence given), why must we mask the outputs fed into the decoder?",
    "To **mask out future information**: the decoder must predict the next word using only the **already-generated (past) words and the encoder output**. Without masking the model could **'cheat'** by attending to / copying the future ground-truth tokens.",
    "Causal (look-ahead) masking enforces autoregressive, left-to-right decoding so the model can't see the answer."),
 ],
 ("ch07","affine-derivatives"): [
  Q("open",2,["WS24 5.1","WS24 5.2","WS24 5.3"],
    "Backprop worked forward pass. (5.1) Compute $Z=XW+b$ with $X=\\begin{bmatrix}2&-2\\\\0&-4\\\\3&-1\\end{bmatrix}$, $W=\\begin{bmatrix}-2\\\\4\\end{bmatrix}$, $b=1$ (broadcast). (5.2) Apply Leaky ReLU ($0.5x$ if $x<0$) to $Z=[5,-2,0.5]^\\top$. (5.3) Compute $L=\\tfrac12\\sum_{i}(Y_i-\\hat Y_i)^2$ for $Y=[3,-2,1]^\\top,\\ \\hat Y=[2,0,1]^\\top$.",
    "**5.1** $XW=[-12,-16,-10]^\\top$; add broadcast $b=[1,1,1]^\\top$ → $Z=[-11,-15,-9]^\\top$. **5.2** $\\sigma([5,-2,0.5])=[5,\\,-1,\\,0.5]^\\top$ (negative entry $\\times0.5$). **5.3** $L=\\tfrac12\\big[(3-2)^2+(-2-0)^2+(1-1)^2\\big]=\\tfrac12(1+4+0)=2.5$.",
    "Affine → LeakyReLU → squared-error: the standard forward pass before computing gradients."),
  Q("open",2,["WS24 5.4","WS24 5.5","WS24 5.6","WS24 5.7"],
    "Backprop worked gradients (same toy net). (5.4) $\\frac{\\partial L}{\\partial Y}$ for $L=\\tfrac12\\sum(Y-\\hat Y)^2$, $Y=[3,-2,1]^\\top,\\hat Y=[2,0,1]^\\top$. (5.5) $\\frac{\\partial L}{\\partial Z}$ given $\\frac{\\partial L}{\\partial Y}=[-2,-1,1]^\\top$, $Z=[5,-2,0.5]^\\top$ through Leaky ReLU. (5.6) $\\frac{\\partial L}{\\partial W},\\frac{\\partial L}{\\partial X},\\frac{\\partial L}{\\partial b}$ given $\\frac{\\partial L}{\\partial Z}=[1,-1,0]^\\top$, $X,W$ as above. (5.7) What is $\\frac{\\partial L}{\\partial X}$ used for?",
    "**5.4** $\\frac{\\partial L}{\\partial Y}=Y-\\hat Y=[1,-2,0]^\\top$. **5.5** LeakyReLU derivative is $1$ for $z\\ge0$, $0.5$ for $z<0$ → $[1,0.5,1]$; $\\frac{\\partial L}{\\partial Z}=\\frac{\\partial L}{\\partial Y}\\odot[1,0.5,1]=[-2,-0.5,1]^\\top$. **5.6** $\\frac{\\partial L}{\\partial W}=X^\\top\\frac{\\partial L}{\\partial Z}=[2,2]^\\top$; $\\frac{\\partial L}{\\partial X}=\\frac{\\partial L}{\\partial Z}\\,W^\\top=\\begin{bmatrix}-2&4\\\\2&-4\\\\0&0\\end{bmatrix}$; $\\frac{\\partial L}{\\partial b}=\\sum_i\\frac{\\partial L}{\\partial Z_i}=0$. **5.7** It is the **upstream gradient passed to the previous layer** to continue backpropagation.",
    "Note the shapes: $\\partial L/\\partial W$ matches $W$, $\\partial L/\\partial X$ matches $X$; the bias gradient sums the upstream over the batch."),
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
