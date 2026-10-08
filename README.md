# SUBURBIOUS: Grid-Based Strategy Board Game (Python)

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📄 Overview
An interactive, turn-based CLI grid strategy game implemented in **Python**. Inspired by city-building puzzle mechanics (similar to *Triple Town*), players place entities on a $6 \times 6$ board to form connected groups that trigger structural evolution (collapses), while managing roaming entities (*Bigfoots*) and spatial constraints.

## ⚙️ Core Game Mechanics & Algorithms

- **Recursive Connected-Component Finding (Flood Fill):** Implements recursive graph/grid traversal algorithms (`grupo` and `region`) to identify matching adjacent entities and enclosed spatial regions[cite: 11].
- **Chain Collapses:** When 3 or more identical structures form an adjacent group, they collapse into a single higher-tier building (e.g., *Store $\rightarrow$ House $\rightarrow$ Mansion $\rightarrow$ Building $\rightarrow$ Hospital*)[cite: 11].
- **Entity State Machine & AI Movement:** Roaming *Bigfoots* age dynamically per turn, leave debris based on threshold age, move toward vacant neighboring cells, and transition to *Babies* when fully enclosed by surrounding structures[cite: 11].
- **Score & Inventory System:** Tracks total board score dynamically and includes an inventory/warehouse cell for strategic element swapping[cite: 11].

## 📁 Project Structure
```text
.
├── src/
│   └── main.py       # Main game engine and CLI interface
└── README.md
```

## 🚀 How to Run

### Prerequisites
- Python 3.8 or higher installed.

### Execution
Run the game directly using Python:
```bash
python src/main.py
```

1. Option to load a predefined board setup file or generate a random initial board[cite: 11].
2. Enter target coordinates (e.g., `A1`, `C4`) to place the current element[cite: 11].
3. Use `*` to store/swap the current element with the warehouse[cite: 11].

## 👥 Authors
- **Javier Vaca Sánchez** ([@javivsr](https://github.com/javivsr))[cite: 11]
- **Enrique Quiñones Ureta**[cite: 11]