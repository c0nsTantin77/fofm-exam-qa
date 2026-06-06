#!/usr/bin/env python3
"""Patch: add the missing `options` to the coverage-pass MC questions
(keyed by their first source). Sets options only when the question is type
'mc' and currently has no options."""
import glob, json, pathlib, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
ROOT = pathlib.Path(__file__).resolve().parent.parent

def O(*pairs): return [{"text": t, "correct": c} for t, c in pairs]

OPTS = {
 "WS23 1.6": O(("$f(x) = 2\\sigma(x) - 1$ (sigmoid).", True),
              ("$f(x) = \\tanh(10x)$", True),
              ("$f(x) = \\max(-1, x)$", False),
              ("$f(x) = \\min(\\max(-1, x), 1)$ (clamp)", True)),
 "WS23 1.8": O(("$N$ (input spatial size)", True), ("$k$ (kernel size)", True),
              ("$m$ (number of filters)", True), ("$C$ (number of input channels)", False)),
 "SS25 1.6": O(("Low-level features are extracted in deeper layers.", False),
              ("Both kernel size and padding affect the number of learnable parameters.", False),
              ("Convolutional layers are translation equivariant.", True),
              ("Convolutional layers are rotation invariant.", False)),
 "WS23 1.1": O(("It does not have any learnable parameters.", True),
              ("It always performs better than Max Pooling, since it ignores no features.", False),
              ("It reduces the spatial dimensions of the input.", True),
              ("It reduces the channel dimension of the input.", False)),
 "SS25 1.1": O(("Decrease the learning rate", True), ("Increase the learning rate", False),
              ("Decrease the batch size", False), ("Try other optimizers", True)),
 "SS25 1.5": O(("Dropout", False), ("Batch Normalization", True),
              ("Weight Decay", False), ("Weight Initialization", False)),
 "SS25 1.4": O(("Batch normalization reduces the impact of poor weight initialization.", True),
              ("Kaiming initialization considers both input and output layer sizes.", False),
              ("Xavier initialization doesn't work well with ReLU activations.", True),
              ("Kaiming initialization considers the size of the input layer only.", True)),
 "SS25 1.8": O(("Adding skip connections.", False), ("Using ReLU as activation functions.", True),
              ("Introducing convolutional layers.", False),
              ("Increasing depth and number of parameters.", True)),
 "WS23 1.4": O(("The hidden layer should ideally be larger than the input layer.", False),
              ("The encoder and decoder have the same number of layers.", False),
              ("Any autoencoder can perfectly learn the identity function.", False),
              ("An autoencoder can be used as a lossy compressor.", True)),
 "WS23 1.5": O(("A convolution then a transposed convolution with identical weights is an identity operation.", False),
              ("Transposed convolution adds trainable parameters, whereas interpolation does not.", True),
              ("Transposed convolution is equivalent to unpooling followed by a standard convolution.", True),
              ("Transposed convolution equals bilinear interpolation followed by a standard convolution.", False)),
 "WS23 1.7": O(("The generator maximizes the probability its output is classified 'real' by the discriminator.", True),
              ("The discriminator learns the distribution of input images, but the generator does not.", False),
              ("After training, the discriminator loss tends to a constant value.", True),
              ("A fully trained discriminator can be used as a sampling mechanism.", False)),
 "SS25 1.2": O(("During training, RNNs suffer from vanishing gradients, but not exploding gradients.", False),
              ("The output of an RNN at each timestep depends only on the current input.", False),
              ("RNNs inherently model sequence order through recurrence, so they need no positional encoding.", True),
              ("RNNs maintain a hidden state updated each timestep to capture temporal dependencies.", True)),
 "SS25 1.3": O(("To limit the number of parameters in the model.", False),
              ("To allow the network to forget or retain information over long sequences.", True),
              ("To progressively reduce the dimensionality of the hidden state over time.", False),
              ("To ensure the output always depends only on the most recent input token.", False)),
 "WS23 1.3": O(("The attention mechanism itself is invariant to order.", True),
              ("The concept of a transformer can only be applied to text data.", False),
              ("Transformers utilize convolutional layers to gather context information.", False),
              ("Due to masked attention, the decoder output depends only on previous outputs and the encoder.", True)),
}

def main():
    patched = 0
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        p = pathlib.Path(f)
        if p.name == "chapters.json":
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        changed = False
        for kp in data["knowledge_points"]:
            for q in kp["questions"]:
                key = q["sources"][0] if q["sources"] else ""
                if q["type"] == "mc" and "options" not in q and key in OPTS:
                    q["options"] = OPTS[key]
                    patched += 1
                    changed = True
        if changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"patched {p.name}")
    print(f"patched {patched} MC questions")

if __name__ == "__main__":
    main()
