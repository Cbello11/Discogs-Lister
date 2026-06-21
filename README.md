# Discogs Lister

Automated listing tool for records and other music media on Discogs marketplace.
Browser-based GUI — no coding required to use.

## Features

- **Search** the Discogs database by artist, title, label, or barcode
- **Auto-filled listing form** with release data pulled from Discogs
- **Price Intelligence** — shows Low / Median / High marketplace prices with one-click "Use Median"
- **Condition grading** with built-in Discogs grading guide (press `G` to open)
- **Drag-and-drop photo uploads** (up to 3 images per listing)
- **Draft saving** with autosave every 30 seconds
- **Bulk Queue** — add multiple items, submit them all at once
- **History log** with CSV export
- Supports Vinyl, CD, Cassette, DVD, Blu-ray, Box Set, and all Discogs formats

## Quick Start

### 1. Install

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Get Discogs Credentials

Go to **https://www.discogs.com/settings/developers**

**Easiest option — Personal Access Token:**
- Scroll to "Personal Access Token" and generate one
- Paste it in the app when you log in (no `.env` edit needed)

**Full OAuth (optional):**
- Create a new app to get a Consumer Key & Secret
- Add them to your `.env` file

### 3. Run

```bash
python run.py
```

The app opens automatically at **http://127.0.0.1:5000**

## How to List a Record

1. **Search** for the release (artist name, album title, barcode)
2. Click **"List This"** on the correct version
3. Select **Media Condition** and **Sleeve Condition**
4. Review the **Price Intelligence** panel — click "Use Median" or enter your price
5. Add your **location**, notes, and photos
6. Click **"List Now"** — done!

## Bulk Listing

- Save drafts for multiple records using "Save Draft"
- Go to **Bulk Queue** to review and submit them all at once

## Project Structure

```
app/
  auth/        OAuth + personal token login
  search/      Release search
  listing/     Listing form, drafts, bulk queue
  history/     Listing history + CSV export
  api/         Internal JSON API for the frontend
  discogs/     Discogs API wrapper, pricing, image upload
  templates/   HTML templates (Bootstrap 5)
  static/      CSS + JavaScript
run.py         Start the app
```
