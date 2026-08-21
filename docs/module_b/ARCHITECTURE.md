# Module 3: Battery Health & Thermal Management - System Architecture Specification 📐🧠
### Mathematical Formulation & Neural Network Design of the Dual-Pillar Engine

This document details the exact mathematical formulations, neural network topology, and thermodynamic multi-zone coupling implemented in the Module 3 production engine.

---

## 🏛️ 1. The Cyber-Physical Cloud-Edge Twin Philosophy

Electric Vehicle batteries are complex, non-linear electrochemical systems. Deploying machine learning to real-world automotive fleets requires overcoming two fundamental constraints:
1. **Edge Latency Constraints:** Instantaneous safety threats (e.g., thermal runaway, micro internal short circuits) must be classified in **$<5\,\text{ms}$** on vehicle hardware with deterministic execution.
2. **Extrapolation & Non-Linearity Constraints:** Long-term capacity degradation ($SOH$) is path-dependent and influenced by historical C-rates, ambient temperature cycles, and depth of discharge ($DOD$).

BatteryIQ reconciles this dichotomy via a **Cyber-Physical Cloud-Edge Twin**:

```
                                  CYBER-PHYSICAL SYSTEM
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                                                                             │
    │   PHYSICAL DOMAIN (Vehicle Fleet)            CYBER DOMAIN (AI Twin)         │
    │   ┌─────────────────────────────┐           ┌────────────────────────────┐  │
    │   │ • Lithium-Ion Cells (NMC)   │           │ • SOH Hybrid CNN-LSTM      │  │
    │   │ • Liquid / Air Cooling Loop │ ◄───────► │ • Multi-Zone Random Forest │  │
    │   │ • Drive Motor & Inverter    │  5G Sync  │ • Proactive Digital Twin   │  │
    │   └─────────────────────────────┘           └────────────────────────────┘  │
    │                                                                             │
    └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 2. Pillar 1: Hybrid 1D-CNN + LSTM (Battery Health SOH)

### Mathematical Formulation
Let the input telemetry sequence over window length $L = 10$ time-steps be defined as matrix $\mathbf{X} \in \mathbb{R}^{L \times D}$, where $D = 4$ features $[V, I, T, \text{SoC}]$:

$$\mathbf{X} = \begin{bmatrix} 
V_1 & I_1 & T_1 & \text{SoC}_1 \\
V_2 & I_2 & T_2 & \text{SoC}_2 \\
\vdots & \vdots & \vdots & \vdots \\
V_L & I_L & T_L & \text{SoC}_L
\end{bmatrix}$$

### Branch 1: 1D-Convolutional Spatial Feature Extraction
The 1D-CNN acts as a local feature extractor, scanning across adjacent time-steps to identify sharp voltage drops, sudden discharge current spikes, and thermal derivative shifts:

$$\mathbf{H}_{\text{conv}} = \text{ReLU}\left( \mathbf{W}_{\text{conv}} * \mathbf{X}^\top + \mathbf{b}_{\text{conv}} \right)$$

$$\mathbf{H}_{\text{pool}} = \text{MaxPool1D}\left( \mathbf{H}_{\text{conv}}, \text{kernel}=2 \right)$$

* Filter Channels: $32$ filters, Kernel size $k = 3$, Padding $p = 1$.
* Output Dimension: $\mathbb{R}^{32 \times (L / 2)}$.

### Branch 2: Long Short-Term Memory (LSTM) Temporal Recurrence
The spatial feature maps are fed into a 2-layer stacked LSTM network to model the long-term chemical aging drift across charge cycles:

$$\mathbf{f}_t = \sigma\left( \mathbf{W}_f \mathbf{h}_{\text{pool}, t} + \mathbf{U}_f \mathbf{h}_{t-1} + \mathbf{b}_f \right) \quad \text{(Forget Gate)}$$

$$\mathbf{i}_t = \sigma\left( \mathbf{W}_i \mathbf{h}_{\text{pool}, t} + \mathbf{U}_i \mathbf{h}_{t-1} + \mathbf{b}_i \right) \quad \text{(Input Gate)}$$

$$\tilde{\mathbf{C}}_t = \tanh\left( \mathbf{W}_c \mathbf{h}_{\text{pool}, t} + \mathbf{U}_c \mathbf{h}_{t-1} + \mathbf{b}_c \right) \quad \text{(Candidate Memory)}$$

$$\mathbf{C}_t = \mathbf{f}_t \odot \mathbf{C}_{t-1} + \mathbf{i}_t \odot \tilde{\mathbf{C}}_t \quad \text{(Cell State Update)}$$

$$\mathbf{o}_t = \sigma\left( \mathbf{W}_o \mathbf{h}_{\text{pool}, t} + \mathbf{U}_o \mathbf{h}_{t-1} + \mathbf{b}_o \right) \quad \text{(Output Gate)}$$

$$\mathbf{h}_t = \mathbf{o}_t \odot \tanh\left( \mathbf{C}_t \right) \quad \text{(Hidden State)}$$

* Hidden Dimension: $64$ units per layer, Dropout: $0.20$.

### Branch 3: Dense Regression Head
The final hidden state vector $\mathbf{h}_L \in \mathbb{R}^{64}$ passes through a multi-layer perceptron head to output the predicted capacity percentage:

$$\hat{y}_{\text{SOH}} = \mathbf{W}_2 \cdot \text{ReLU}\left( \mathbf{W}_1 \mathbf{h}_L + \mathbf{b}_1 \right) + b_2$$

---

## 🔥 3. Pillar 2: Multi-Zone Random Forest (Thermal Management)

### The Multi-Zone Coupling Paradigm
Traditional BMS architectures only evaluate battery pack temperature ($T_{\text{batt}}$), creating a critical blind spot during high-torque driving conditions (e.g., hill climbs, severe payload transport). In real-world electric commercial vehicles, **Motor Inverters (`vct`) and Drive Motors (`vmt`) often overheat prior to the battery pack**, inducing severe heat flux into the adjacent battery casing.

```
       [Drive Motor (vmt)] ──Heat Conduction──► [Motor Controller (vct)]
               │                                       │
               └────────► [Battery Pack (vbt)] ◄───────┘
