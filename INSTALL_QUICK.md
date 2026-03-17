# ⚡ Fast Installation Guide (New Laptop)

Follow these steps to get the **AutoRoads AI Assistant** and **OpenROAD** running on your new laptop in minimum time.

---

## 🛠️ Step 0: Install Tools (If Missing)
If you don't have **Git** or **Python** yet, open PowerShell as Admin and run this one-liner:
```powershell
winget install -e --id Git.Git Python.Python.3.12
```
*Restart your terminal after this step.*

---

## 🏎️ Step 1: Clone the Project
If you have Git:
```bash
git clone https://github.com/RishitTandon7/AutoRoads.git
cd AutoRoads
```
**If you don't want Git**: 
Go to [github.com/RishitTandon7/AutoRoads](https://github.com/RishitTandon7/AutoRoads), click the green **Code** button, and select **Download ZIP**. Unzip it on your desktop.

---

## 🐧 Step 2: Install OpenROAD (via WSL)
Open PowerShell as Administrator and run:
```powershell
wsl --install -d Ubuntu
```
After Ubuntu installs, run this in the Ubuntu terminal:
```bash
sudo apt-get update && sudo apt-get install -y openroad
```

---

## 🐍 Step 3: Run the AI Assistant
Inside the `AutoRoads` folder on Windows, just double-click:
**`start_autoroads.bat`**

*This will automatically launch the X-Server, install Python libraries, and open the web UI.*

---

## 🖥️ Step 4: Setup the GUI (X-Server)
1. Install [**VcXsrv**](https://sourceforge.net/projects/vcxsrv/).
2. Run **XLaunch** with `Disable access control` checked.
3. In WSL terminal: `export DISPLAY=:0`
