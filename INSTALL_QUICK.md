# ⚡ Fast Installation Guide (New Laptop)

Follow these steps to get the **AutoRoads AI Assistant** and **OpenROAD** running on your new laptop in minimum time.

---

## 🏎️ Step 1: Clone the Project
Open a terminal (PowerShell or Bash) and run:
```bash
git clone https://github.com/RishitTandon7/AutoRoads.git
cd AutoRoads
```

---

## 🐧 Step 2: Install OpenROAD (via WSL)
Open PowerShell as Administrator and run:
```powershell
wsl --install -d Ubuntu
```
After Ubuntu installs and you set your username, run this **one-liner** inside the Ubuntu terminal to install OpenROAD dependencies:
```bash
sudo apt-get update && sudo apt-get install -y openroad xterm
```
*(Note: If the `openroad` package isn't in your default apt, you can download the fast precision-binary from the [OpenROAD Precision Releases](https://github.com/The-OpenROAD-Project/OpenROAD/releases)).*

---

## 🐍 Step 3: Run the AI Assistant
Back in your **Windows** terminal (inside the `AutoRoads` folder), just run:
```powershell
python run.py
```
**Why this is fast:**
- My `run.py` script has an **Auto-Dependency Manager**. 
- It will automatically detect missing libraries (FastAPI, Uvicorn, etc.) and pip-install them for you on the first run.
- You don't need to manually install things from `requirements.txt`.

---

## 🖥️ Step 4: Setup the GUI (X-Server)
To see the chip layouts (the "Visual Flows"), you need an X-Server on Windows:
1. Download and install [**VcXsrv**](https://sourceforge.net/projects/vcxsrv/).
2. Run **XLaunch** with these settings:
   - `Multiple windows`
   - `Start no client`
   - **Crucial:** Check `Disable access control`.
3. In your WSL terminal, add this to your `~/.bashrc`:
   ```bash
   export DISPLAY=:0
   ```

---

## ✅ Step 5: Verify
Once `run.py` is running:
1. Open `http://localhost:8000` in your browser.
2. Ask the AI: *"Run the MPW Shuttle floorplan"* or just run `bash designs/gcd/run_mpw.sh` in WSL.

---

> [!TIP]
> **Minimum Time Shortcut:** 
> If you already have your `/home/rishit/OpenROAD/test` folder on your old laptop, zip it and move it to the same path on the new laptop. This keeps all your PDKs and synthesis results ready!