```

### Ensemble Architecture & Gini Impurity
BatteryIQ implements an ensemble of $B = 200$ randomized decision trees:

$$\hat{P}(\text{Critical} \mid \mathbf{x}) = \frac{1}{B} \sum_{b=1}^{B} f_b\left( \mathbf{x} \right)$$

Where each node split $s$ on feature $j$ at threshold $\theta$ minimizes the Gini Impurity:

$$I_G(p) = 1 - \sum_{k=0}^{1} p_k^2$$

$$\Delta I_G = I_G(D) - \left( \frac{|D_L|}{|D|} I_G(D_L) + \frac{|D_R|}{|D|} I_G(D_R) \right)$$

### Verified Gini Feature Importance Breakdown

| Feature Name | Symbol | Mathematical Description | Relative Importance |
| :--- | :---: | :--- | :---: |
| **Battery Temperature** | `vbt` | Core cell pack temperature sensor | **35.0%** |
| **Motor Stator Temperature** | `vmt` | Traction motor coil winding sensor | **22.0%** |
| **Controller Temperature** | `vct` | Power electronics MOSFET / IGBT inverter temp | **18.0%** |
| **Pack Voltage** | `vbv` | Instantaneous total pack voltage | **15.0%** |
| **Vehicle Speed** | `speed` | Ground speed reflecting aerodynamic cooling | **6.0%** |
| **State of Charge** | `soc` | Remaining chemical energy capacity | **4.0%** |

---

## ⚖️ 4. Overcoming the "Accuracy Paradox" via 50/50 Balanced Downsampling

In real commercial fleets, $<2\%$ of operational seconds represent dangerous thermal anomalies. A naive classifier predicting "All Safe" achieves $98\%$ raw accuracy while failing to catch $100\%$ of catastrophic fires.

BatteryIQ solves this by isolating the $5,157$ true critical alert instances and pairing them with an equal sample of $5,157$ benign alerts:

$$\text{Class Distribution} = \begin{cases} 
\text{Critical Faults} (y=1): & 5,157 \text{ records } (50.0\%) \\
\text{Benign Events} (y=0): & 5,157 \text{ records } (50.0\%) 
\end{cases}$$

This forces the decision trees to learn the precise non-linear thermodynamic boundary separating normal driving from irreversible thermal runaway.
