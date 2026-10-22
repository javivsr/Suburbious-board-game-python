# SUBURBIOUS: Grid-Based Strategy Board Game (Python)

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📄 Overview
An interactive, turn-based grid strategy game implemented in **Python**, with a command-line version and a **graphical version built with wxPython**. Inspired by city-building puzzle mechanics (similar to *Triple Town*), players place entities on a $6 \times 6$ board to form connected groups that trigger structural evolution (collapses), while managing roaming entities (*Bigfoots*) and spatial constraints.

## ⚙️ Core Game Mechanics & Algorithms

- **Recursive Connected-Component Finding (Flood Fill):** Implements recursive graph/grid traversal algorithms (`grupo` and `region`) to identify matching adjacent entities and enclosed spatial regions.
- **Chain Collapses:** When 3 or more identical structures form an adjacent group, they collapse into a single higher-tier building (e.g., *Store $\rightarrow$ House $\rightarrow$ Mansion $\rightarrow$ Building $\rightarrow$ Hospital*).
- **Entity State Machine & AI Movement:** Roaming *Bigfoots* age dynamically per turn, leave debris based on threshold age, move toward vacant neighboring cells, and transition to *Babies* when fully enclosed by surrounding structures.
- **Score & Inventory System:** Tracks total board score dynamically and includes an inventory/warehouse cell for strategic element swapping.

## 🖥️ Graphical Version (wxPython)

- Event-driven GUI with a turn timer, animations for collapses and Bigfoot movements, and sound effects.
- The game engine exposes callbacks so the interface can animate each move.
- Includes a random-move option (`jugar_azar`) that picks a valid move automatically.

## 📁 Project Structure
```text
.
├── src/
│   ├── main.py       # Command-line version: game engine and CLI interface
│   └── gui/
│       ├── engine.py # Game engine adapted for the GUI (callbacks, board size, random moves)
│       └── gui.py    # wxPython graphical interface
└── README.md
```

## 🚀 How to Run

### Prerequisites
- Python 3.8 or higher installed.

### Command-line version
```bash
python src/main.py
```

1. Option to load a predefined board setup file or generate a random initial board.
2. Enter target coordinates (e.g., `A1`, `C4`) to place the current element.
3. Use `*` to store/swap the current element with the warehouse.

### Graphical version
```bash
pip install wxPython
cd src/gui
python gui.py
```

> **Note:** the image and sound assets used by the GUI are not included yet. They will be added in a future update using openly licensed (CC0) assets. Until then, the graphical version will not start.

## 🙏 Acknowledgements
The game engine is based on the reference solution provided by the course instructor and is published with their permission. The modifications are described at the top of `src/gui/engine.py`.

## 👥 Authors
- **Javier Vaca Sánchez** ([@javivsr](https://github.com/javivsr))
- **Enrique Quiñones Ureta** ([@enrquin](https://github.com/enrquin))
