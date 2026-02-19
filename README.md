# 🛡️ LLM Guardian V2

A 3-phase hybrid AI firewall that detects jailbreak and prompt injection attacks.

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run demo.py
```

## 🌐 Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `demo.py`
5. Click **Deploy**

## 🏗️ Architecture

| Phase | Method | Weight |
|-------|--------|--------|
| 1 | Regex Rules (25 patterns) | 25% |
| 2 | Semantic DB — ChromaDB + all-MiniLM-L6-v2 (70+ fingerprints) | 35% |
| 3 | TF-IDF + Logistic Regression (546 samples, 84.5% accuracy) | 40% |

**Formula:** `Risk = 0.25×P1 + 0.35×P2 + 0.40×P3`

- 🚨 **BLOCK** → Risk > 70%
- ⚠️ **REVIEW** → Risk 30–70% (soft block)
- ✅ **ALLOW** → Risk < 30%

## 📁 Files

```
demo.py              ← Streamlit UI
detector.py          ← Hybrid 3-phase engine
preprocessor.py      ← Token smuggling / Base64 / homoglyph normalizer
phase1_rules.py      ← Regex engine
phase2_semantic.py   ← ChromaDB semantic engine
rules.json           ← 25 attack patterns
attacks.txt          ← 70+ jailbreak fingerprints
jailbreak_data.csv   ← 546 training samples
requirements.txt     ← Dependencies
```
