# Project Overview

Welcome to the GitHub repository for my LLM Chess Project for my Capstone Graduation Project.

## 1. The Data Loader

- **File:** `data_loader.py`
- **Description:** This script is responsible for creating the initial datasets. It processes lichess PGN files compressed with Zstandard (`.zst`) to generate a foundational dataset for further analysis and training.

## 2. Data Updating

- **File:** `data_with_ranking.py`
- **Description:** This module updates a JSON Lines (`.jsonl`) file. Its main function is to re-sort legal chess moves based on their effectiveness, as determined by a powerful chess engine. This re-sorting enhances the accuracy and relevancy of our data for predicting human moves.

## 3. Training a QLoRA

- **Notebook:** `mistral-finetune-chess.ipynb`
- **Features:** 
  - Training and loading model checkpoints.
  - A game loop that allows users to play against the trained model.
  - 
---

This project is an ongoing effort, and I plan on continuing it for the foreseeable future.

---
