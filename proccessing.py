import cv2
import numpy as np
from dataclasses import dataclass


@dataclass
class Cell:
    row: int
    col: int
    x: int
    y: int
    width: int
    height: int


def extract_table(image_bytes: bytes) -> list[list[dict]]:
    """
    Détecte les cellules d'un tableau via morphologie mathématique.
    Retourne une grille 2D de cellules triées par (row, col).
    """
    # Décodage + grayscale
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image invalide ou format non supporté.")

    # Binarisation adaptative (robuste aux variations d'éclairage)
    binary = cv2.adaptiveThreshold(
        img, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=15, C=10
    )

    h, w = binary.shape

    # --- Détection des lignes horizontales ---
    h_kernel_len = max(w // 30, 20)
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_len, 1))
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel, iterations=2)

    # --- Détection des lignes verticales ---
    v_kernel_len = max(h // 30, 20)
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_len))
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel, iterations=2)

    # Fusion + dilatation légère pour fermer les gaps
    grid = cv2.add(horizontal, vertical)
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    grid = cv2.dilate(grid, close_kernel, iterations=1)

    # Contours des cellules
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cells: list[Cell] = []
    min_area = (w * h) * 0.0005  # filtre le bruit (< 0.05% de l'image)

    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if cw * ch < min_area:
            continue
        # Exclut le contour global de l'image entière
        if cw > w * 0.95 and ch > h * 0.95:
            continue
        cells.append(Cell(row=0, col=0, x=x, y=y, width=cw, height=ch))

    if not cells:
        return []

    # Tri spatial + attribution row/col par clustering des coordonnées
    cells = _assign_grid_positions(cells)
    return _to_grid(cells)


def _assign_grid_positions(cells: list[Cell]) -> list[Cell]:
    """Groupe les cellules en lignes/colonnes par clustering des centres."""
    tolerance = 10  # px

    def cluster(values: list[int]) -> list[int]:
        """Retourne l'index de cluster pour chaque valeur."""
        sorted_vals = sorted(set(values))
        clusters: list[int] = []
        group = 0
        prev = sorted_vals[0]
        mapping = {prev: 0}
        for v in sorted_vals[1:]:
            if v - prev > tolerance:
                group += 1
            mapping[v] = group
            prev = v
        return [mapping[v] for v in values]

    centers_y = [c.y + c.height // 2 for c in cells]
    centers_x = [c.x + c.width // 2 for c in cells]

    rows = cluster(centers_y)
    cols = cluster(centers_x)

    for i, cell in enumerate(cells):
        cell.row = rows[i]
        cell.col = cols[i]

    return cells


def _to_grid(cells: list[Cell]) -> list[list[dict]]:
    """Convertit la liste de cellules en grille 2D."""
    max_row = max(c.row for c in cells) + 1
    max_col = max(c.col for c in cells) + 1

    grid: list[list[dict | None]] = [[None] * max_col for _ in range(max_row)]
    for cell in cells:
        grid[cell.row][cell.col] = {
            "x": cell.x,
            "y": cell.y,
            "width": cell.width,
            "height": cell.height,
        }

    # Remplace None par dict vide (cellules manquantes)
    return [
        [col if col is not None else {} for col in row]
        for row in grid
    ]