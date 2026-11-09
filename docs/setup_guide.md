# Windows setup guide

1. Open this folder in Visual Studio Code.
2. Open **Terminal > New Terminal**.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Activate it:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the Command Prompt activation script:
   `.venv\Scripts\activate.bat`.

5. Install the listed dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Copy values from `.env.example` into `.env` only when you are ready to
   configure approved Azure credentials. Keep secrets local.
7. Start the scaffold:

   ```powershell
   streamlit run app.py
   ```

The current app intentionally shows placeholders and does not call Azure yet.
