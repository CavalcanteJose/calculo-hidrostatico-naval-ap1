
<p align="center">
  <img src="https://github.com/Meet2147/streamlit-preview/raw/HEAD/media/128_1.png" alt="Streamlit Preview" height="60">
</p>

<p align="center">
  <b>Preview Streamlit apps directly inside VS Code.</b><br/>
  No more context switching between editor and browser.
</p>

<p align="center">
  <img src="https://img.shields.io/visual-studio-marketplace/v/mjethwa-streamlit.streamlit-preview?label=Version&style=for-the-badge">
  <img src="https://img.shields.io/visual-studio-marketplace/i/mjethwa-streamlit.streamlit-preview?label=Installs&style=for-the-badge">
  <img src="https://img.shields.io/visual-studio-marketplace/r/mjethwa-streamlit.streamlit-preview?label=Rating&style=for-the-badge">
</p>

---

# ✨ Streamlit Preview (VS Code)

**Streamlit Preview** lets you open and preview your Streamlit application **inside a VS Code tab**, similar to an embedded browser.

Stop switching between your editor and browser — stay focused in one window.

---

# 🚀 Features (Free)

### 🔁 One-click Preview
Run your current `app.py` (or any Streamlit script) and open it instantly in VS Code.

### 🔄 Auto Hot-Reload
Write → Save → Instantly see updates via Streamlit’s built-in reload.

### 🧭 Port 8501 (Default)
Automatically waits for the Streamlit server to start — fewer errors, smoother workflow.

### 🪟 Clean UI Layout
Side panel for app URL & controls, main panel displays the Streamlit UI.

---

# 🧪 Streamlit Preview **Pro** (Coming Soon)

Unlock premium features designed for professional workflows:

### ⚙️ Choose Python Environment
Run Streamlit using any virtual environment or Conda environment.

### 🔌 Custom Ports & Auto-Retry
Run multiple Streamlit previews in parallel (8501, 8502, 8503…).

### 📌 Workspace Profiles
Automatically remember:
- Script path
- Environment
- Port
- Auto-start settings

### 📜 Built-In Log Panel
View Streamlit stdout & stderr logs in a dedicated VS Code panel.

### 🌍 Share via Tunnel
One-click sharing using:
- `ngrok`
- `cloudflared`

> **Streamlit Preview Pro** will be a *one-time purchase* activated via a license key.

---

# 🧰 Requirements

- **Python 3.x** in PATH
  - Windows → `python`
  - macOS/Linux → `python3`
- Install Streamlit:

```bash
pip install streamlit
````

-----

# 📦 Installation

## From Marketplace

1.  Open VS Code
2.  Go to Extensions
3.  Search for: Streamlit Preview
4.  Click Install

## Or install via VSIX

```bash
code --install-extension streamlit-preview.vsix
```

-----

# 🛠 Usage

### ▶️ 1. Open Your Streamlit Script

Open `app.py` or any file that runs Streamlit.

### ▶️ 2. Start Preview

**Command Palette** →

`Streamlit: Preview Current File`

### ▶️ 3. Edit & Save

Every save triggers a reload. **No restart required.**

### ⏹ 4. Stop Preview

`Streamlit: Stop Preview`

-----

# ⚙️ Settings

| Setting | Description |
| :--- | :--- |
| `streamlitPreview.port` | Default Streamlit port (8501) |
| `streamlitPreview.autoStart` | Auto-start preview when opening a Streamlit file |
| `streamlitPreview.openInSidePanel` | Open preview inside sidebar panel |

-----

# 🖼 Screenshots

### 📌 Streamlit Preview inside VS Code

<p align="center">
  <img src="https://github.com/Meet2147/streamlit-preview/raw/HEAD/media/S3.png" width="80%">
</p>

-----

# 🧩 Commands

| Command | Description |
| :--- | :--- |
| `Streamlit: Preview Current File` | Run & preview Streamlit inside VS Code |
| `Streamlit: Stop Preview` | Stop the running Streamlit server |
| `Streamlit: Open Logs (Pro)` | View Streamlit logs |
| `Streamlit: Configure Profile (Pro)` | Set environment, port, and workspace settings |

-----

# 🧰 Contributing

Contributions are welcome\!
File issues, bugs, or feature requests here:

👉 **GitHub Issues:**
[https://github.com//streamlit-preview/issues](https://github.com/Meet2147/streamlit-preview/issues)

-----

# ⭐ Feedback & Reviews

If you enjoy this extension, please consider leaving a ⭐⭐⭐⭐⭐ review\!

👉 **Marketplace:**
[https://marketplace.visualstudio.com/items?itemName=mjethwa-streamlit.streamlit-preview](https://marketplace.visualstudio.com/items?itemName=mjethwa-streamlit.streamlit-preview)

-----

# 🔐 Licensing (Pro Version Workflow)

Here is how licensing will work when you launch Streamlit Preview Pro:

### 1️⃣ User Purchases a License

Sold via:

  * LemonSqueezy
  * Gumroad
  * Stripe
  * Paddle

### 2️⃣ License Key is Generated

Example:
`SLP-ABCD-1234-WXYZ`

### 3️⃣ User Enters License in VS Code

New command:
`Streamlit: Activate License`

### 4️⃣ Extension Sends License to Your Backend

Your server returns:

```json
{
  "valid": true,
  "plan": "pro",
  "email": "user@example.com"
}
```

### 5️⃣ Pro Unlocks Instantly

You store activation in:
`context.globalState`

### 6️⃣ Auto Revalidation

Every \~7 days the license is rechecked.

If license becomes invalid → Pro features lock again.

-----

# 📜 License

  * Free version → MIT License
  * Pro version → Commercial license (one-time purchase)

-----

# ✅ Next Steps

Just tell me:

👉 “Let’s update `package.json`”

or

👉 “Let’s implement the licensing system”

or

👉 “Let’s work on the Pro features UI”

I’m ready to continue\!

-----

If you'd like, I can also:

  * Generate marketplace screenshots
  * Write your `CHANGELOG.md`
  * Add badges for Python, Streamlit, license, repo size
  * Create a beautiful cover banner for the extension page

Just say **“Make the graphics”** or **“Generate screenshots mockups”**.

```

What part of the development process would you like to focus on next?
```