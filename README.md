

Follow these steps to set up and run the project locally.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/haythemd/news-assignment.git
cd news-assignment
```

## Step 2: Create a Virtual Environment (Optional but Recommended)

# on Linux/MacOS

```bash
python3 -m venv venv
source venv/bin/activate
```
# on Windows 

```bash
python3 -m venv venv
.\venv\Scripts\activate
```
## Step 3: Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Step 4: Launch the Server

```bash
python3 -m uvicorn main:app
```